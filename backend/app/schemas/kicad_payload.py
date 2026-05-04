from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KiCadPadNet(BaseModel):
    pad_index: int
    pad_name: str
    net: str


class KiCadFootprint(BaseModel):
    reference: str
    value: str
    footprint_id: str
    pads: list[KiCadPadNet] = Field(default_factory=list)


class KiCadDesignPayload(BaseModel):
    """Snapshot exported from KiCad (pcbnew plugin or CLI)."""

    kicad_version: str = ""
    # pcbnew | schematic_netlist | cli
    source: str = "pcbnew"
    board_path: str = ""
    footprints: list[KiCadFootprint] = Field(default_factory=list)
    nets: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class KiCadAnalyzeRequest(BaseModel):
    design: KiCadDesignPayload
    user_message: str | None = Field(
        default=None,
        description="Optional goal, e.g. 'Check power integrity hints before fab.'",
    )
