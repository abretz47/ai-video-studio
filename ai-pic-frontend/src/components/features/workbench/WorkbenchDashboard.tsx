"use client";

import Link from "next/link";
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

const formatDateTime = (value: string) =>
  new Date(value).toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });

const taskStatusLabel = (status: string) => {
  if (status === "processing") return "Generating";
  if (status === "pending") return "Queued";
  if (status === "completed") return "Completed";
  if (status === "failed") return "Failed";
  if (status === "cancelled") return "Cancelled";
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
      title="IP Production Workbench"
      subtitle="Continue stories, episodes, and tasks around each IP"
      breadcrumb={["IP Center", "Production Workbench"]}
    >
      {loading ? (
        <OperatorState title="Loading workbench data..." />
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
              Retry
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
                    IP / Environment Production Status
                  </h2>
                  <p className="mt-1 text-xs text-gray-500">
                    Current production moves forward around IPs, stories, episodes, and environment assets; new content should start from an IP project first.
                  </p>
                </div>
                <Link href="/virtual-ip" className={operatorButtonClass("primary")}>
                  Open IP Project
                </Link>
              </div>
            </OperatorPanel>

            <div className="grid gap-3 md:grid-cols-4">
              <MetricCard label="Pending Today" value={summary.metrics.pending_tasks} />
              <MetricCard label="Generating" value={summary.metrics.running_tasks} />
              <MetricCard label="Failed Tasks" value={summary.metrics.failed_tasks} tone="red" />
              <MetricCard
                label="Ready to Continue"
                value={summary.metrics.continuable_episodes}
                tone="green"
              />
            </div>

            <OperatorPanel>
              <OperatorSectionHeader
                title="Continue Production"
                subtitle="Move forward from existing content to the episode timeline"
                action={
                  <Link href="/stories" className={operatorButtonClass("secondary")}>
                    View All
                  </Link>
                }
              />
              <div className="overflow-x-auto">
                <table className={`${operatorTableClass} min-w-[1080px]`}>
                  <thead className={operatorTableHeadClass}>
                    <tr>
                      <th className="w-[280px] px-5 py-3 text-left font-medium">
                        IP / Story / Episode
                      </th>
                      <th className="px-4 py-3 text-left font-medium">Current Stage</th>
                      <th className="px-4 py-3 text-left font-medium">Script</th>
                      <th className="px-4 py-3 text-left font-medium">Timeline</th>
                      <th className="px-4 py-3 text-left font-medium">Storyboard</th>
                      <th className="px-4 py-3 text-left font-medium">Last Updated</th>
                      <th className="px-5 py-3 text-right font-medium">Actions</th>
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
                            Episode {episode.episode_number} · {episode.episode_title}
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
                          {formatDateTime(episode.updated_at)}
                        </td>
                        <td className="px-5 py-4 text-right">
                          <Link
                            href={episodeWorkspaceHref(episode.episode_business_id, {
                              tab: "timeline",
                              scriptId: episode.latest_script_id,
                            })}
                            className={operatorButtonClass("primary", "whitespace-nowrap")}
                          >
                            Open Timeline
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
            <OperatorInspector title="Tasks & Audit">
              <div className="space-y-5">
                <div>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <h2 className="text-sm font-semibold text-gray-950">Task Queue</h2>
                    <Link href="/tasks" className={operatorButtonClass("ghost")}>
                      View All
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
                          Retry
                        </Link>
                      ) : (
                        <span>{formatDateTime(task.updated_at)}</span>
                      )}
                    </div>
                  </div>
                ))}
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <h2 className="text-sm font-semibold">Run Audit</h2>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-gray-600">
                    <AuditItem label="Script Check" value="Passed" />
                    <AuditItem label="Storyboard Check" value="Passed" />
                    <AuditItem label="Duration Check" value="Pending Review" tone="amber" />
                    <AuditItem label="Sensitive Content" value="Passed" />
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
