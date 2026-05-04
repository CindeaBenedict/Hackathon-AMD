"""Agent loop: Observe → Reason → Retrieve → Simulate → Measure → Diagnose → Act (orchestrated)."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from app.services.rag import RagEngine
from app.services.spice import compare_to_expected, run_dc_operating_point


Phase = Literal[
    "observe",
    "reason",
    "retrieve",
    "simulate",
    "measure",
    "diagnose",
    "act",
]


@dataclass
class AgentState:
    session_id: str
    user_message: str
    phase: Phase = "observe"
    rag_hits: list[dict] = field(default_factory=list)
    simulation: dict[str, Any] = field(default_factory=dict)
    measurements: dict[str, float] = field(default_factory=dict)
    faults: list[dict] = field(default_factory=list)
    tool_timeline: list[dict] = field(default_factory=list)
    reply: str = ""
    confidence: float = 0.0
    next_tool: dict[str, Any] | None = None


class ProbePilotAgent:
    def __init__(self) -> None:
        self.rag = RagEngine()

    def run_turn(self, user_message: str, measurements: dict[str, float] | None = None) -> AgentState:
        sid = str(uuid.uuid4())
        state = AgentState(session_id=sid, user_message=user_message)
        meas = dict(measurements or {})

        # Demo: LED fault scenario — missing base drive if TP5 low while Vin ok
        low = user_message.lower()
        if any(k in low for k in ("led", "does not turn on", "won't turn on", "not turn on")):
            return self._demo_led_fault(state, meas)

        # Generic path
        state.phase = "retrieve"
        state.rag_hits = self.rag.query(user_message, max_results=4)
        state.phase = "simulate"
        sr = run_dc_operating_point("current")
        state.simulation = {"node_voltages": sr.node_voltages, "notes": sr.notes}
        state.phase = "diagnose"
        issues = compare_to_expected(meas, sr.node_voltages)
        state.faults = [{"fault": "measurement mismatch", "details": issues, "confidence": 0.5}] if issues else []
        state.confidence = 0.55 if not issues else 0.72
        state.reply = (
            "I parsed your request, pulled theory from the knowledge base, and compared "
            "your latest measurements to a DC operating-point estimate. "
            "Upload a netlist or schematic for a tighter loop."
        )
        state.next_tool = {
            "tool": "multimeter.measure_voltage",
            "target": {"positive_probe": "TP2", "negative_probe": "GND"},
            "mode": "DC",
            "expected_range": "2.8V-3.2V",
            "safety": {"max_expected_voltage": "12V", "safe": True},
            "reason": "Anchor the divider output before chasing downstream faults.",
        }
        state.tool_timeline.append({"phase": "simulate", "tool": "simulator.run_spice", "status": "ok"})
        state.tool_timeline.append({"phase": "measure", "tool": "multimeter.measure_voltage", "status": "proposed"})
        return state

    def _demo_led_fault(self, state: AgentState, meas: dict[str, float]) -> AgentState:
        """Injected-fault demo: high Vin, low base → LED off."""
        state.phase = "retrieve"
        state.rag_hits = self.rag.query("LED driver transistor base fault", topic="LED", max_results=3)
        state.phase = "simulate"
        sr = run_dc_operating_point("demo_board")
        state.simulation = {"node_voltages": sr.node_voltages, "notes": sr.notes}
        state.phase = "measure"

        # merge demo measurements if client sent empty
        demo = {
            "TP1": meas.get("TP1", 9.0),
            "TP2": meas.get("TP2", 3.0),
            "TP4": meas.get("TP4", 3.0),
            "TP5": meas.get("TP5", 0.05),
            "LED_ANODE": meas.get("LED_ANODE", 0.0),
        }
        state.measurements = demo

        state.phase = "diagnose"
        if demo["TP5"] < 0.4 and demo["TP1"] > 6:
            state.faults = [
                {"fault": "Missing or weak base drive (TP5 low)", "confidence": 0.78},
                {"fault": "Open base resistor / wrong value", "confidence": 0.14},
                {"fault": "Dead LED (less likely if anode near 0V)", "confidence": 0.08},
            ]
            state.confidence = 0.78
            state.reply = (
                "Vin looks healthy and the divider node is in range, but the transistor base (TP5) "
                "is far below what we need to switch the LED chain. Next, confirm the base resistor "
                "value and continuity from the driving node — expect ~0.6–0.8V at the base when active."
            )
            state.next_tool = {
                "tool": "multimeter.measure_voltage",
                "target": {"positive_probe": "TP5", "negative_probe": "GND"},
                "mode": "DC",
                "expected_range": "0.55V-0.85V",
                "safety": {"max_expected_voltage": "12V", "safe": True},
                "reason": "Verify whether the base is being biased; low reading implies missing drive.",
            }
        else:
            state.faults = [{"fault": "Further localization needed", "confidence": 0.4}]
            state.confidence = 0.5
            state.reply = "Measurements look partially healthy — capture TP6 and LED anode next."
            state.next_tool = {
                "tool": "multimeter.measure_voltage",
                "target": {"positive_probe": "LED_ANODE", "negative_probe": "GND"},
                "mode": "DC",
                "expected_range": "1.8V-3.0V",
                "safety": {"max_expected_voltage": "12V", "safe": True},
                "reason": "Check LED forward voltage with supply present.",
            }

        state.tool_timeline = [
            {"phase": "simulate", "tool": "simulator.run_spice", "payload": {"analysis": "dc_operating_point"}, "status": "ok"},
            {"phase": "measure", "tool": "multimeter.measure_voltage", "payload": {"target": "TP1"}, "status": "synthetic"},
            {"phase": "measure", "tool": "multimeter.measure_voltage", "payload": {"target": "LED_ANODE"}, "status": "synthetic"},
            {"phase": "measure", "tool": "multimeter.measure_voltage", "payload": {"target": "TP5"}, "status": "synthetic"},
            {"phase": "diagnose", "tool": "internal.rank_faults", "status": "ok"},
        ]
        return state


def state_to_json(state: AgentState) -> dict[str, Any]:
    return {
        "session_id": state.session_id,
        "phase": state.phase,
        "reply": state.reply,
        "confidence": state.confidence,
        "rag_hits": state.rag_hits,
        "simulation": state.simulation,
        "measurements": state.measurements,
        "faults": state.faults,
        "tool_timeline": state.tool_timeline,
        "next_tool": state.next_tool,
    }


def pretty_tool_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, indent=2)
