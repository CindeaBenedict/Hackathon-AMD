from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_settings
from app.deps import agent
from app.routers import kicad
from app.schemas.tools import parse_tool_call
from app.services.agent import state_to_json
from app.services.safety import validate_tool_call

app = FastAPI(title="ProbePilot", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    get_settings()


def _cors_origins() -> list[str]:
    return [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kicad.router, prefix="/api/kicad", tags=["kicad"])


class ChatRequest(BaseModel):
    message: str
    measurements: dict[str, float] = Field(default_factory=dict)


class ToolValidateRequest(BaseModel):
    command: dict[str, Any]


class RagRequest(BaseModel):
    query: str
    circuit_type: str | None = None
    topic: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "probepilot"}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    state = agent.run_turn(req.message, req.measurements)
    return state_to_json(state)


@app.post("/api/tools/validate")
def validate_tool(req: ToolValidateRequest) -> dict[str, Any]:
    try:
        cmd = parse_tool_call(req.command)
    except Exception as e:
        return {"valid": False, "error": str(e)}
    res = validate_tool_call(cmd)
    return {
        "valid": True,
        "allowed": res.allowed,
        "requires_human_confirmation": res.requires_human_confirmation,
        "message": res.message,
        "normalized": req.command,
    }


@app.post("/api/rag/query")
def rag_query(req: RagRequest) -> dict[str, Any]:
    hits = agent.rag.query(req.query, circuit_type=req.circuit_type, topic=req.topic)
    return {"results": hits}


@app.websocket("/ws/diagnostics")
async def ws_diagnostics(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "invalid json"})
                continue
            msg = payload.get("message", "")
            meas = payload.get("measurements") or {}
            state = agent.run_turn(msg, meas if isinstance(meas, dict) else {})
            await ws.send_json({"type": "agent_state", "data": state_to_json(state)})
            await asyncio.sleep(0)  # yield
    except WebSocketDisconnect:
        return
