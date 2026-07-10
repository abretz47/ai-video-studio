"use client";

interface StatusLineTask {
  taskId: number;
  phase: string;
  error: string | null;
}

/**
 * Inline progress line for one tracked generation task, shown next to the
 * submit control so operators never have to leave for the task list.
 */
export function GenerationTaskStatusLine({
  label,
  task,
}: {
  label: string;
  task?: StatusLineTask | null;
}) {
  if (!task) return null;
  if (task.phase === "pending" || task.phase === "processing") {
    return (
      <div
        className="mt-2 flex items-center gap-2 rounded-md bg-blue-50 px-2 py-1.5 text-xs text-blue-700"
        role="status"
      >
        <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        <span>
          {label} is generating (Task #{task.taskId}). This view will refresh automatically when it finishes…
        </span>
      </div>
    );
  }
  if (task.phase === "completed") {
    return (
      <div className="mt-2 rounded-md bg-green-50 px-2 py-1.5 text-xs text-green-700">
        {label} completed successfully (Task #{task.taskId})
      </div>
    );
  }
  if (task.phase === "failed") {
    return (
      <div className="mt-2 rounded-md bg-red-50 px-2 py-1.5 text-xs text-red-700">
        {label} failed to generate (Task #{task.taskId}):{" "}
        {task.error || "Unknown error"}
      </div>
    );
  }
  if (task.phase === "timeout") {
    return (
      <div className="mt-2 rounded-md bg-amber-50 px-2 py-1.5 text-xs text-amber-700">
        Task #{task.taskId} for {label} timed out. Please check the task list later.
      </div>
    );
  }
  return null;
}
