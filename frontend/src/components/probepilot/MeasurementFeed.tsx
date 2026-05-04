"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = { measurements: Record<string, number> };

export function MeasurementFeed({ measurements }: Props) {
  const entries = Object.entries(measurements);
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Activity className="h-4 w-4 text-amd" />
          Live measurements
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {entries.length === 0 ? (
          <p className="text-xs text-slate-500">Waiting for agent or bench feed…</p>
        ) : (
          entries.map(([k, v]) => (
            <motion.div
              key={k}
              layout
              className="flex items-center justify-between rounded-md border border-amd-border/70 bg-slate-900/60 px-2 py-1 font-mono text-xs"
            >
              <span className="text-slate-400">{k}</span>
              <span className="text-emerald-300">{v.toFixed(3)} V</span>
            </motion.div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
