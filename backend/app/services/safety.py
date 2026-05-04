"""Hardware command safety gate — blocks execution until rules pass."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.tools import (
    AbortTool,
    AgentToolCall,
    MultimeterVoltageTool,
    OscilloscopeCaptureTool,
    SwitchMatrixConnectTool,
)


@dataclass
class SafetyResult:
    allowed: bool
    requires_human_confirmation: bool
    message: str


def _parse_volts(s: str | None) -> float | None:
    if not s:
        return None
    m = re.search(r"([\d.]+)\s*V", s, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"([\d.]+)", s)
    if m:
        return float(m.group(1))
    return None


def validate_tool_call(cmd: AgentToolCall, settings_max_v: float = 60.0) -> SafetyResult:
    if isinstance(cmd, AbortTool):
        return SafetyResult(True, False, "Abort acknowledged.")

    if isinstance(cmd, MultimeterVoltageTool):
        mx = None
        if cmd.safety and cmd.safety.max_expected_voltage:
            mx = _parse_volts(cmd.safety.max_expected_voltage)
        er = _parse_volts(cmd.expected_range.split("-")[1]) if cmd.expected_range and "-" in cmd.expected_range else None
        peak = max([v for v in (mx, er) if v is not None], default=None)
        if peak and peak > settings_max_v:
            return SafetyResult(False, True, f"Voltage {peak}V exceeds policy {settings_max_v}V.")
        pos = cmd.target.get("positive_probe", "")
        neg = cmd.target.get("negative_probe", "")
        if pos and neg and pos.upper() == neg.upper():
            return SafetyResult(False, False, "Positive and negative probes must differ.")
        if cmd.safety and cmd.safety.safe is False:
            return SafetyResult(False, True, cmd.safety.reason or "Tool marked unsafe.")
        return SafetyResult(True, False, "Multimeter DC voltage check passed policy.")

    if isinstance(cmd, OscilloscopeCaptureTool):
        return SafetyResult(True, False, "Oscilloscope capture allowed pending bench limits.")

    if isinstance(cmd, SwitchMatrixConnectTool):
        if cmd.safety and cmd.safety.safe is False:
            return SafetyResult(False, True, cmd.safety.reason or "Relay path unsafe.")
        # naive short check: same net to supply rail patterns
        risky = ("VCC", "VIN", "VBAT", "12V", "5V")
        if cmd.positive.upper() in risky and cmd.negative.upper() == "GND":
            return SafetyResult(False, True, "Matrix path may short rail to ground — require human confirmation.")
        return SafetyResult(True, False, "Switch matrix route passed static checks.")

    return SafetyResult(True, False, "No extra safety rules.")
