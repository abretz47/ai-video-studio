import { useCallback, useMemo, useState } from "react";

import { useTaskPolling, type TaskPollPair } from "@/hooks/useTaskPolling";
import { taskAPI } from "@/utils/api/endpoints";
import type { Task } from "@/utils/api/types";

interface UseVirtualIPImageTaskRefreshOptions {
  refreshImages: () => Promise<void>;
  showAlert: (opts: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
  }) => void;
}

export function useVirtualIPImageTaskRefresh({
  refreshImages,
  showAlert,
}: UseVirtualIPImageTaskRefreshOptions) {
  const [pendingTaskId, setPendingTaskId] = useState<number | null>(null);

  const fetchTask = useCallback(async (taskId: number) => {
    const response = await taskAPI.getTask(String(taskId));
    return response.success && response.data ? response.data : null;
  }, []);

  const handleTaskUpdate = useCallback(
    (task: Task | null) => {
      if (!task) return;
      if (task.status === "completed") {
        setPendingTaskId(null);
        void refreshImages()
          .then(() => {
            showAlert({
              message: "Image generation completed and the list has been refreshed",
              variant: "success",
            });
          })
          .catch((error) => {
            console.error("Failed to refresh virtual IP images:", error);
            showAlert({
              message: "Images generated, but failed to refresh the list",
              variant: "error",
            });
          });
        return;
      }
      if (task.status === "failed" || task.status === "cancelled") {
        setPendingTaskId(null);
        showAlert({
          message:
            task.error_message || task.progress_detail || "Image generation task not completed",
          variant: "error",
        });
      }
    },
    [refreshImages, showAlert],
  );

  const taskPairs = useMemo<TaskPollPair[]>(
    () => [{ id: pendingTaskId, onUpdate: handleTaskUpdate }],
    [handleTaskUpdate, pendingTaskId],
  );

  useTaskPolling({ taskPairs, fetchTask, intervalMs: 3000 });

  const trackTask = useCallback((taskId: number) => {
    setPendingTaskId(taskId);
  }, []);

  return {
    pendingImageTaskId: pendingTaskId,
    trackImageTask: trackTask,
  };
}
