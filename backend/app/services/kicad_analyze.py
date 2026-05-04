from __future__ import annotations

from collections import Counter
from typing import Any

from app.schemas.kicad_payload import KiCadDesignPayload, KiCadFootprint
from app.services.agent import ProbePilotAgent, state_to_json


def _check_duplicate_refs(footprints: list[KiCadFootprint]) -> list[dict[str, Any]]:
    refs = [f.reference for f in footprints if f.reference]
    counts = Counter(refs)
    issues: list[dict[str, Any]] = []
    for ref, n in counts.items():
        if n > 1:
            issues.append(
                {
                    "id": "duplicate_reference",
                    "severity": "error",
                    "detail": f"Reference {ref!r} appears {n} times.",
                },
            )
    return issues


def _check_missing_values(footprints: list[KiCadFootprint]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for fp in footprints:
        if not (fp.value or "").strip():
            issues.append(
                {
                    "id": "empty_value",
                    "severity": "warning",
                    "detail": f"{fp.reference}: empty value field.",
                },
            )
        if not (fp.footprint_id or "").strip():
            issues.append(
                {
                    "id": "empty_footprint",
                    "severity": "warning",
                    "detail": f"{fp.reference}: missing footprint assignment.",
                },
            )
    return issues


def _check_power_nets(nets: list[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    upper = [n.upper() for n in nets]
    has_gnd = any("GND" in n or n == "0" for n in upper)
    has_pwr = any(any(x in n for x in ("VCC", "VDD", "+3V3", "+5V", "VBAT")) for n in upper)
    if has_pwr and not has_gnd:
        issues.append(
            {
                "id": "power_without_gnd",
                "severity": "warning",
                "detail": "Power-like nets found but no obvious GND net name — verify ground return.",
            },
        )
    return issues


def analyze_kicad_design(
    payload: KiCadDesignPayload,
    agent: ProbePilotAgent,
    user_message: str | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.extend(_check_duplicate_refs(payload.footprints))
    checks.extend(_check_missing_values(payload.footprints))
    checks.extend(_check_power_nets(payload.nets))

    lines = [
        "[KiCad design snapshot]",
        f"source={payload.source} kicad={payload.kicad_version or 'unknown'} board={payload.board_path or 'unsaved'}",
        f"footprints={len(payload.footprints)} nets={len(payload.nets)}",
    ]
    if checks:
        lines.append("static_checks:")
        for c in checks[:12]:
            lines.append(f"- [{c['severity']}] {c['id']}: {c['detail']}")
        if len(checks) > 12:
            lines.append(f"... and {len(checks) - 12} more")
    else:
        lines.append("static_checks: none detected (heuristic pass)")

    # Pull a few values for RAG context keywords
    values = " ".join({fp.value for fp in payload.footprints if fp.value})[:400]
    if values:
        lines.append(f"sample_values: {values}")

    composed = "\n".join(lines)
    goal = user_message or "Review this KiCad export for obvious design issues and suggest next checks."
    state = agent.run_turn(f"{composed}\n\n{goal}", {})
    return {
        "checks": checks,
        "stats": {
            "footprint_count": len(payload.footprints),
            "net_count": len(payload.nets),
        },
        "agent": state_to_json(state),
    }
