"use client";

import { operatorButtonClass } from "@/components/shared";
import type {
  EpisodeCharacter,
  TimelineClipVideoReworkAction,
} from "@/utils/api/types";
import { ClipProductionActionIcon } from "./ClipProductionActionIcon";
import { ClipProductionActionShell } from "./ClipProductionActionShell";
import { CompactProductionDetails } from "./CompactProductionDetails";
import { VideoReferenceSelect } from "./TimelineClipProviderReworkCardSections";
import type { TimelineVideoReferenceChoice } from "./TimelineClipProviderReworkModel";
import { TimelineClipVideoBindingSummary } from "./TimelineClipVideoBindingSummary";
import { TimelineClipTaskStatusLine } from "./TimelineClipTaskStatusLine";
import type { TrackedClipGenerationTask } from "./useTimelineClipGenerationTaskTracker";
import type { VideoModelOption } from "./TimelineClipProviderReworkControlsTypes";
import {
  VIDEO_FIELD_CLASS,
  VIDEO_FIELD_GRID_CLASS,
  VIDEO_LABEL_CLASS,
  VideoActionSelect,
  VideoModelSelect,
  VideoRatioSelect,
  VideoResolutionSelect,
} from "./TimelineClipVideoReworkFields";

export function TimelineClipVideoReworkCard({
  action,
  prompt,
  model,
  duration,
  resolution,
  ratio,
  reason,
  videoReferenceChoice,
  storyboardPanelIndex,
  startEndReferenceAvailable,
  manualReferenceAvailable,
  episodeCharacters,
  selectedCharacterVirtualIpIds,
  selectedCharacterReferenceUrls,
  selectedEnvironmentReferenceUrls,
  videoModels,
  videoModelsLoading,
  submitting,
  submitError,
  canSubmit,
  disabledReason,
  videoTask,
  currentClipId,
  onActionChange,
  onPromptChange,
  onModelChange,
  onDurationChange,
  onResolutionChange,
  onRatioChange,
  onReasonChange,
  onVideoReferenceChoiceChange,
}: {
  action: TimelineClipVideoReworkAction;
  prompt: string;
  model: string;
  duration: string;
  resolution: string;
  ratio: string;
  reason: string;
  videoReferenceChoice: TimelineVideoReferenceChoice;
  storyboardPanelIndex?: number | null;
  startEndReferenceAvailable: boolean;
  manualReferenceAvailable: boolean;
  episodeCharacters: EpisodeCharacter[];
  selectedCharacterVirtualIpIds: number[];
  selectedCharacterReferenceUrls: string[];
  selectedEnvironmentReferenceUrls: string[];
  videoModels?: VideoModelOption[];
  videoModelsLoading?: boolean;
  submitting: boolean;
  submitError: string | null;
  canSubmit: boolean;
  disabledReason?: string | null;
  videoTask?: TrackedClipGenerationTask;
  currentClipId?: string | null;
  onActionChange: (value: TimelineClipVideoReworkAction) => void;
  onPromptChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onDurationChange: (value: string) => void;
  onResolutionChange: (value: string) => void;
  onRatioChange: (value: string) => void;
  onReasonChange: (value: string) => void;
  onVideoReferenceChoiceChange: (value: TimelineVideoReferenceChoice) => void;
}) {
  return (
    <ClipProductionActionShell
      kind="video"
      step="3"
      title="Clip Video"
      tone="primary"
    >
      <div
        data-clip-action-group="video"
        className="inline-flex w-full min-w-0 items-center gap-0 min-[720px]:w-auto"
      >
        <button
          type="submit"
          aria-label="Generate/Rework This Clip Video"
          title={disabledReason || "Generate/Rework This Clip Video"}
          disabled={!canSubmit}
          className={operatorButtonClass(
            "primary",
            "!h-8 min-w-0 flex-1 gap-1.5 whitespace-nowrap rounded-l-md rounded-r-none border border-blue-600 px-3 shadow-none min-[720px]:min-w-[15rem] min-[720px]:max-w-[17rem]",
          )}
        >
          <ClipProductionActionIcon kind="video" />
          <span>{submitting ? "Submitting..." : "Generate/Rework This Clip Video"}</span>
        </button>
        <CompactProductionDetails
          label="..."
          ariaLabel="Expand video bindings and parameters"
          tone="primary"
          attached
        >
          <div className="grid gap-2">
            <VideoActionSelect value={action} onChange={onActionChange} />
            <label className={VIDEO_LABEL_CLASS}>
              <span>Motion prompt override</span>
              <textarea
                aria-label="Motion prompt override"
                value={prompt}
                onChange={(event) => onPromptChange(event.target.value)}
                placeholder="Leave empty to use the timeline camera motion plan"
                rows={3}
                className={`resize-none ${VIDEO_FIELD_CLASS}`}
              />
              <span className="text-[11px] text-slate-400">
                Leave empty to use the timeline camera motion plan
              </span>
            </label>
            <div className={VIDEO_FIELD_GRID_CLASS}>
              <VideoModelSelect
                value={model}
                videoModels={videoModels}
                videoModelsLoading={videoModelsLoading}
                onChange={onModelChange}
              />
              <label className={VIDEO_LABEL_CLASS}>
                <span>Duration (seconds)</span>
                <input
                  type="number"
                  min={0.1}
                  step={0.1}
                  value={duration}
                  onChange={(event) => onDurationChange(event.target.value)}
                  placeholder="Use clip duration by default"
                  className={VIDEO_FIELD_CLASS}
                />
              </label>
            </div>
            <div className={VIDEO_FIELD_GRID_CLASS}>
              <VideoResolutionSelect
                value={resolution}
                onChange={onResolutionChange}
              />
              <VideoRatioSelect value={ratio} onChange={onRatioChange} />
            </div>
            <label className={VIDEO_LABEL_CLASS}>
              <span>Reason for rework</span>
              <input
                type="text"
                value={reason}
                onChange={(event) => onReasonChange(event.target.value)}
                placeholder="Optional; this will be recorded in the clip asset history"
                className={VIDEO_FIELD_CLASS}
              />
            </label>
          </div>
        </CompactProductionDetails>
      </div>
      <div
        data-clip-reference-controls="video"
        className="mt-2 grid min-w-0 gap-2 rounded-md border border-blue-100 bg-white p-2"
      >
        <TimelineClipVideoBindingSummary
          episodeCharacters={episodeCharacters}
          selectedCharacterVirtualIpIds={selectedCharacterVirtualIpIds}
          selectedCharacterReferenceUrls={selectedCharacterReferenceUrls}
          selectedEnvironmentReferenceUrls={selectedEnvironmentReferenceUrls}
        />
        <VideoReferenceSelect
          value={videoReferenceChoice}
          storyboardPanelIndex={storyboardPanelIndex}
          startEndAvailable={startEndReferenceAvailable}
          manualRefsAvailable={manualReferenceAvailable}
          onChange={onVideoReferenceChoiceChange}
        />
      </div>
      <div className="grid gap-2">
        {!canSubmit && disabledReason ? (
          <div
            data-clip-video-generation-gate="blocked"
            className="rounded-md bg-amber-50 px-2 py-1.5 text-xs text-amber-700"
          >
            {disabledReason}
          </div>
        ) : null}
        {submitError ? (
          <div className="text-xs text-red-600">{submitError}</div>
        ) : null}
        <TimelineClipTaskStatusLine
          kind="video"
          task={videoTask}
          currentClipId={currentClipId ?? null}
        />
      </div>
    </ClipProductionActionShell>
  );
}
