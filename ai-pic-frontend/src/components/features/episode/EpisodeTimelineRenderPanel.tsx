"use client";

import { ProgressBar, operatorButtonClass } from "@/components/shared";
import type {
  TimelineRenderJobResponse,
  TimelineRenderType,
} from "@/utils/api/types";
import type { TimelineRenderReadiness } from "./EpisodeTimelineRenderModel";
import {
  MissingClipsDetails,
  TimelineRenderActionButtons,
  TimelineRenderStatusHeader,
  renderJobFailureText,
  renderJobHistoryClass,
  renderJobMissingClipCount,
  renderJobOutputUrl,
  renderStatusLabel,
  renderTypeLabel,
} from "./EpisodeTimelineRenderPanelParts";

export function TimelineRenderPanel({
  readiness,
  latestJob,
  renderJobs,
  loading,
  busy,
  error,
  onQueueRender,
  onRetryRender,
  onRestartRenderJob,
}: {
  readiness: TimelineRenderReadiness;
  latestJob: TimelineRenderJobResponse | null;
  renderJobs: TimelineRenderJobResponse[];
  loading: boolean;
  busy: boolean;
  error: string | null;
  onQueueRender: (renderType: TimelineRenderType) => void;
  onRetryRender: (renderType: TimelineRenderType) => void;
  onRestartRenderJob: (jobId: number) => void;
}) {
  const outputUrl = renderJobOutputUrl(latestJob);
  const missingFromJob = renderJobMissingClipCount(latestJob);
  const canRender = readiness.ready && !busy;
  const finalButtonVariant = canRender ? "primary" : "secondary";
  const renderInFlight =
    latestJob?.status === "queued" || latestJob?.status === "running";
  const blockedByMissingClips =
    !readiness.ready && readiness.missingClips.length > 0 && !latestJob;
  const readyClipCount = Math.max(
    0,
    readiness.videoClipCount - readiness.missingClips.length,
  );
  const readyPercent = readiness.videoClipCount
    ? Math.round((readyClipCount / readiness.videoClipCount) * 100)
    : 0;
  if (blockedByMissingClips) {
    return (
      <details data-timeline-render-panel="collapsed" className="px-2 py-1">
        <summary
          data-timeline-render-summary="inline"
          data-timeline-render-summary-layout="clustered-status-strip"
          className="flex min-h-7 w-full max-w-full cursor-pointer list-none items-center gap-2 px-2 py-0.5 marker:hidden [&::-webkit-details-marker]:hidden"
        >
          <div className="min-w-0 shrink">
            <TimelineRenderStatusHeader
              readiness={readiness}
              latestJob={latestJob}
              loading={loading}
              error={error}
            />
          </div>
          <span
            data-timeline-render-readiness-meter="inline-count"
            title={`${readyClipCount}/${readiness.videoClipCount} clips ready`}
            className="ml-1 inline-flex items-center gap-1.5 whitespace-nowrap text-[11px] font-semibold text-slate-600"
          >
            <span
              data-timeline-render-readiness-track="true"
              aria-hidden="true"
              className="h-1.5 w-12 overflow-hidden rounded-full bg-slate-200"
            >
              <span
                data-timeline-render-readiness-fill="true"
                className="block h-full rounded-full bg-amber-400"
                style={{ width: `${readyPercent}%` }}
              />
            </span>
            <span>
              {readyClipCount}/{readiness.videoClipCount} ready
            </span>
          </span>
          <span
            data-timeline-render-missing-action="inline-link"
            title="View missing clips"
            className="inline-flex h-6 items-center whitespace-nowrap px-1 text-[11px] font-semibold text-slate-600 hover:text-slate-950"
          >
            View
          </span>
        </summary>
        <div className="mt-2 border-t border-gray-100 pt-2">
          <MissingClipsDetails missingClips={readiness.missingClips} />
        </div>
      </details>
    );
  }

  return (
    <div data-timeline-render-panel="expanded" className="px-2.5 py-1.5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <TimelineRenderStatusHeader
          readiness={readiness}
          latestJob={latestJob}
          loading={loading}
          error={error}
        />
        <TimelineRenderActionButtons
          canRender={canRender}
          finalButtonVariant={finalButtonVariant}
          latestJob={latestJob}
          readiness={readiness}
          busy={busy}
          onQueueRender={onQueueRender}
          onRetryRender={onRetryRender}
        />
      </div>

      {latestJob ? (
        <div className="mt-3">
          <ProgressBar
            value={latestJob.progress || 0}
            tone={latestJob.status === "failed" ? "red" : "blue"}
          />
        </div>
      ) : null}

      {!readiness.ready && readiness.missingClips.length > 0 ? (
        <MissingClipsDetails missingClips={readiness.missingClips} />
      ) : null}

      {latestJob?.status === "failed" ? (
        <div className="mt-3 text-xs text-red-700">
          Failure reason: {renderJobFailureText(latestJob, missingFromJob)}
        </div>
      ) : null}

      {outputUrl && latestJob?.status === "succeeded" ? (
        <div className="mt-3 grid gap-3 rounded-md border border-green-200 bg-green-50 p-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <video
            aria-label="Play rendered final cut"
            className="w-full rounded-md border border-green-200 bg-black"
            controls
            preload="none"
            src={outputUrl}
          />
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-medium text-green-800">
              {renderTypeLabel(latestJob.render_type)} is ready
            </span>
            <a
              href={outputUrl}
              download
              target="_blank"
              rel="noreferrer"
              className={operatorButtonClass("primary")}
            >
              Download final cut
            </a>
            <a
              href={outputUrl}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-medium text-blue-700 hover:text-blue-900"
            >
              Open in new tab
            </a>
          </div>
        </div>
      ) : null}

      {renderInFlight ? (
        <div className="mt-3 text-xs text-gray-500">
          Render task #{latestJob?.id} is in progress
        </div>
      ) : null}

      {renderJobs.length > 1 ? (
        <details className="mt-3">
          <summary className="cursor-pointer text-[11px] font-medium text-slate-500 hover:text-slate-800">
            Job history ({renderJobs.length})
          </summary>
          <ul className="mt-1.5 space-y-1">
            {renderJobs.map((job) => (
              <li
                key={job.id}
                className="flex items-center gap-2 text-[11px] text-slate-600"
              >
                <span className="font-medium">#{job.id}</span>
                <span>{renderTypeLabel(job.render_type)}</span>
                <span
                  className={`rounded-sm border px-1 py-0.5 ${renderJobHistoryClass(job.status)}`}
                >
                  {renderStatusLabel(job.status)}
                </span>
                {(job.status === "failed" || job.status === "cancelled") ? (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => onRestartRenderJob(job.id)}
                    className="ml-auto text-[11px] font-medium text-blue-600 hover:text-blue-900 disabled:opacity-50"
                  >
                    Restart
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </div>
  );
}
