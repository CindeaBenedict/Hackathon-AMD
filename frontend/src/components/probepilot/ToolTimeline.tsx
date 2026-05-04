"use client";

import { motion } from "framer-motion";
import { Cpu } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = { events: Record<string, unknown>[] };

export function ToolTimeline({ events }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Cpu className="h-4 w-4 text-amd" />
          Agent tool timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
        {events.length === 0 ? (
          <p className="text-xs text-slate-500">No tool events yet.</p>
        ) : (
          events.map((ev, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className="rounded-md border border-amd-border/70 bg-slate-900/60 px-2 py-1 text-xs text-slate-300"
            >
              <span className="font-mono text-[10px] uppercase text-slate-500">
                {String(ev.phase ?? "step")}
              </span>{" "}
              <span className="font-mono text-emerald-200">{String(ev.tool ?? "")}</span>{" "}
              <span className="text-slate-500">{String(ev.status ?? "")}</span>
            </motion.div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
