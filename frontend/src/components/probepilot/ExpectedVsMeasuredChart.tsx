"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = {
  expected: Record<string, number>;
  measured: Record<string, number>;
};

export function ExpectedVsMeasuredChart({ expected, measured }: Props) {
  const keys = Array.from(new Set([...Object.keys(expected), ...Object.keys(measured)])).filter((k) => k !== "GND");
  const data = keys.map((k) => ({
    node: k,
    expected: expected[k] ?? null,
    measured: measured[k] ?? null,
  }));

  return (
    <Card className="min-h-[280px]">
      <CardHeader>
        <CardTitle className="text-sm">Expected vs measured (V)</CardTitle>
      </CardHeader>
      <CardContent className="h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="node" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[0, "auto"]} />
            <Tooltip
              contentStyle={{ background: "#020617", border: "1px solid #1f2937", borderRadius: 8 }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Legend />
            <Line type="monotone" dataKey="expected" stroke="#38bdf8" strokeWidth={2} dot={false} name="Expected" />
            <Line type="monotone" dataKey="measured" stroke="#f97316" strokeWidth={2} dot name="Measured" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
