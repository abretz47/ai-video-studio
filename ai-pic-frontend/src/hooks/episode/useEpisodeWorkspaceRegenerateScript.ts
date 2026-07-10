"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { scriptAPI } from "@/utils/api/endpoints";
import type { Script, Task } from "@/utils/api/types";
import type { NotifyVariant } from "@/components/shared/notifications";
import { useGenerationTaskTracker } from "@/hooks/useGenerationTaskTracker";
import { sortScriptsNewestFirst } from "./scriptSort";
import type {
  PendingRegenerateState,
  ShowAlert,
} from "./episodeWorkspaceScriptActions.types";
import { parsePendingRegenerateState } from "./episodeWorkspaceScriptActions.types";
import { resolveScriptIdFromTask } from "./useEpisodeWorkspaceScriptTaskTracking";

export function useEpisodeWorkspaceRegenerateScript(args: {
  episodeKey: string;
  scripts: Script[];
  setScripts: React.Dispatch<React.SetStateAction<Script[]>>;
  showAlert: ShowAlert;
  onSelectScript: (scriptId: number | null) => void;
  regenerateScriptId: number | null;
  notify?: (message: string, variant: NotifyVariant) => void;
  pollIntervalMs?: number;
}) {
  const {
    episodeKey,
    scripts,
    setScripts,
    showAlert,
    onSelectScript,
    regenerateScriptId,
    notify,
    pollIntervalMs,
  } = args;

  const [submitting, setSubmitting] = useState(false);
  const knownIdsRef = useRef<Set<number>>(new Set());
  const pendingStorageKey = useMemo(
    () => `episode-workspace:pending-regenerate:${episodeKey}`,
    [episodeKey],
  );

  const setPendingRegenerate = useCallback(
    (payload: PendingRegenerateState) => {
      if (typeof window === "undefined") return;
      sessionStorage.setItem(pendingStorageKey, JSON.stringify(payload));
    },
    [pendingStorageKey],
  );

  const clearPendingRegenerate = useCallback(() => {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(pendingStorageKey);
  }, [pendingStorageKey]);

  const getPendingRegenerate = useCallback(() => {
    if (typeof window === "undefined") return null;
    const pending = parsePendingRegenerateState(
      sessionStorage.getItem(pendingStorageKey),
    );
    if (!pending) return null;
    const maxAgeMs = 1000 * 60 * 60 * 24; // 24h
    if (Date.now() - pending.createdAtMs > maxAgeMs) {
      sessionStorage.removeItem(pendingStorageKey);
      return null;
    }
    return pending;
  }, [pendingStorageKey]);

  const handleCompleted = useCallback(
    async (_kind: "regenerate", _taskId: number, task: Task | null) => {
      clearPendingRegenerate();
      const scriptIdFromTask = resolveScriptIdFromTask(task);
      const scriptsRes = await scriptAPI.getEpisodeScripts(episodeKey);
      if (
        !scriptsRes.success ||
        !Array.isArray(scriptsRes.data) ||
        scriptsRes.data.length === 0
      ) {
        showAlert({ message: "Failed to load the latest script list", variant: "warning" });
        return;
      }
      const ordered = sortScriptsNewestFirst(scriptsRes.data);
      setScripts(ordered);
      const known = knownIdsRef.current;
      const picked =
        (typeof scriptIdFromTask === "number"
          ? ordered.find((script) => script.id === scriptIdFromTask)
          : null) ||
        ordered.find((script) => !known.has(script.id)) ||
        null;
      if (!picked) {
        showAlert({
          message: "A new script was generated but is not yet visible in the list. Please refresh later.",
          variant: "info",
        });
        return;
      }
      onSelectScript(picked.id);
      const bizIdHint = picked.business_id
        ? ` [${picked.business_id.slice(0, 8)}...]`
        : "";
      notify?.(
        `Generated new script（v${picked.version} / ID: ${picked.id}${bizIdHint})`,
        "success",
      );
    },
    [
      clearPendingRegenerate,
      episodeKey,
      notify,
      onSelectScript,
      setScripts,
      showAlert,
    ],
  );

  const tracker = useGenerationTaskTracker<"regenerate">({
    labels: { regenerate: "New Script Version" },
    onCompleted: handleCompleted,
    onFailed: () => clearPendingRegenerate(),
    onNotify: notify,
    pollIntervalMs,
  });

  const handleRegenerateScript = useCallback(
    async (model?: string) => {
      if (!regenerateScriptId) {
        showAlert({ message: "No script available for regeneration", variant: "warning" });
        return;
      }
      try {
        setSubmitting(true);
        const knownIds = new Set((scripts || []).map((script) => script.id));
        const res = await scriptAPI.regenerateScript(
          regenerateScriptId,
          model ? { model } : undefined,
        );
        if (res.success && res.data?.task_id) {
          knownIdsRef.current = knownIds;
          setPendingRegenerate({
            taskId: res.data.task_id,
            knownScriptIds: [...knownIds],
            createdAtMs: Date.now(),
          });
          notify?.(
            `Script regeneration task submitted #${res.data.task_id}，and the new version will be auto-selected when completed`,
            "info",
          );
          tracker.track("regenerate", res.data.task_id);
        } else {
          showAlert({
            message: `Script regeneration failed: ${res.error || "Unknown error"}`,
            variant: "error",
          });
        }
      } catch (error) {
        console.error("Failed to regenerate script:", error);
        showAlert({ message: "Script regeneration failed", variant: "error" });
      } finally {
        setSubmitting(false);
      }
    },
    [
      notify,
      regenerateScriptId,
      scripts,
      setPendingRegenerate,
      showAlert,
      tracker,
    ],
  );

  const resumedRef = useRef(false);
  useEffect(() => {
    if (resumedRef.current) return;
    resumedRef.current = true;
    const pending = getPendingRegenerate();
    if (!pending) return;
    knownIdsRef.current = new Set(pending.knownScriptIds);
    tracker.track("regenerate", pending.taskId);
  }, [getPendingRegenerate, tracker]);

  const regenerating = submitting || tracker.isActive("regenerate");

  return { regenerating, handleRegenerateScript };
}
