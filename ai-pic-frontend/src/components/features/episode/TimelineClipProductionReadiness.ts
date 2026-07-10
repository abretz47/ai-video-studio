import type { TimelineItem } from "@/components/features";
import {
  timelineClipHasShotPlan,
  timelineClipStartEndFrameStatus,
  timelineClipStoryboardPanelIndex,
  timelineClipStoryboardSheetUrl,
} from "./TimelineClipProviderReworkModel";

export interface TimelineClipProductionReadiness {
  storyboardReady: boolean;
  keyframesReady: boolean;
  canGenerateVideo: boolean;
  videoGateMessage: string | null;
  storyboardPanelIndex: number | null;
  storyboardSheetUrl: string | null;
  keyframeStatus: { startReady: boolean; endReady: boolean; label: string };
}

export const VIDEO_IMAGE_GATE_MESSAGE =
  "Complete the clip storyboard and start/end frames before generating video";

export function timelineClipProductionReadiness(
  item: TimelineItem | null,
): TimelineClipProductionReadiness {
  const storyboardPanelIndex = timelineClipStoryboardPanelIndex(item);
  const storyboardSheetUrl = timelineClipStoryboardSheetUrl(item);
  const keyframeStatus = timelineClipStartEndFrameStatus(item);
  const storyboardReady = Boolean(storyboardSheetUrl);
  const keyframesReady = keyframeStatus.startReady && keyframeStatus.endReady;
  const canGenerateVideo =
    (storyboardReady && keyframesReady) || timelineClipHasShotPlan(item);
  return {
    storyboardReady,
    keyframesReady,
    canGenerateVideo,
    videoGateMessage: canGenerateVideo ? null : VIDEO_IMAGE_GATE_MESSAGE,
    storyboardPanelIndex,
    storyboardSheetUrl,
    keyframeStatus,
  };
}
