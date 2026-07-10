"use client";

import { useCallback, useEffect, useState } from "react";
import type { AlertOptions } from "@/components/shared/modals";
import { storyStructureAPI } from "@/utils/api/endpoints";
import type { Environment, NormalizedScene } from "@/utils/api/types";

export function useTimelineSceneEnvironments({
  showAlert,
}: {
  showAlert: (options: AlertOptions) => void;
}) {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [sceneEnvOverrides, setSceneEnvOverrides] = useState<
    Record<number, number | null>
  >({});
  const [selectedEnvironmentId, setSelectedEnvironmentId] = useState<
    number | null
  >(null);
  const [environmentSaving, setEnvironmentSaving] = useState(false);

  useEffect(() => {
    let active = true;
    void storyStructureAPI.listEnvironments().then((res) => {
      if (!active) return;
      setEnvironments(res.success && res.data ? res.data : []);
    });
    return () => {
      active = false;
    };
  }, []);

  const saveEnvironment = useCallback(async (selectedScene: NormalizedScene | null) => {
    if (!selectedScene) return;
    setEnvironmentSaving(true);
    try {
      const res = await storyStructureAPI.updateScene(selectedScene.id, {
        environment_id: selectedEnvironmentId,
      });
      if (res.success) {
        setSceneEnvOverrides((prev) => ({
          ...prev,
          [selectedScene.id]: selectedEnvironmentId,
        }));
        showAlert({ message: "Scene environment saved", variant: "success" });
      } else {
        showAlert({
          message: res.error || "Failed to save scene environment",
          variant: "error",
        });
      }
    } finally {
      setEnvironmentSaving(false);
    }
  }, [selectedEnvironmentId, showAlert]);

  return {
    environments,
    sceneEnvOverrides,
    selectedEnvironmentId,
    setSelectedEnvironmentId,
    environmentSaving,
    saveEnvironment,
  };
}
