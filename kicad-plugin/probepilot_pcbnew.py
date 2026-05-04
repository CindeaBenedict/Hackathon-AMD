# -*- coding: utf-8 -*-
"""
ProbePilot — KiCad pcbnew ActionPlugin
======================================
Copy this file into your KiCad scripting plugins folder, then restart KiCad.

Windows (typical KiCad 8):
  %USERPROFILE%\\Documents\\KiCad\\8.0\\scripting\\plugins\\
Linux:
  ~/.local/share/kicad/8.0/scripting/plugins/

Environment:
  PROBEPILOT_API_URL   Base URL for ProbePilot FastAPI (default: http://127.0.0.1:8000)

The standalone ProbePilot app (or bench stack) should have `uvicorn` running so
`/api/kicad/analyze` accepts the JSON snapshot exported from the active board.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import pcbnew


def _api_base() -> str:
    return os.environ.get("PROBEPILOT_API_URL", "http://127.0.0.1:8000").rstrip("/")


def _fp_reference(fp) -> str:
    if hasattr(fp, "GetReferenceAsString"):
        return fp.GetReferenceAsString()
    return fp.GetReference()


def _fp_lib_id(fp) -> str:
    if hasattr(fp, "GetFPIDAsString"):
        return fp.GetFPIDAsString()
    return str(fp.GetFPID())


def _iter_footprints(board):
    if hasattr(board, "Footprints"):
        try:
            return list(board.Footprints())
        except Exception:
            pass
    if hasattr(board, "GetFootprints"):
        return list(board.GetFootprints())
    return list(board.GetModules())


def _pad_net_name(pad) -> str:
    try:
        n = pad.GetNetname()
        if n:
            return str(n)
    except Exception:
        pass
    try:
        net = pad.GetNet()
        if net and hasattr(net, "GetNetname"):
            return str(net.GetNetname() or "")
    except Exception:
        pass
    return ""


def _iter_pads(fp):
    if hasattr(fp, "Pads"):
        try:
            return list(fp.Pads())
        except Exception:
            pass
    if hasattr(fp, "PadsList"):
        return list(fp.PadsList())
    return []


def _collect_snapshot(board) -> dict:
    footprints: list[dict] = []
    nets: set[str] = set()
    for fp in _iter_footprints(board):
        pads_out: list[dict] = []
        for i, pad in enumerate(_iter_pads(fp)):
            net = _pad_net_name(pad)
            if net:
                nets.add(net)
            pname = ""
            try:
                pname = str(pad.GetName() if hasattr(pad, "GetName") else pad.GetPadName())
            except Exception:
                pname = ""
            pads_out.append({"pad_index": i, "pad_name": pname, "net": net})
        footprints.append(
            {
                "reference": _fp_reference(fp),
                "value": fp.GetValue(),
                "footprint_id": _fp_lib_id(fp),
                "pads": pads_out,
            },
        )
    board_path = ""
    try:
        board_path = str(board.GetFileName())
    except Exception:
        board_path = ""
    ver = ""
    for attr in ("GetBuildVersion", "GetKiCadVersion"):
        fn = getattr(pcbnew, attr, None)
        if callable(fn):
            try:
                ver = str(fn())
                break
            except Exception:
                continue
    return {
        "kicad_version": ver,
        "source": "pcbnew",
        "board_path": board_path,
        "footprints": footprints,
        "nets": sorted(nets),
    }


def _post_analyze(payload: dict) -> dict:
    url = _api_base() + "/api/kicad/analyze"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


class ProbePilotPcbnewPlugin(pcbnew.ActionPlugin):
    def defaults(self) -> None:
        self.name = "ProbePilot"
        self.category = "ProbePilot"
        self.description = "Send board snapshot to ProbePilot for checks + agent analysis."
        self.show_toolbar_button = True

    def Run(self) -> None:
        import wx

        board = pcbnew.GetBoard()
        if board is None:
            wx.MessageBox("No active board.", "ProbePilot", wx.OK | wx.ICON_WARNING)
            return

        design = _collect_snapshot(board)
        body = {
            "design": design,
            "user_message": "KiCad pcbnew export: review for obvious issues and suggest next checks.",
        }

        try:
            result = _post_analyze(body)
        except urllib.error.HTTPError as e:
            wx.MessageBox(f"HTTP {e.code}: {e.reason}", "ProbePilot", wx.OK | wx.ICON_ERROR)
            return
        except urllib.error.URLError as e:
            wx.MessageBox(
                f"Could not reach ProbePilot API at {_api_base()}\n\n{e.reason}\n\n"
                "Start the backend (uvicorn) or set PROBEPILOT_API_URL.",
                "ProbePilot",
                wx.OK | wx.ICON_ERROR,
            )
            return
        except Exception as e:  # noqa: BLE001 — plugin UX
            wx.MessageBox(str(e), "ProbePilot", wx.OK | wx.ICON_ERROR)
            return

        checks = result.get("checks") or []
        stats = result.get("stats") or {}
        agent = result.get("agent") or {}
        reply = agent.get("reply") or "(no agent reply)"
        summary = (
            f"Footprints: {stats.get('footprint_count', '?')} | Nets: {stats.get('net_count', '?')}\n"
            f"Checks: {len(checks)}\n\n"
            f"{reply[:900]}"
        )
        wx.MessageBox(summary, "ProbePilot", wx.OK | wx.ICON_INFORMATION)


ProbePilotPcbnewPlugin().register()
