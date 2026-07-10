"use client";

import { useEffect, useState } from "react";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
} from "@/components/shared";
import { firstTimelineVideoClipId } from "@/hooks/episode/timelineClipUtils";
import type {
  NormalizedScene,
  TimelineResolvedVideoListResponse,
  TimelineResponse,
} from "@/utils/api/types";
import { episodeWorkspaceHref } from "@/utils/routes";
import {
  buildStoryboardSupportFrames,
  buildStoryboardSupportSummary,
} from "./WorkspaceStoryboardSupportModel";
import { WorkspaceStoryboardActions } from "./WorkspaceStoryboardActions";
import { WorkspaceStoryboardClipManagement } from "./WorkspaceStoryboardClipManagement";
import { StoryboardSupportFrameRow } from "./WorkspaceStoryboardFrameRow";
import { WorkspaceStoryboardTimelinePanel } from "./WorkspaceStoryboardTimelinePanel";
import { buildStoryboardTimelineOverview } from "./WorkspaceStoryboardTimelineOverviewModel";

type ShowAlert = (options: {
  message: string;
  variant: "info" | "success" | "warning" | "error";
}) => void;

interface WorkspaceStoryboardTabContentProps {
  episodeKey?: string;
  selectedScriptId?: number | null;
  hasStoryboard?: boolean;
  selectedAudioTimeline?: Record<string, unknown> | null;
  selectedTimelineSpec?: TimelineResponse | null;
  onTimelineUpdated?: (timeline: TimelineResponse) => void;
  resolvedVideos?: TimelineResolvedVideoListResponse | null;
  selectedStoryboard: Record<string, unknown> | null;
  normalizedScenes: NormalizedScene[];
  showAlert?: ShowAlert;
}

export function WorkspaceStoryboardTabContent({
  episodeKey = "",
  selectedScriptId,
  hasStoryboard,
  selectedAudioTimeline,
  selectedTimelineSpec,
  onTimelineUpdated,
  resolvedVideos,
  selectedStoryboard,
  normalizedScenes,
  showAlert,
}: WorkspaceStoryboardTabContentProps) {
  const [localTimelineSpec, setLocalTimelineSpec] =
    useState<TimelineResponse | null>(selectedTimelineSpec ?? null);
  useEffect(() => {
    setLocalTimelineSpec(selectedTimelineSpec ?? null);
  }, [selectedTimelineSpec]);
  const handleTimelineUpdated = (timeline: TimelineResponse) => {
    setLocalTimelineSpec(timeline);
    onTimelineUpdated?.(timeline);
  };
  const timelineHref = episodeWorkspaceHref(episodeKey, {
    tab: "timeline",
    scriptId: selectedScriptId,
  });
  const summary = buildStoryboardSupportSummary(
    selectedStoryboard,
    localTimelineSpec,
  );
  const timelineOverview = buildStoryboardTimelineOverview(
    localTimelineSpec,
    selectedAudioTimeline,
  );
  const firstVideoClipId = firstTimelineVideoClipId(localTimelineSpec);
  const frames = buildStoryboardSupportFrames(
    selectedStoryboard,
    normalizedScenes,
    localTimelineSpec,
  );
  const storyboardStatus = frames.length
    ? "Placeholders ready"
    : hasStoryboard
    ? "Placeholders missing"
    : "Placeholders pending";

  return (
    <div className="space-y-4">
      <section
        data-storyboard-support-shell="unframed"
        className="border-b border-slate-200 bg-white"
      >
        <OperatorSectionHeader
          title="Storyboard Support Workspace"
          subtitle="Summarize storyboards, start/end frames, and video status by clip"
          action={
            <WorkspaceStoryboardActions
              selectedScriptId={selectedScriptId}
              selectedAudioTimeline={selectedAudioTimeline}
              timelineHref={timelineHref}
              clipStoryboardHref={
                firstVideoClipId
                  ? episodeWorkspaceHref(episodeKey, {
                      tab: "timeline",
                      scriptId: selectedScriptId,
                      extraParams: { clipId: firstVideoClipId },
                    })
                  : null
              }
              showAlert={showAlert}
            />
          }
        />
        {timelineOverview ? (
          <WorkspaceStoryboardTimelinePanel
            episodeKey={episodeKey}
            selectedScriptId={selectedScriptId}
            selectedTimelineSpec={localTimelineSpec}
            selectedAudioTimeline={selectedAudioTimeline}
            selectedStoryboard={selectedStoryboard}
            overview={timelineOverview}
          />
        ) : null}
        <div
          data-storyboard-support-context-strip="inline"
          className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-slate-100 bg-slate-50/50 px-3 py-1.5 text-xs text-slate-600"
        >
          <SupportMetaItem
            label="Source"
            value={storyboardTimelineSourceLabel(
              summary.timelineId,
              summary.timelineVersion,
              summary.generationSource,
            )}
          />
          <SupportMetaItem label="Storyboard" value={storyboardStatus} />
          <SupportMetaItem
            label="Assets"
            value={`${summary.imageCount} keyframes · ${summary.videoCount} videos`}
          />
        </div>
      </section>

      <WorkspaceStoryboardClipManagement
        episodeKey={episodeKey}
        selectedScriptId={selectedScriptId}
        selectedTimelineSpec={localTimelineSpec}
        selectedStoryboard={selectedStoryboard}
        normalizedScenes={normalizedScenes}
        resolvedVideos={resolvedVideos}
      />

      <OperatorPanel>
        <OperatorSectionHeader
          title="Placeholder Frames"
          subtitle={`${summary.frameCount} timeline-aligned shots`}
        />
        {frames.length ? (
          <div className="divide-y divide-gray-100">
            {frames.map((frame) => (
              <StoryboardSupportFrameRow
                key={frame.id}
                frame={frame}
                selectedTimelineSpec={localTimelineSpec}
                showAlert={showAlert}
                onTimelineUpdated={handleTimelineUpdated}
              />
            ))}
          </div>
        ) : (
          <div className="p-4">
            <OperatorState
              title="No storyboard placeholders yet"
              detail="The current script does not have any timeline placeholder frames to review."
            />
          </div>
        )}
      </OperatorPanel>
    </div>
  );
}

function SupportMetaItem({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex min-w-0 items-center gap-1.5">
      <span className="text-slate-500">{label}</span>
      <span className="truncate font-medium text-slate-800">{value}</span>
    </span>
  );
}

function storyboardTimelineSourceLabel(
  timelineId: string | null,
  timelineVersion: string | null,
  generationSource: string | null,
) {
  return timelineId
    ? `Timeline ${timelineId} · v${timelineVersion ?? "?"}`
    : generationSource ?? "Current script beat";
}
