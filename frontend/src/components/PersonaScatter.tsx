"use client";

import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export interface ScatterPoint {
  x: number;
  y: number;
  clusterId: number;
  userId: string;
}

export function PersonaScatter({ points, highlightUserId }: { points: ScatterPoint[]; highlightUserId?: string }) {
  return (
    <div className="h-72 w-full rounded-xl border p-4 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <XAxis type="number" dataKey="x" hide />
          <YAxis type="number" dataKey="y" hide />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter
            data={points}
            fill="#6366f1"
            shape={(props: any) =>
              props.payload.userId === highlightUserId ? (
                <circle cx={props.cx} cy={props.cy} r={8} fill="#ef4444" />
              ) : (
                <circle cx={props.cx} cy={props.cy} r={4} fill="#6366f1" opacity={0.5} />
              )
            }
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
