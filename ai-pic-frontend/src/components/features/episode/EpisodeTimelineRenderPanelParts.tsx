"use client";

import { operatorButtonClass } from "@/components/shared";
import { getString } from "@/hooks/useEpisodeDetail";
import type {
  TimelineRenderJobResponse,
  TimelineRenderType,
} from "@/utils/api/types";
import type { TimelineRenderReadiness } from "./EpisodeTimelineRenderModel";

export function TimelineRenderStatusHeader({
  readiness,
  latestJob,
  loading,
  error,
}: {
  readiness: TimelineRenderReadiness;
  latestJob: TimelineRenderJobResponse | null;
  loading: boolean;
  error: string | null;
}) {
  const readinessLabel = readiness.ready
    ? `${readiness.videoClipCount} clips ready to render`
    : readiness.videoClipCount
    ? `${readiness.missingClips.length} missing`
    : "No video track";
  const readinessTextClass = readiness.ready
    ? "text-emerald-700"
    : "text-slate-500";

  return (
    <div
      data-timeline-render-status-header="compact"
      className="flex min-w-0 flex-wrap items-center gap-2"
    >
      <span
        data-timeline-render-label="final-output"
        title="Render/export status"
        className="text-[11px] font-bold text-slate-900"
      >
        Final Cut
      </span>
      <span className="sr-only">Render/export</span>
      <span
        data-timeline-render-readiness={readiness.ready ? "ready" : "blocked"}
        className={`inline-flex items-center gap-1 text-[11px] font-semibold ${readinessTextClass}`}
      >
        <span
          aria-hidden="true"
          className={`h-1.5 w-1.5 rounded-full ${
            readiness.ready ? "bg-emerald-500" : "bg-amber-500"
          }`}
        />
        {readinessLabel}
      </span>
      {latestJob ? (
        <span
          className={`rounded-sm border px-1.5 py-0.5 text-[11px] font-medium ${renderJobClass(
            latestJob.status,
          )}`}
        >
          {renderTypeLabel(latestJob.render_type)} ·{" "}
          {renderStatusLabel(latestJob.status)}
        </span>
      ) : null}
      {loading ? (
        <span className="text-xs text-gray-500">Refreshing...</span>
      ) : null}
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </div>
  );
}

export function TimelineRenderActionButtons({
  canRender,
  finalButtonVariant,
  latestJob,
  readiness,
  busy,
  onQueueRender,
  onRetryRender,
}: {
  canRender: boolean;
  finalButtonVariant: "primary" | "secondary";
  latestJob: TimelineRenderJobResponse | null;
  readiness: TimelineRenderReadiness;
  busy: boolean;
  onQueueRender: (renderType: TimelineRenderType) => void;
  onRetryRender: (renderType: TimelineRenderType) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <button
        type="button"
        onClick={() => onQueueRender("proxy")}
        disabled={!canRender}
        className={operatorButtonClass("secondary")}
      >
        Render Preview
      </button>
      <button
        type="button"
        onClick={() => onQueueRender("final")}
        disabled={!canRender}
        className={operatorButtonClass(finalButtonVariant)}
      >
        Export Final Cut
      </button>
      {latestJob?.status === "failed" ? (
        <button
          type="button"
          onClick={() =>
            onRetryRender(latestJob.render_type as TimelineRenderType)
          }
          disabled={!readiness.ready || busy}
          className={operatorButtonClass("secondary")}
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export function MissingClipsDetails({
  missingClips,
}: {
  missingClips: TimelineRenderReadiness["missingClips"];
}) {
  const generating = missingClips.filter(
    (clip) => clip.reason === "generating",
  );
  const missing = missingClips.filter((clip) => clip.reason !== "generating");
  const joinIds = (clips: typeof missingClips) =>
    clips
      .slice(0, 4)
      .map((clip) => clip.clipId)
      .join("、") + (clips.length > 4 ? " ..." : "");

  return (
    <details className="mt-2 rounded-md border border-amber-100 bg-amber-50/50 px-2 py-1.5 text-xs">
      <summary className="cursor-pointer font-medium text-amber-800">
        Missing Clips ({missingClips.length})
      </summary>
      <div className="mt-2 space-y-1">
        {generating.length > 0 ? (
          <div className="text-blue-700">
            Generating clips (renderable automatically when done): {joinIds(generating)}
          </div>
        ) : null}
        {missing.length > 0 ? (
          <div className="text-amber-800">Missing clips: {joinIds(missing)}</div>
        ) : null}
      </div>
    </details>
  );
}

export function renderJobOutputUrl(job: TimelineRenderJobResponse | null) {
  return job?.output_asset?.file_url || job?.output_asset?.file_path || null;
}

export function renderJobMissingClipCount(
  job: TimelineRenderJobResponse | null,
) {
  const missing = job?.log?.missing_clips;
  return Array.isArray(missing) ? missing.length : 0;
}

export function renderJobFailureText(
  job: TimelineRenderJobResponse,
  missingClipCount: number,
) {
  const code = getString(job.log?.code);
  if (code === "missing_clip_videos") {
    return `Missing ${missingClipCount} video clips`;
  }
  if (code === "no_video_clips") return "The timeline has no renderable video track";
  if (code === "stale_timeline_version") return "The timeline version has changed";
  return code || "Render failed";
}

export function renderTypeLabel(value: string) {
  if (value === "proxy") return "Preview";
  if (value === "final") return "Final Cut";
  if (value === "export") return "Export";
  return value;
}

export function renderStatusLabel(value: string) {
  if (value === "queued") return "Queued";
  if (value === "running") return "Rendering";
  if (value === "succeeded") return "Completed";
  if (value === "failed") return "Failed";
  if (value === "cancelled") return "Cancelled";
  return value;
}

function renderJobClass(status: string) {
  if (status === "succeeded") return "border-emerald-200 text-emerald-700";
  if (status === "failed" || status === "cancelled") {
    return "border-red-200 text-red-700";
  }
  if (status === "running") return "border-amber-200 text-amber-700";
  if (status === "queued") return "border-blue-200 text-blue-700";
  return "border-gray-200 text-gray-600";
}

export function renderJobHistoryClass(status: string) {
  if (status === "succeeded") return "border-emerald-200 text-emerald-700";
  if (status === "failed" || status === "cancelled") return "border-red-200 text-red-700";
  if (status === "running") return "border-amber-200 text-amber-700";
  if (status === "queued") return "border-blue-200 text-blue-700";
  return "border-gray-200 text-gray-600";
}
