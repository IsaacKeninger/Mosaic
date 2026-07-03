import { Persona } from "@/lib/types";

export function PersonaCard({ persona }: { persona: Persona }) {
  return (
    <div className="rounded-xl border p-6 shadow-sm">
      <h2 className="text-xl font-bold">{persona.name}</h2>
      <p className="mt-2 text-sm text-gray-600">{persona.description}</p>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <h3 className="font-semibold">Strengths</h3>
          <ul className="list-disc pl-4">
            {persona.strengths.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold">Weaknesses</h3>
          <ul className="list-disc pl-4">
            {persona.weaknesses.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
