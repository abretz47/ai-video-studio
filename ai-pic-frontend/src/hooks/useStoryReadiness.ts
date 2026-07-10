"use client";

import { useCallback, useState } from "react";
import { storyAPI } from "@/utils/api/endpoints";
import type { ReadinessResult, QuickFixResponse } from "@/utils/api/types";

interface UseStoryReadinessOptions {
  storyId: number | string | null;
  showAlert: (options: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
  }) => void;
  onStoryUpdated?: () => void;
}

export function useStoryReadiness({
  storyId,
  showAlert,
  onStoryUpdated,
}: UseStoryReadinessOptions) {
  const [readiness, setReadiness] = useState<ReadinessResult | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(false);
  const [readinessError, setReadinessError] = useState<string | null>(null);
  const [quickFixLoading, setQuickFixLoading] = useState(false);

  const checkReadiness = useCallback(async () => {
    if (!storyId) return;

    setReadinessLoading(true);
    setReadinessError(null);

    try {
      const result = await storyAPI.checkStoryReadiness(storyId);
      if (result.success && result.data) {
        setReadiness(result.data);
      } else {
        setReadinessError(result.error || "Check failed");
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      setReadinessError(message);
    } finally {
      setReadinessLoading(false);
    }
  }, [storyId]);

  const runQuickFix = useCallback(
    async (dryRun: boolean): Promise<QuickFixResponse | null> => {
      if (!storyId) return null;

      setQuickFixLoading(true);

      try {
        const result = await storyAPI.quickFixStory(storyId, {
          dry_run: dryRun,
        });
        if (result.success && result.data) {
          if (!dryRun) {
            showAlert({
              message: `Fixed ${result.data.improvement.fixed_count} issues`,
              variant: "success",
            });
            // Refresh readiness after applying fixes
            setReadiness(result.data.final_readiness);
            onStoryUpdated?.();
          }
          return result.data;
        } else {
          showAlert({
            message: `Quick fix failed: ${result.error || "Unknown error"}`,
            variant: "error",
          });
          return null;
        }
      } catch (e) {
        const message = e instanceof Error ? e.message : String(e);
        showAlert({
          message: `Quick fix failed: ${message}`,
          variant: "error",
        });
        return null;
      } finally {
        setQuickFixLoading(false);
      }
    },
    [storyId, showAlert, onStoryUpdated],
  );

  const canGenerate = readiness?.can_proceed ?? true;

  return {
    readiness,
    readinessLoading,
    readinessError,
    quickFixLoading,
    canGenerate,
    checkReadiness,
    runQuickFix,
  };
}
