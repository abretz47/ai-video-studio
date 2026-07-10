"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { scriptAPI } from "@/utils/api/endpoints";
import type {
  NormalizedScene,
  Script,
  TimelineResolvedVideoListResponse,
  TimelineResponse,
} from "@/utils/api/types";
import { OperatorState } from "@/components/shared";
import { EpisodeTimelineWorkspace } from "./EpisodeTimelineWorkspace";
import { useTimelinePipelineTracking } from "./useTimelinePipelineTracking";

interface WorkspaceTimelineTabContentProps {
  episodeId: number | string;
  scripts: Script[];
  selectedScriptId: number | null;
  selectedScript: Script | null;
  selectedTimelineSpec: TimelineResponse | null;
  onTimelineUpdated?: (timeline: TimelineResponse) => void;
  resolvedVideos?: TimelineResolvedVideoListResponse | null;
  resolvedVideosError?: string | null;
  reloadResolvedVideos?: () => void | Promise<void>;
  initialSelectedClipId?: string | null;
  selectedAudioTimeline: Record<string, unknown> | null;
  selectedStoryboard: Record<string, unknown> | null;
  normalizedScenes: NormalizedScene[];

  // Model selection
  timingModel: string;
  setTimingModel: (value: string) => void;

  // Alert
  showAlert: (options: {
    message: string;
    variant: "info" | "success" | "warning" | "error";
  }) => void;
}

export function WorkspaceTimelineTabContent({
  episodeId,
  scripts,
  selectedScriptId,
  selectedScript,
  selectedTimelineSpec,
  onTimelineUpdated,
  resolvedVideos,
  resolvedVideosError,
  reloadResolvedVideos,
  initialSelectedClipId,
  selectedAudioTimeline,
  selectedStoryboard,
  normalizedScenes,
  timingModel,
  setTimingModel,
  showAlert,
}: WorkspaceTimelineTabContentProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [pipelineBusy, setPipelineBusy] = useState(false);
  const [useDurationControl, setUseDurationControl] = useState(false);
  const { pipelineTask, trackPipelineTask } = useTimelinePipelineTracking({
    episodeId,
    selectedScriptId,
    onTimelineUpdated,
  });

  const autoTimelinePipelineRunId = searchParams.get("autoTimelinePipeline");

  const handleGenerateTimelinePipeline = useCallback(async () => {
    if (!selectedScriptId) {
      showAlert({ message: "Please select a script first", variant: "warning" });
      return;
    }
    try {
      setPipelineBusy(true);
      const res = await scriptAPI.generateTimelinePipelineAsync(
        selectedScriptId,
        {
          timing_model: timingModel || undefined,
          // Use sensible defaults
          overwrite_audio: true,
          overwrite_timeline: true,
          overwrite_storyboard: true,
          min_pause_seconds: 1.5,
          use_duration_control: useDurationControl,
        },
      );
      if (res.success && res.data) {
        trackPipelineTask(res.data.task_id);
        showAlert({
          message: `One-click pipeline task submitted (task_id=${res.data.task_id}); the timeline will refresh automatically when it completes`,
          variant: "info",
        });
      } else {
        showAlert({
          message: `Failed to create one-click pipeline task: ${res.error || "Unknown error"}`,
          variant: "error",
        });
      }
    } catch (error) {
      console.error("Failed to create one-click pipeline task:", error);
      showAlert({ message: "Failed to create one-click pipeline task", variant: "error" });
    } finally {
      setPipelineBusy(false);
    }
  }, [
    selectedScriptId,
    showAlert,
    timingModel,
    trackPipelineTask,
    useDurationControl,
  ]);

  useEffect(() => {
    if (!autoTimelinePipelineRunId || pipelineBusy || !selectedScriptId) return;

    try {
      const storageKey = `autoTimelinePipeline:${selectedScriptId}`;
      const lastRunId = window.sessionStorage.getItem(storageKey);
      if (lastRunId === autoTimelinePipelineRunId) return;
      window.sessionStorage.setItem(storageKey, autoTimelinePipelineRunId);
    } catch {
      // ignore
    }

    void handleGenerateTimelinePipeline();

    const params = new URLSearchParams(searchParams.toString());
    params.delete("autoTimelinePipeline");
    const next = params.toString();
    router.replace(next ? `${pathname}?${next}` : pathname, { scroll: false });
  }, [
    autoTimelinePipelineRunId,
    handleGenerateTimelinePipeline,
    pathname,
    pipelineBusy,
    router,
    searchParams,
    selectedScriptId,
  ]);

  const handleNavigateToTasks = useCallback(() => {
    router.push("/tasks");
  }, [router]);

  const handleNavigateToScript = useCallback(() => {
    if (selectedScript) {
      router.push(
        `/scripts/${selectedScript.business_id || selectedScript.id}`,
      );
    }
  }, [router, selectedScript]);

  const handleNavigateToStoryboard = useCallback(() => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", "storyboard");
    if (selectedScriptId) {
      params.set("scriptId", String(selectedScriptId));
    }
    router.push(`${pathname}?${params.toString()}`);
  }, [pathname, router, searchParams, selectedScriptId]);

  const handleNavigateToCharacters = useCallback(() => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", "characters");
    if (selectedScriptId) {
      params.set("scriptId", String(selectedScriptId));
    }
    router.push(`${pathname}?${params.toString()}`);
  }, [pathname, router, searchParams, selectedScriptId]);

  const handleSelectedClipIdChange = useCallback(
    (clipId: string | null) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("tab", "timeline");
      if (selectedScriptId) params.set("scriptId", String(selectedScriptId));
      if (clipId) {
        params.set("clipId", clipId);
      } else {
        params.delete("clipId");
      }
      const next = params.toString();
      if (next === searchParams.toString()) return;
      router.replace(`${pathname}?${next}`, { scroll: false });
    },
    [pathname, router, searchParams, selectedScriptId],
  );

  if (scripts.length === 0) {
    return (
      <OperatorState
        title="No scripts yet"
        detail="Generate a script first before creating a timeline"
      />
    );
  }

  return (
    <EpisodeTimelineWorkspace
      episodeId={episodeId}
      selectedScriptId={selectedScriptId}
      selectedTimelineSpec={selectedTimelineSpec}
      onTimelineUpdated={onTimelineUpdated}
      resolvedVideos={resolvedVideos}
      resolvedVideosError={resolvedVideosError}
      reloadResolvedVideos={reloadResolvedVideos}
      onSelectedClipIdChange={handleSelectedClipIdChange}
      initialSelectedClipId={initialSelectedClipId}
      selectedAudioTimeline={selectedAudioTimeline}
      selectedStoryboard={selectedStoryboard}
      normalizedScenes={normalizedScenes}
      pipelineBusy={pipelineBusy}
      timingModel={timingModel}
      setTimingModel={setTimingModel}
      useDurationControl={useDurationControl}
      setUseDurationControl={setUseDurationControl}
      onGenerateTimelinePipeline={handleGenerateTimelinePipeline}
      pipelineTask={pipelineTask}
      onNavigateToTasks={handleNavigateToTasks}
      onNavigateToScript={handleNavigateToScript}
      onNavigateToStoryboard={handleNavigateToStoryboard}
      onNavigateToCharacters={handleNavigateToCharacters}
    />
  );
}
