"use client";

import { useCallback } from "react";
import { timelineAPI } from "@/utils/api/endpoints";
import type { TimelineResponse } from "@/utils/api/types";

/**
 * Refresh clip assets and re-fetch the timeline spec after a clip generation
 * task completes, so previews and panel references update in place.
 */
export function useTimelineGenerationRefresh({
  timelineSpecId,
  onTimelineUpdated,
  reloadClipAssets,
  reloadRenderJobs,
  reloadResolvedVideos,
}: {
  timelineSpecId: number | string | null;
  onTimelineUpdated?: (timeline: TimelineResponse) => void;
  reloadClipAssets?: () => void | Promise<void>;
  reloadRenderJobs?: () => void | Promise<void>;
  reloadResolvedVideos?: () => void | Promise<void>;
}) {
  return useCallback(async () => {
    await reloadClipAssets?.();
    await reloadResolvedVideos?.();
    // After clip video generation succeeds, the backend automatically queues the final render; refresh the render panel here so the new job appears immediately.
    await reloadRenderJobs?.();
    if (!timelineSpecId || !onTimelineUpdated) return;
    const res = await timelineAPI.getTimeline(timelineSpecId);
    if (res.success && res.data) onTimelineUpdated(res.data);
  }, [
    onTimelineUpdated,
    reloadClipAssets,
    reloadRenderJobs,
    reloadResolvedVideos,
    timelineSpecId,
  ]);
}
