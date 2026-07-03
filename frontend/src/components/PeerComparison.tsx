"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export function PeerComparison({
  userFeatures,
  centroidFeatures,
}: {
  userFeatures: Record<string, number>;
  centroidFeatures: Record<string, number>;
}) {
  const data = Object.keys(userFeatures).map((key) => ({
    feature: key,
    you: userFeatures[key],
    average: centroidFeatures[key] ?? 0,
  }));

  return (
    <div className="h-72 w-full rounded-xl border p-4 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="feature" hide />
          <YAxis />
          <Tooltip />
          <Bar dataKey="you" fill="#6366f1" />
          <Bar dataKey="average" fill="#d1d5db" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
