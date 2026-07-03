"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#84cc16"];

export function SpendingBreakdown({ featureVector }: { featureVector: Record<string, number> }) {
  const data = Object.entries(featureVector)
    .filter(([key]) => key.startsWith("pct_"))
    .map(([key, value]) => ({ name: key.replace("pct_", ""), value }));

  return (
    <div className="h-64 w-full rounded-xl border p-4 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
