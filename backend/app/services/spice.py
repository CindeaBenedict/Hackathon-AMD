"""SPICE / ngspice integration stub — replace with subprocess to ngspice on MI300X dev image."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SpiceResult:
    analysis: str
    node_voltages: dict[str, float]
    notes: str


def run_dc_operating_point(netlist_id: str) -> SpiceResult:
    """Demo board nominal DC values (fault injection happens in measurements, not here)."""
    _ = netlist_id
    return SpiceResult(
        analysis="dc_operating_point",
        node_voltages={
            "TP1": 9.0,
            "TP2": 3.0,
            "TP3": 3.0,
            "TP4": 3.05,
            "TP5": 0.65,
            "TP6": 0.0,
            "LED_ANODE": 2.4,
            "GND": 0.0,
        },
        notes="Stub simulation — wire ngspice for real netlists.",
    )


def compare_to_expected(
    measured: dict[str, float],
    expected: dict[str, float],
    tol_ratio: float = 0.15,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for k, ev in expected.items():
        if k not in measured:
            continue
        mv = measured[k]
        band = max(0.05, abs(ev) * tol_ratio)
        if abs(mv - ev) > band:
            issues.append(
                {
                    "node": k,
                    "expected": ev,
                    "measured": mv,
                    "delta": round(mv - ev, 4),
                }
            )
    return issues
