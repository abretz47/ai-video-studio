"use client";

import { useCallback, useEffect, useState } from "react";
import { storyStructureAPI } from "@/utils/api/endpoints";
import type { NormalizedScene } from "@/utils/api/types";

export function useNormalizedScenes(scriptId: number | null) {
  const [normalizedScenes, setNormalizedScenes] = useState<NormalizedScene[]>(
    [],
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!scriptId) {
      setNormalizedScenes([]);
      setError(null);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const res = await storyStructureAPI.getNormalizedScenes(scriptId);
      if (res.success && res.data) {
        setNormalizedScenes(res.data);
      } else {
        setNormalizedScenes([]);
        setError(res.error || "Failed to load scenes");
      }
    } catch (err) {
      console.error("Failed to load scenes:", err);
      setNormalizedScenes([]);
      setError("Failed to load scenes");
    } finally {
      setLoading(false);
    }
  }, [scriptId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    normalizedScenes,
    normalizedScenesLoading: loading,
    normalizedScenesError: error,
    refreshNormalizedScenes: refresh,
  };
}
