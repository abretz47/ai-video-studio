"use client";

import type { TimelineItem } from "@/components/features";
import type { TimelineClipAssetResponse } from "@/utils/api/types";
import { TimelineClipProviderReworkControls } from "./TimelineClipProviderReworkControls";
import { TimelineClipReworkControls } from "./TimelineClipReworkControls";

export function AssetOperationDetails({
  clipId,
  item,
  timelineId,
  timelineVersion,
  onReworkRecorded,
  onNotify,
  showProviderControls,
}: {
  clipId: string | null;
  item: TimelineItem | null;
  timelineId?: number | string | null;
  timelineVersion?: number | null;
  onReworkRecorded?: () => void | Promise<void>;
  onNotify?: (
    message: string,
    variant: "success" | "error" | "warning" | "info",
  ) => void;
  showProviderControls: boolean;
}) {
  return (
    <details className="mt-2 border-t border-gray-100 pt-2">
      <summary className="cursor-pointer text-xs font-medium text-gray-600 hover:text-gray-950">
        Asset Actions
      </summary>
      {clipId ? (
        <div className="mt-2 truncate font-mono text-[11px] text-gray-500">
          Clip ID：{clipId}
        </div>
      ) : null}
      <TimelineClipReworkControls
        timelineId={timelineId}
        timelineVersion={timelineVersion}
        clipId={clipId}
        onRecorded={onReworkRecorded}
        onNotify={onNotify}
      />
      {showProviderControls ? (
        <TimelineClipProviderReworkControls
          timelineId={timelineId}
          timelineVersion={timelineVersion}
          clipId={clipId}
          item={item}
          onQueued={onReworkRecorded}
          onNotify={onNotify}
        />
      ) : null}
    </details>
  );
}

export function ClipAssetAuditRow({
  asset,
}: {
  asset: TimelineClipAssetResponse;
}) {
  const locator =
    asset.media_asset?.file_url ||
    asset.media_asset?.object_key ||
    asset.media_asset?.file_path ||
    `media_asset_id=${asset.media_asset_id}`;
  return (
    <div className="rounded border border-gray-100 px-2 py-2 text-xs">
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-gray-900">
          {assetRoleLabel(asset.asset_role)}
        </span>
        <span className="text-gray-500">#{asset.id}</span>
      </div>
      <div className="mt-1 truncate text-gray-600">{locator}</div>
      <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-gray-500">
        <span>{sourceLabel(asset.source)}</span>
        {asset.replacement_of_id ? (
          <span>Replacement #{asset.replacement_of_id}</span>
        ) : null}
        {asset.render_job_id ? <span>Render #{asset.render_job_id}</span> : null}
      </div>
    </div>
  );
}

function assetRoleLabel(role: string) {
  const labels: Record<string, string> = {
    source_audio: "Source Audio",
    start_frame: "Start Frame",
    end_frame: "End Frame",
    storyboard_image: "Storyboard Image",
    storyboard_video: "Storyboard Video",
    clip_storyboard_sheet: "Clip Storyboard",
    storyboard_grid_sheet: "Legacy Storyboard Grid",
    generated_video: "Generated Video",
    render_output: "Render Output",
  };
  return labels[role] || role;
}

function sourceLabel(source?: string | null) {
  if (source === "operator_rework") return "Manual Rework";
  if (source === "render_job") return "Render Task";
  if (source === "timeline_spec") return "Timeline Spec";
  return source || "Unknown source";
}
