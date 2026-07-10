"use client";

import { operatorSelectClass } from "@/components/shared";
import type { TimelineVideoReferenceChoice } from "./TimelineClipProviderReworkModel";

const VIDEO_REFERENCE_HINTS: Record<TimelineVideoReferenceChoice, string> = {
  start_end:
    "Use this clip’s start/end frame images to drive video generation. Generate the start/end frames first.",
  clip_storyboard_panel:
    "Use this clip’s storyboard panel as the reference image for video generation.",
  storyboard_grid_panel:
    "Use the legacy full-timeline storyboard grid panel as the reference image.",
  manual_refs:
    "Use only the images from the “Additional reference image URLs” above as references.",
};

export function VideoReferenceSelect({
  value,
  storyboardPanelIndex,
  startEndAvailable,
  manualRefsAvailable,
  onChange,
}: {
  value: TimelineVideoReferenceChoice;
  storyboardPanelIndex?: number | null;
  startEndAvailable: boolean;
  manualRefsAvailable: boolean;
  onChange: (value: TimelineVideoReferenceChoice) => void;
}) {
  return (
    <label className="grid gap-1 text-xs text-gray-700">
      <span>Video reference source</span>
      <select
        aria-label="Video reference source"
        value={value}
        onChange={(event) =>
          onChange(event.target.value as TimelineVideoReferenceChoice)
        }
        className={operatorSelectClass("w-full")}
      >
        <option value="start_end" disabled={!startEndAvailable}>
          {startEndAvailable ? "Start/end frame" : "Start/end frame (generate first)"}
        </option>
        <option value="clip_storyboard_panel" disabled={!storyboardPanelIndex}>
          {storyboardPanelIndex
            ? `Storyboard Panel ${storyboardPanelIndex}`
            : "Storyboard Panel (generate the clip storyboard first)"}
        </option>
        <option value="manual_refs" disabled={!manualRefsAvailable}>
          Manual/shared reference images
        </option>
      </select>
      <span className="text-[11px] text-gray-400">
        {VIDEO_REFERENCE_HINTS[value]}
      </span>
    </label>
  );
}
