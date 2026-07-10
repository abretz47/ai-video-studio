"use client";

import type {
  ClipGenerationTaskKind,
  TrackedClipGenerationTask,
} from "./useTimelineClipGenerationTaskTracker";
import { clipGenerationTaskKindLabel } from "./useTimelineClipGenerationTaskTracker";

/**
 * Inline generation progress for one queued clip task, shown directly under
 * the submit button so the operator never has to leave for the task list.
 */
export function TimelineClipTaskStatusLine({
  kind,
  task,
  currentClipId,
}: {
  kind: ClipGenerationTaskKind;
  task: TrackedClipGenerationTask | undefined;
  currentClipId: string | null;
}) {
  if (!task) return null;
  if (task.clipId && currentClipId && task.clipId !== currentClipId) {
    return null;
  }
  const label = clipGenerationTaskKindLabel(kind);
  if (task.phase === "pending" || task.phase === "processing") {
    return (
      <div
        className="mt-2 flex items-center gap-2 rounded-md bg-blue-50 px-2 py-1.5 text-[11px] text-blue-700"
        role="status"
      >
        <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        <span>
          {label}Generating (Task #{task.taskId})，will auto-refresh after completion…
        </span>
      </div>
    );
  }
  if (task.phase === "completed") {
    return (
      <div className="mt-2 rounded-md bg-green-50 px-2 py-1.5 text-[11px] text-green-700">
        {label}GeneratedCompleted（Task #{task.taskId})
      </div>
    );
  }
  if (task.phase === "failed") {
    return (
      <div className="mt-2 rounded-md bg-red-50 px-2 py-1.5 text-[11px] text-red-700">
        {label}Generation failed (Task #{task.taskId})：{task.error || "Unknown error"}
      </div>
    );
  }
  if (task.phase === "timeout") {
    return (
      <div className="mt-2 rounded-md bg-amber-50 px-2 py-1.5 text-[11px] text-amber-700">
        {label}Task #{task.taskId} wait timed out. Please check the task list later
      </div>
    );
  }
  return null;
}
