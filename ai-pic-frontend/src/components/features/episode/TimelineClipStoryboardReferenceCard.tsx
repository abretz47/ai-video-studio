"use client";

import { operatorButtonClass, operatorSelectClass } from "@/components/shared";
import type {
  EpisodeCharacter,
  TimelineClipStoryboardStyle,
} from "@/utils/api/types";
import { ClipProductionActionIcon } from "./ClipProductionActionIcon";
import { ClipProductionActionShell } from "./ClipProductionActionShell";
import { CompactProductionDetails } from "./CompactProductionDetails";
import { StoryboardCharacterIpSelector } from "./TimelineClipStoryboardCharacterIpSelector";
import { StoryboardReferenceImageSelectors } from "./TimelineClipStoryboardReferenceImages";
import { TimelineClipTaskStatusLine } from "./TimelineClipTaskStatusLine";
import type { ImageModelOption } from "./TimelineClipProviderReworkControlsTypes";
import type { TimelineClipStoryboardReferenceSelection } from "./useTimelineClipStoryboardReferenceSelection";
import type { TrackedClipGenerationTask } from "./useTimelineClipGenerationTaskTracker";

const FIELD_GRID_CLASS =
  "grid gap-2 min-[760px]:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1.15fr)]";

export function StoryboardReferenceCard({
  storyboardModel,
  storyboardStyle,
  storyboardPanelCount,
  storyboardSheetUrl,
  episodeCharacters,
  episodeCharactersLoading,
  episodeCharactersError,
  onNavigateToCharacters,
  selectedCharacterVirtualIpIds,
  storyboardReferenceSelection,
  generatingStoryboard,
  canGenerateStoryboard,
  storyboardTask,
  currentClipId,
  imageModels,
  imageModelsLoading,
  onStoryboardModelChange,
  onStoryboardStyleChange,
  onStoryboardPanelCountChange,
  onCharacterVirtualIpToggle,
  onGenerateStoryboard,
}: {
  storyboardModel: string;
  storyboardStyle: TimelineClipStoryboardStyle;
  storyboardPanelCount: string;
  storyboardSheetUrl?: string | null;
  episodeCharacters: EpisodeCharacter[];
  episodeCharactersLoading: boolean;
  episodeCharactersError: string | null;
  onNavigateToCharacters?: () => void;
  selectedCharacterVirtualIpIds: number[];
  storyboardReferenceSelection: TimelineClipStoryboardReferenceSelection;
  generatingStoryboard: boolean;
  canGenerateStoryboard: boolean;
  storyboardTask?: TrackedClipGenerationTask;
  currentClipId?: string | null;
  imageModels?: ImageModelOption[];
  imageModelsLoading?: boolean;
  onStoryboardModelChange: (value: string) => void;
  onStoryboardStyleChange: (value: TimelineClipStoryboardStyle) => void;
  onStoryboardPanelCountChange: (value: string) => void;
  onCharacterVirtualIpToggle: (virtualIpId: number, checked: boolean) => void;
  onGenerateStoryboard: () => void;
}) {
  return (
    <ClipProductionActionShell kind="storyboard" step="1" title="Clip Storyboard">
      <div
        data-clip-action-group="storyboard"
        className="inline-flex w-full min-w-0 items-center gap-0 min-[720px]:w-auto"
      >
        <button
          type="button"
          aria-label="Generate Clip Storyboard"
          disabled={!canGenerateStoryboard}
          className={operatorButtonClass(
            "secondary",
            "!h-8 min-w-0 flex-1 gap-1.5 whitespace-nowrap rounded-l-md rounded-r-none border border-slate-200 bg-white px-2.5 text-slate-700 shadow-none hover:bg-slate-50 min-[720px]:min-w-[9.5rem]",
          )}
          onClick={onGenerateStoryboard}
          title="Generate Clip Storyboard"
        >
          <ClipProductionActionIcon kind="storyboard" />
          <span>{generatingStoryboard ? "Submitting..." : "Generate Clip Storyboard"}</span>
        </button>
        <CompactProductionDetails
          label="..."
          ariaLabel="Expand storyboard parameters and references"
          align="left"
          attached
        >
          <div className={FIELD_GRID_CLASS}>
            <label className="grid gap-1 text-xs text-gray-700">
              <span>Visual Style</span>
              <select
                aria-label="Visual Style"
                value={storyboardStyle}
                onChange={(event) =>
                  onStoryboardStyleChange(
                    event.target.value as TimelineClipStoryboardStyle,
                  )
                }
                className={operatorSelectClass("w-full")}
              >
                <option value="live_action">Live Action</option>
                <option value="3d_cartoon">3D Cartoon</option>
                <option value="2d_cartoon">2D Cartoon</option>
              </select>
            </label>
            <label className="grid gap-1 text-xs text-gray-700">
              <span>Storyboard Panels</span>
              <select
                aria-label="Storyboard panel count"
                value={storyboardPanelCount}
                onChange={(event) =>
                  onStoryboardPanelCountChange(event.target.value)
                }
                className={operatorSelectClass("w-full")}
              >
                {["2", "3", "4", "6", "8", "9"].map((count) => (
                  <option key={count} value={count}>
                    {count} panels
                  </option>
                ))}
              </select>
            </label>
            <StoryboardImageModelSelect
              value={storyboardModel}
              imageModels={imageModels}
              imageModelsLoading={imageModelsLoading}
              onChange={onStoryboardModelChange}
            />
          </div>
        </CompactProductionDetails>
      </div>
      <div
        data-clip-reference-controls="storyboard"
        className="mt-2 grid min-w-0 gap-2 rounded-md border border-slate-200 bg-white p-2"
      >
        <StoryboardCharacterIpSelector
          characters={episodeCharacters}
          loading={episodeCharactersLoading}
          error={episodeCharactersError}
          onNavigateToCharacters={onNavigateToCharacters}
          selectedVirtualIpIds={selectedCharacterVirtualIpIds}
          onToggle={onCharacterVirtualIpToggle}
        />
        <StoryboardReferenceImageSelectors
          episodeCharacters={episodeCharacters}
          characterImageOptions={
            storyboardReferenceSelection.characterImageOptions
          }
          environmentImageOptions={
            storyboardReferenceSelection.environmentImageOptions
          }
          selectedVirtualIpIds={selectedCharacterVirtualIpIds}
          selectedCharacterUrls={
            storyboardReferenceSelection.selectedStoryboardCharacterReferenceImages
          }
          selectedEnvironmentUrls={
            storyboardReferenceSelection.selectedStoryboardEnvironmentReferenceImages
          }
          characterImagesLoading={
            storyboardReferenceSelection.characterImagesLoading
          }
          characterImagesError={
            storyboardReferenceSelection.characterImagesError
          }
          onCharacterImagesReplace={
            storyboardReferenceSelection.handleStoryboardCharacterReferenceImagesReplace
          }
          onEnvironmentImagesReplace={
            storyboardReferenceSelection.handleStoryboardEnvironmentReferenceImagesReplace
          }
        />
      </div>
      <TimelineClipTaskStatusLine
        kind="storyboard"
        task={storyboardTask}
        currentClipId={currentClipId ?? null}
      />
      {storyboardSheetUrl ? (
        <a
          href={storyboardSheetUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-3 block overflow-hidden rounded-md border border-gray-200 bg-gray-50"
          title="Click to view full size"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={storyboardSheetUrl}
            alt="Clip StoryboardPreview"
            className="max-h-72 w-full object-contain"
          />
          <div className="border-t border-gray-200 px-2 py-1 text-center text-[11px] text-gray-500">
            Click to view full size
          </div>
        </a>
      ) : null}
    </ClipProductionActionShell>
  );
}

function StoryboardImageModelSelect({
  value,
  imageModels,
  imageModelsLoading,
  onChange,
}: {
  value: string;
  imageModels?: ImageModelOption[];
  imageModelsLoading?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-1 text-xs text-gray-700">
      <span>Image Generation Model</span>
      <select
        aria-label="StoryboardImage Generation Model"
        value={value}
        disabled={imageModelsLoading}
        onChange={(event) => onChange(event.target.value)}
        className={operatorSelectClass("w-full")}
      >
        <option value="">Automatically select model</option>
        {(imageModels || []).map((option) => {
          const optionValue = modelOptionValue(option);
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

function modelOptionValue(option: ImageModelOption) {
  const providerScopedId =
    option.provider && option.id ? `${option.provider}:${option.id}` : option.id;
  return option.model_id || providerScopedId || option.name || "";
}
