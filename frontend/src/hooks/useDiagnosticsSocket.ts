"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { wsDiagnosticsUrl } from "@/lib/utils";

export type AgentStatePayload = {
  session_id: string;
  phase: string;
  reply: string;
  confidence: number;
  rag_hits: { source: string; topic: string; snippet: string; score: number }[];
  simulation: { node_voltages?: Record<string, number>; notes?: string };
  measurements: Record<string, number>;
  faults: { fault: string; confidence: number }[];
  tool_timeline: Record<string, unknown>[];
  next_tool: Record<string, unknown> | null;
};

export function useDiagnosticsSocket() {
  const [connected, setConnected] = useState(false);
  const [last, setLast] = useState<AgentStatePayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const url = wsDiagnosticsUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen = () => {
      setConnected(true);
      setError(null);
    };
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setError("WebSocket error");
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string);
        if (msg.type === "agent_state") setLast(msg.data as AgentStatePayload);
        if (msg.type === "error") setError(String(msg.message));
      } catch {
        setError("Bad message from server");
      }
    };
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  const sendPrompt = useCallback((message: string, measurements: Record<string, number>) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setError("Socket not connected");
      return;
    }
    ws.send(JSON.stringify({ message, measurements }));
  }, []);

  return { connected, last, error, sendPrompt };
}
