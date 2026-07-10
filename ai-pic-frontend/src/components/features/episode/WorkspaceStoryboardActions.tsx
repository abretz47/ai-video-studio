"use client";

import Link from "next/link";
import { useState } from "react";
import { operatorButtonClass } from "@/components/shared";
import { generateStoryboardFromAudioTimelineAsync } from "@/utils/api/endpoints";

type ShowAlert = (options: {
  message: string;
  variant: "info" | "success" | "warning" | "error";
}) => void;

interface WorkspaceStoryboardActionsProps {
  selectedScriptId?: number | null;
  selectedAudioTimeline?: Record<string, unknown> | null;
  timelineHref: string;
  clipStoryboardHref?: string | null;
  showAlert?: ShowAlert;
}

export function WorkspaceStoryboardActions({
  selectedScriptId,
  selectedAudioTimeline,
  timelineHref,
  clipStoryboardHref,
  showAlert,
}: WorkspaceStoryboardActionsProps) {
  const [syncingAudioStoryboard, setSyncingAudioStoryboard] = useState(false);
  const hasClipStoryboardEntry = Boolean(clipStoryboardHref);
  const showAudioStoryboardSync = !hasClipStoryboardEntry;
  const canSyncAudioTimelineStoryboard = Boolean(
    selectedAudioTimeline && selectedScriptId && !syncingAudioStoryboard,
  );

  const handleSyncAudioTimelineStoryboard = async () => {
    if (!selectedScriptId) {
      showAlert?.({ message: "Please select a script first", variant: "warning" });
      return;
    }
    if (!selectedAudioTimeline) {
      showAlert?.({
        message: "Please generate the timeline first，then sync storyboard placeholders",
        variant: "warning",
      });
      return;
    }

    setSyncingAudioStoryboard(true);
    try {
      const res = await generateStoryboardFromAudioTimelineAsync(
        selectedScriptId,
        {
          overwrite_existing: false,
          min_pause_seconds: 1.5,
        },
      );
      if (!res.success || !res.data) {
        showAlert?.({
          message: res.error || "Failed to submit storyboard placeholder task",
          variant: "error",
        });
        return;
      }
      showAlert?.({
        message: `Storyboard placeholder task submitted #${res.data.task_id}`,
        variant: "success",
      });
    } catch (error) {
      showAlert?.({
        message:
          error instanceof Error
            ? `Failed to submit storyboard placeholder task：${error.message}`
            : "Failed to submit storyboard placeholder task",
        variant: "error",
      });
    } finally {
      setSyncingAudioStoryboard(false);
    }
  };

  return (
    <div className="flex flex-wrap justify-end gap-2">
      {clipStoryboardHref ? (
        <Link
          href={clipStoryboardHref}
          className={operatorButtonClass("secondary")}
        >
          Open the first clip storyboard
        </Link>
      ) : null}
      {showAudioStoryboardSync ? (
        <button
          type="button"
          disabled={!canSyncAudioTimelineStoryboard}
          className={operatorButtonClass(
            hasClipStoryboardEntry ? "ghost" : "primary",
          )}
          onClick={handleSyncAudioTimelineStoryboard}
        >
          {syncingAudioStoryboard ? "Submitting..." : "Sync Storyboard Placeholders"}
        </button>
      ) : null}
      {!clipStoryboardHref ? (
        <Link href={timelineHref} className={operatorButtonClass("secondary")}>
          Open Timeline
        </Link>
      ) : null}
    </div>
  );
}
