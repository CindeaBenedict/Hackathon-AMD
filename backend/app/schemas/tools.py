from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SafetyBlock(BaseModel):
    max_expected_voltage: str | None = None
    max_expected_current: str | None = None
    safe: bool = False
    reason: str | None = None


class MultimeterVoltageTool(BaseModel):
    tool: Literal["multimeter.measure_voltage"] = "multimeter.measure_voltage"
    target: dict[str, str]
    mode: Literal["DC", "AC"] = "DC"
    expected_range: str | None = None
    safety: SafetyBlock | None = None
    reason: str = ""


class OscilloscopeCaptureTool(BaseModel):
    tool: Literal["oscilloscope.capture"] = "oscilloscope.capture"
    channel: int = Field(ge=1, le=8)
    probe_node: str
    reference: str = "GND"
    timebase: str = "1ms/div"
    voltage_scale: str = "1V/div"
    trigger: dict[str, Any] | None = None
    reason: str = ""


class SwitchMatrixConnectTool(BaseModel):
    tool: Literal["switch_matrix.connect"] = "switch_matrix.connect"
    instrument: str
    positive: str
    negative: str
    safety: SafetyBlock | None = None
    reason: str = ""


class SimulatorRunSpiceTool(BaseModel):
    tool: Literal["simulator.run_spice"] = "simulator.run_spice"
    analysis: Literal["dc_operating_point", "tran", "ac"] = "dc_operating_point"
    netlist_id: str = "current"
    expected_outputs: list[str] = Field(default_factory=list)
    reason: str = ""


class AbortTool(BaseModel):
    tool: Literal["abort"] = "abort"
    reason: str


AgentToolCall = (
    MultimeterVoltageTool
    | OscilloscopeCaptureTool
    | SwitchMatrixConnectTool
    | SimulatorRunSpiceTool
    | AbortTool
)


def parse_tool_call(data: dict[str, Any]) -> AgentToolCall:
    t = data.get("tool")
    if t == "multimeter.measure_voltage":
        return MultimeterVoltageTool.model_validate(data)
    if t == "oscilloscope.capture":
        return OscilloscopeCaptureTool.model_validate(data)
    if t == "switch_matrix.connect":
        return SwitchMatrixConnectTool.model_validate(data)
    if t == "simulator.run_spice":
        return SimulatorRunSpiceTool.model_validate(data)
    if t == "abort":
        return AbortTool.model_validate(data)
    raise ValueError(f"Unknown tool: {t}")

