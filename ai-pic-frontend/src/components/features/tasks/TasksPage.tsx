"use client";

import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorShell,
  OperatorState,
} from "@/components/shared";
import type { Task as APITask } from "@/utils/api/types";

import { TasksList } from "./TasksList";
import { TasksPagination } from "./TasksPagination";
import { TasksToolbar } from "./TasksToolbar";
import { useTaskPersistedStyle } from "./useTaskPersistedStyle";
import { useTasks } from "./useTasks";

const toTaskId = (id: APITask["id"]): number | null => {
  const taskId = typeof id === "number" ? id : Number(id);
  return Number.isInteger(taskId) ? taskId : null;
};

export function TasksPage() {
  const { showAlert } = useAlertModal();
  const {
    tasks,
    loading,
    fetchError,
    poll,
    setPoll,
    isStartingId,
    deletingTaskId,
    cancellingTaskId,
    page,
    setPage,
    size,
    total,
    totalPages,
    taskTypeFilter,
    setTaskTypeFilter,
    refresh,
    startTask,
    cancelTask,
    deleteTask,
  } = useTasks();

  const { expanded, toggleExpanded, persistedStyle, persistedLoading } =
    useTaskPersistedStyle();

  const handleCancel = (id: APITask["id"]) => {
    const taskId = toTaskId(id);
    if (!taskId) {
      showAlert({ message: "Invalid task ID. Unable to cancel the task.", variant: "warning" });
      return;
    }
    showAlert({
      title: "Cancel Task",
      message: `Are you sure you want to cancel task #${taskId}? Running work will be stopped if possible.`,
      variant: "warning",
      confirmText: "Confirm Cancel",
      onConfirm: () => {
        void cancelTask(taskId).then((res) => {
          if (!res.success) {
            showAlert({
              message: res.message || "Failed to cancel task",
              variant: "error",
            });
          }
        });
      },
    });
  };

  const handleStart = async (id: APITask["id"]) => {
    const taskId = toTaskId(id);
    if (!taskId) {
      showAlert({ message: "Invalid task ID. Unable to start the task.", variant: "warning" });
      return;
    }
    const res = await startTask(taskId);
    if (res.success) {
      showAlert({
        message: res.message || "Task started",
        variant: "success",
      });
    } else {
      showAlert({ message: res.message || "Failed to start task", variant: "error" });
    }
  };

  const handleDelete = (id: APITask["id"]) => {
    const taskId = toTaskId(id);
    if (!taskId) {
      showAlert({ message: "Invalid task ID. Unable to delete the task.", variant: "warning" });
      return;
    }
    showAlert({
      title: "Confirm Delete Task",
      message: "Are you sure you want to delete this task?",
      variant: "warning",
      confirmText: "Delete",
      onConfirm: async () => {
        const res = await deleteTask(taskId);
        if (!res.success) {
          showAlert({
            message: res.message || "Failed to delete task",
            variant: "error",
          });
        }
      },
    });
  };

  return (
    <OperatorShell
      title="Tasks"
      subtitle="Generation queue, retry handling, and audit information"
      breadcrumb={["IP Center", "Tasks"]}
    >
      <div className="space-y-4">
        <OperatorPanel>
          <OperatorSectionHeader
            title="Task Queue"
            subtitle={`${total} tasks total, currently on page ${page} / ${totalPages || 1}`}
            action={
          <TasksToolbar
            poll={poll}
            onPollChange={setPoll}
            onRefresh={() => void refresh()}
            taskTypeFilter={taskTypeFilter}
            onTaskTypeFilterChange={(next) => {
              setTaskTypeFilter(next);
              setPage(1);
            }}
          />
            }
          />
          {fetchError ? (
            <div className="p-4">
              <OperatorState title={fetchError} tone="red" />
            </div>
          ) : null}
          {loading ? (
            <div className="p-4">
              <OperatorState title="Loading task list..." />
            </div>
          ) : null}
          <TasksList
            tasks={tasks}
            loading={loading}
            fetchError={fetchError}
            expanded={expanded}
            onToggleExpanded={toggleExpanded}
            persistedStyle={persistedStyle}
            persistedLoading={persistedLoading}
            isStartingId={isStartingId}
            deletingTaskId={deletingTaskId}
            cancellingTaskId={cancellingTaskId}
            onStart={(taskId) => void handleStart(taskId)}
            onCancel={handleCancel}
            onDelete={handleDelete}
          />
          {!loading && !fetchError && tasks.length > 0 ? (
            <TasksPagination
              total={total}
              size={size}
              page={page}
              totalPages={totalPages}
              onPrev={() => setPage((p) => Math.max(1, p - 1))}
              onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
            />
          ) : null}
        </OperatorPanel>
      </div>
    </OperatorShell>
  );
}
