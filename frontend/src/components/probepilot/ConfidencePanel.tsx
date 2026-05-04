"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = { confidence: number; faults: { fault: string; confidence: number }[] };

export function ConfidencePanel({ confidence, faults }: Props) {
  const pct = Math.round(Math.min(1, Math.max(0, confidence)) * 100);
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Diagnosis confidence</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
          <motion.div
            className="h-full bg-gradient-to-r from-amd to-orange-400"
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ type: "spring", stiffness: 120, damping: 18 }}
          />
        </div>
        <p className="text-xs text-slate-400">{pct}% aggregate confidence (demo heuristic)</p>
        <div className="space-y-2">
          {faults.map((f) => (
            <div key={f.fault} className="flex items-center justify-between text-xs">
              <span className="text-slate-300">{f.fault}</span>
              <span className="font-mono text-slate-400">{Math.round(f.confidence * 100)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
