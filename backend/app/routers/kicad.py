from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.deps import agent
from app.schemas.kicad_payload import KiCadAnalyzeRequest
from app.services.kicad_analyze import analyze_kicad_design

router = APIRouter()


@router.post("/analyze")
def kicad_analyze(req: KiCadAnalyzeRequest) -> dict[str, Any]:
    """Accept design JSON from the KiCad plugin (or CLI) and return checks + agent reasoning."""
    return analyze_kicad_design(req.design, agent, req.user_message)
