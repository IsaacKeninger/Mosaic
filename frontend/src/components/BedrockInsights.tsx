export function BedrockInsights({ recommendations }: { recommendations: string[] }) {
  return (
    <div className="rounded-xl border p-6 shadow-sm">
      <h3 className="font-semibold">Recommendations</h3>
      <ul className="mt-2 space-y-2 text-sm">
        {recommendations.map((rec) => (
          <li key={rec} className="flex gap-2">
            <span>💡</span>
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
