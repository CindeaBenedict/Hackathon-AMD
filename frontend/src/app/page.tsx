"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { CircuitUploadPanel } from "@/components/probepilot/CircuitUploadPanel";
import { ChatPanel } from "@/components/probepilot/ChatPanel";
import { MeasurementFeed } from "@/components/probepilot/MeasurementFeed";
import { ConfidencePanel } from "@/components/probepilot/ConfidencePanel";
import { ExpectedVsMeasuredChart } from "@/components/probepilot/ExpectedVsMeasuredChart";
import { ToolTimeline } from "@/components/probepilot/ToolTimeline";
import { JsonToolViewer } from "@/components/probepilot/JsonToolViewer";
import { CircuitInspector } from "@/components/probepilot/CircuitInspector";
import { useDiagnosticsSocket } from "@/hooks/useDiagnosticsSocket";
import { useVoiceLab } from "@/hooks/useVoiceLab";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  const { connected, last, error, sendPrompt } = useDiagnosticsSocket();
  const [measurements, setMeasurements] = useState<Record<string, number>>({
    TP1: 9.0,
    TP2: 3.0,
    TP4: 3.0,
    TP5: 0.05,
    LED_ANODE: 0.0,
  });

  const onTranscript = useCallback(
    (text: string) => {
      sendPrompt(text, measurements);
    },
    [sendPrompt, measurements],
  );

  const { listening, supported, start, stop, speak } = useVoiceLab(onTranscript);
  const spokenSid = useRef<string | null>(null);

  useEffect(() => {
    if (!last?.session_id || !last.reply) return;
    if (spokenSid.current === last.session_id) return;
    spokenSid.current = last.session_id;
    speak(last.reply);
  }, [last, speak]);

  const handleSend = useCallback(
    (text: string) => {
      sendPrompt(text, measurements);
    },
    [sendPrompt, measurements],
  );

  const expected = useMemo(() => last?.simulation?.node_voltages ?? {}, [last]);

  useEffect(() => {
    if (last?.measurements && Object.keys(last.measurements).length) {
      setMeasurements((m) => ({ ...m, ...last.measurements }));
    }
  }, [last?.measurements]);

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 lg:px-8">
      <header className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-amd to-orange-500 shadow-lg shadow-amd/30" />
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">ProbePilot</h1>
              <p className="text-sm text-slate-400">Cursor for circuits — AMD GPU–ready agentic lab copilot</p>
            </div>
          </motion.div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge>Observe → Reason → Retrieve → Simulate → Measure → Diagnose → Act</Badge>
          {error ? <Badge className="border-red-500/50 text-red-300">{error}</Badge> : null}
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-1">
          <CircuitUploadPanel />
          <MeasurementFeed measurements={last?.measurements && Object.keys(last.measurements).length ? last.measurements : measurements} />
          <CircuitInspector />
        </div>
        <div className="space-y-4 lg:col-span-1">
          <ChatPanel
            connected={connected}
            onSend={handleSend}
            onVoice={() => {
              if (listening) stop();
              else start();
            }}
            listening={listening}
            voiceSupported={supported}
            lastReply={last?.reply}
          />
          <ConfidencePanel confidence={last?.confidence ?? 0} faults={last?.faults ?? []} />
        </div>
        <div className="space-y-4 lg:col-span-1">
          <ExpectedVsMeasuredChart expected={expected} measured={last?.measurements ?? measurements} />
          <ToolTimeline events={last?.tool_timeline ?? []} />
          <JsonToolViewer data={(last?.next_tool as Record<string, unknown>) ?? null} />
        </div>
      </section>

      <footer className="text-center text-[11px] text-slate-500">
        Hardware commands are validated server-side. Risky relay paths require explicit human confirmation.{" "}
        <span className="text-slate-600">Lab Professor Mode (custom teacher voice) only with written consent.</span>
      </footer>
    </main>
  );
}
