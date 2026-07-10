"use client";

import Link from "next/link";
import { formatDateTime, t } from "@/lib/i18n";
import {
  OperatorShell,
  OperatorPanel,
  OperatorInspector,
  OperatorMainCanvas,
  OperatorSectionHeader,
  OperatorState,
  OperatorWorkspace,
  ProgressBar,
  StatusPill,
  operatorButtonClass,
  operatorTableClass,
  operatorTableHeadClass,
  operatorTableRowClass,
  taskStatusTone,
} from "@/components/shared";
import { useWorkbenchSummary } from "@/hooks/useWorkbenchSummary";
import type { WorkbenchTask } from "@/utils/api/types";
import { episodeWorkspaceHref } from "@/utils/routes";
import { AuditItem, MetricCard, ReadyCell } from "./WorkbenchDashboardParts";

const taskStatusLabel = (status: string) => {
  if (status === "processing") return t("workbench.taskStatus.processing", "Running");
  if (status === "pending") return t("workbench.taskStatus.pending", "Queued");
  if (status === "completed") return t("workbench.taskStatus.completed", "Completed");
  if (status === "failed") return t("workbench.taskStatus.failed", "Failed");
  if (status === "cancelled") return t("workbench.taskStatus.cancelled", "Cancelled");
  return status;
};

const taskTone = (task: WorkbenchTask) =>
  task.status === "failed"
    ? "red"
    : task.status === "completed"
    ? "green"
    : task.status === "processing"
    ? "amber"
    : "blue";

