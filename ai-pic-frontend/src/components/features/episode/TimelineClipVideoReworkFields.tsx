"use client";

import { operatorSelectClass } from "@/components/shared";
import type { TimelineClipVideoReworkAction } from "@/utils/api/types";
import type { VideoModelOption } from "./TimelineClipProviderReworkControlsTypes";

const VIDEO_ACTION_OPTIONS: Array<{
  value: TimelineClipVideoReworkAction;
  label: string;
}> = [
  { value: "re_cut", label: "Re-cut" },
  { value: "re_render", label: "Re-render" },
];

const RESOLUTION_OPTIONS = ["720p", "1080p"];
const RATIO_OPTIONS = ["9:16", "16:9", "1:1", "4:3", "3:4"];

export const VIDEO_FIELD_CLASS = [
  "rounded-md border border-gray-200 px-2 py-1.5 text-xs",
  "outline-none focus:border-gray-400",
].join(" ");
export const VIDEO_FIELD_GRID_CLASS =
  "grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-2";
export const VIDEO_LABEL_CLASS = "grid gap-1 text-xs text-gray-700";

export function VideoActionSelect({
  value,
  onChange,
}: {
  value: TimelineClipVideoReworkAction;
  onChange: (value: TimelineClipVideoReworkAction) => void;
}) {
  return (
    <label className={VIDEO_LABEL_CLASS}>
      <span>Rework Action</span>
      <select
        aria-label="Rework Action"
        value={value}
        onChange={(event) =>
          onChange(event.target.value as TimelineClipVideoReworkAction)
        }
        className={operatorSelectClass("w-full")}
      >
        {VIDEO_ACTION_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <span className="text-[11px] text-gray-400">
        Both options regenerate the clip video; they only differ as action
        categories in the asset audit trail.
      </span>
    </label>
  );
}

export function VideoModelSelect({
  value,
  videoModels,
  videoModelsLoading,
  onChange,
}: {
  value: string;
  videoModels?: VideoModelOption[];
  videoModelsLoading?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className={VIDEO_LABEL_CLASS}>
      <span>Video Model</span>
      <select
        aria-label="Video Model"
        value={value}
        disabled={videoModelsLoading}
        onChange={(event) => onChange(event.target.value)}
        className={operatorSelectClass("w-full")}
      >
        <option value="">Automatically select model</option>
        {(videoModels || []).map((option) => {
          const providerScopedId =
            option.provider && option.id
              ? `${option.provider}:${option.id}`
              : option.id;
          const optionValue =
            option.model_id || providerScopedId || option.name || "";
          if (!optionValue) return null;
          return (
            <option key={optionValue} value={optionValue}>
              {option.name || option.model_id || option.id}
            </option>
          );
        })}
      </select>
    </label>
  );
}

export function VideoResolutionSelect({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className={VIDEO_LABEL_CLASS}>
      <span>Resolution</span>
      <select
        aria-label="Resolution"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={operatorSelectClass("w-full")}
      >
        {RESOLUTION_OPTIONS.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export function VideoRatioSelect({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className={VIDEO_LABEL_CLASS}>
      <span>Aspect Ratio</span>
      <select
        aria-label="Aspect Ratio"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={operatorSelectClass("w-full")}
      >
        <option value="">Auto</option>
        {RATIO_OPTIONS.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
