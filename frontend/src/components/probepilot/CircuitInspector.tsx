"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const DEMO_NETS = [
  { net: "VIN", nodes: ["TP1", "R1.1"] },
  { net: "DIV_OUT", nodes: ["TP2", "R1.2", "R2.1", "TP3"] },
  { net: "GND", nodes: ["R2.2", "Q1.E", "LED.C"] },
  { net: "BASE", nodes: ["TP5", "R3.2", "Q1.B"] },
  { net: "LOAD", nodes: ["TP6", "Q1.C", "R4.1"] },
];

export function CircuitInspector() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">KiCad-style inspector (demo)</CardTitle>
        <p className="text-xs text-slate-500">Nets and test points for the hackathon demo board.</p>
      </CardHeader>
      <CardContent className="space-y-2">
        {DEMO_NETS.map((row) => (
          <div key={row.net} className="rounded-md border border-amd-border/60 bg-slate-900/50 p-2">
            <div className="text-xs font-semibold text-amd">{row.net}</div>
            <div className="mt-1 flex flex-wrap gap-1">
              {row.nodes.map((n) => (
                <span key={n} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-200">
                  {n}
                </span>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
