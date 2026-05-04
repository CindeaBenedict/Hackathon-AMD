"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = { data: Record<string, unknown> | null };

export function JsonToolViewer({ data }: Props) {
  const text = data ? JSON.stringify(data, null, 2) : "// Next validated tool call appears here";
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">JSON tool call (validated)</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="max-h-[220px] overflow-auto rounded-lg border border-amd-border bg-black/60 p-3 font-mono text-[11px] leading-relaxed text-emerald-100">
          {text}
        </pre>
      </CardContent>
    </Card>
  );
}