export function WorkbenchDashboard() {
  const { summary, loading, error, refresh } = useWorkbenchSummary();

  return (
    <OperatorShell
      title={t("workbench.title", "IP Production Workspace")}
      subtitle={t("workbench.subtitle", "Continue stories, episodes, and tasks around each IP")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("workbench.breadcrumb", "Production Workspace"),
      ]}
    >
      {loading ? (
        <OperatorState title={t("workbench.loading", "Loading workspace data...")} />
      ) : error ? (
        <OperatorState
          title={error}
          tone="red"
          action={
            <button
              type="button"
              onClick={() => void refresh()}
              className={operatorButtonClass("danger")}
            >
              {t("common.retry", "Retry")}
            </button>
          }
        />
      ) : summary ? (
        <OperatorWorkspace
          variant="main-inspector"
          main={
            <OperatorMainCanvas className="space-y-5">
              <OperatorPanel className="p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="text-sm font-semibold text-gray-950">
                      {t("workbench.stateTitle", "IP / environment production status")}
                    </h2>
                    <p className="mt-1 text-xs text-gray-500">
                      {t(
                        "workbench.stateDescription",
                        "Current production flows through IPs, stories, episodes, and environment assets. Start new work from IP projects first.",
                      )}
                    </p>
                  </div>
                  <Link href="/virtual-ip" className={operatorButtonClass("primary")}>
                    {t("workbench.openIpProjects", "Open IP projects")}
                  </Link>
                </div>
              </OperatorPanel>

              <div className="grid gap-3 md:grid-cols-4">
                <MetricCard label={t("workbench.metrics.pending", "Pending today")} value={summary.metrics.pending_tasks} />
                <MetricCard label={t("workbench.metrics.running", "Running")} value={summary.metrics.running_tasks} />
                <MetricCard label={t("workbench.metrics.failed", "Failed tasks")} value={summary.metrics.failed_tasks} tone="red" />
                <MetricCard label={t("workbench.metrics.continuable", "Ready to continue")} value={summary.metrics.continuable_episodes} tone="green" />
              </div>

              <OperatorPanel>
                <OperatorSectionHeader
                  title={t("workbench.continueTitle", "Continue production")}
                  subtitle={t("workbench.continueSubtitle", "Move existing content forward into the episode timeline")}
                  action={
                    <Link href="/stories" className={operatorButtonClass("secondary")}>
                      {t("common.viewAll", "View all")}
                    </Link>
                  }
                />
                <div className="overflow-x-auto">
                  <table className={`${operatorTableClass} min-w-[1080px]`}>
                    <thead className={operatorTableHeadClass}>
                      <tr>
                        <th className="w-[280px] px-5 py-3 text-left font-medium">
                          {t("workbench.table.ipStoryEpisode", "IP / Story / Episode")}
                        </th>
                        <th className="px-4 py-3 text-left font-medium">{t("workbench.table.currentStage", "Current stage")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("common.script", "Script")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("common.timeline", "Timeline")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("common.storyboard", "Storyboard")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("common.updatedAt", "Last updated")}</th>
                        <th className="px-5 py-3 text-right font-medium">{t("common.actions", "Actions")}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {summary.recent_episodes.map((episode) => (
                        <tr
                          key={episode.episode_id}
                          className={operatorTableRowClass}
                        >
                          <td className="w-[280px] px-5 py-4">
                            <div className="line-clamp-2 font-medium text-gray-950">
                              {episode.story_title}
                            </div>
                            <div className="mt-1 text-xs text-gray-500">
                              {t("common.episodeWithNumber", "Episode {number}",).replace("{number}", String(episode.episode_number))} · {episode.episode_title}
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <StatusPill tone={episode.timeline_ready ? "green" : "blue"}>
                              {episode.current_stage_label}
                            </StatusPill>
                          </td>
                          <ReadyCell ready={episode.script_ready} />
                          <ReadyCell ready={episode.timeline_ready} />
                          <ReadyCell ready={episode.storyboard_ready} />
                          <td className="px-4 py-4 text-xs text-gray-500">
                            {formatDateTime(episode.updated_at, {
                              month: "2-digit",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </td>
                          <td className="px-5 py-4 text-right">
                            <Link
                              href={episodeWorkspaceHref(episode.episode_business_id, {
                                tab: "timeline",
                                scriptId: episode.latest_script_id,
                              })}
                              className={operatorButtonClass("primary", "whitespace-nowrap")}
                            >
                              {t("common.openTimeline", "Open timeline")}
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </OperatorPanel>
            </OperatorMainCanvas>
          }
          inspector={
            <OperatorInspector title={t("workbench.inspectorTitle", "Tasks & audit")}>
              <div className="space-y-5">
                <div>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <h2 className="text-sm font-semibold text-gray-950">{t("workbench.taskQueue", "Task queue")}</h2>
                    <Link href="/tasks" className={operatorButtonClass("ghost")}>
                      {t("common.viewAll", "View all")}
                    </Link>
                  </div>
                  <div className="space-y-4">
                    {summary.task_queue.map((task) => (
                      <div key={task.id} className="space-y-2">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <div className="truncate text-sm font-medium text-gray-950">
                              {task.title}
                            </div>
                            <div className="mt-0.5 text-xs text-gray-500">
                              {task.task_type}
                            </div>
                          </div>
                          <StatusPill tone={taskStatusTone(task.status)}>
                            {taskStatusLabel(task.status)}
                          </StatusPill>
                        </div>
                        <ProgressBar value={task.progress} tone={taskTone(task)} />
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{task.progress}%</span>
                          {task.status === "failed" ? (
                            <Link href="/tasks" className="font-medium text-red-600">
                              {t("common.retry", "Retry")}
                            </Link>
                          ) : (
                            <span>
                              {formatDateTime(task.updated_at, {
                                month: "2-digit",
                                day: "2-digit",
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <h2 className="text-sm font-semibold">{t("workbench.auditTitle", "Run audit")}</h2>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-gray-600">
                    <AuditItem label={t("workbench.audit.scriptValidation", "Script validation")} value={t("common.pass", "Passed")} />
                    <AuditItem label={t("workbench.audit.storyboardValidation", "Storyboard validation")} value={t("common.pass", "Passed")} />
                    <AuditItem label={t("workbench.audit.durationValidation", "Duration validation")} value={t("common.reviewNeeded", "Needs review")} tone="amber" />
                    <AuditItem label={t("workbench.audit.sensitiveContent", "Sensitive content")} value={t("common.pass", "Passed")} />
                  </div>
                </div>
              </div>
            </OperatorInspector>
          }
        />
      ) : null}
    </OperatorShell>
  );
}
