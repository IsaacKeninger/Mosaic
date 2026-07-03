import { Persona, UserFeatureVector } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getPersona(userId: string): Promise<UserFeatureVector> {
  const res = await fetch(`${API_BASE_URL}/persona/${userId}`);
  if (!res.ok) throw new Error(`Failed to fetch persona for ${userId}`);
  return res.json();
}

export async function getPersonaDetails(personaId: string): Promise<Persona> {
  const res = await fetch(`${API_BASE_URL}/persona/details/${personaId}`);
  if (!res.ok) throw new Error(`Failed to fetch persona details for ${personaId}`);
  return res.json();
}
