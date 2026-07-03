import { useEffect, useState } from "react";
import { getPersona } from "@/lib/api";
import { UserFeatureVector } from "@/lib/types";

export function usePersona(userId: string | null) {
  const [data, setData] = useState<UserFeatureVector | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    getPersona(userId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  return { data, loading, error };
}
