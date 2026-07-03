export interface Persona {
  personaId: string;
  clusterId: number;
  name: string;
  description: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  centroidFeatures: Record<string, number>;
  memberCount: number;
}

export interface UserFeatureVector {
  userId: string;
  clusterId: number;
  personaId: string;
  featureVector: Record<string, number>;
  lastSynced: string;
  pcaCoordinates: { x: number; y: number };
}

export interface SandboxUser {
  username: string;
  profile: string;
}
