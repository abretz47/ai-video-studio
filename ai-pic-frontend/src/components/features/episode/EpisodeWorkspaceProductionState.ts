"use client";

import type { Script } from "@/utils/api/types";
import type { TimelineResolvedVideoListResponse } from "@/utils/api/types";
import type { TabKey } from "@/hooks/episode/useEpisodeWorkspaceController";

export type WorkflowStepStatus = "pending" | "ready" | "generating";

export interface WorkflowStatus {
  script: WorkflowStepStatus;
  timeline: WorkflowStepStatus;
  storyboard: WorkflowStepStatus;
}

export type ProductionActionKind =
  | "generate-script"
  | "generate-timeline"
  | "open-clip"
  | "open-storyboard"
  | "open-timeline";

export type ProductionStep = {
  key: "script" | "timeline" | "clip-video" | "render-export";
  label: string;
  status: WorkflowStepStatus;
};

export type ProductionState = {
  steps: ProductionStep[];
  primaryAction: {
    kind: ProductionActionKind;
    label: string;
    disabled?: boolean;
  };
};

export function buildEpisodeProductionState({
  activeTab,
  script,
  workflowStatus,
  storyboardActionLabel,
  resolvedVideos,
}: {
  activeTab: TabKey;
  script?: Script | null;
  workflowStatus: WorkflowStatus;
  storyboardActionLabel?: string;
  resolvedVideos?: TimelineResolvedVideoListResponse | null;
}): ProductionState {
  const scriptReady = Boolean(script) || workflowStatus.script === "ready";
  const hasTimelineClipEntry = storyboardActionLabel === "Open Clip Storyboard";
  const timelineReady =
    workflowStatus.timeline === "ready" && hasTimelineClipEntry;
  const clipVideoStatus = clipVideoStepStatus(
    timelineReady,
    workflowStatus,
    resolvedVideos,
  );

  const steps: ProductionStep[] = [
    { key: "script", label: "Script", status: scriptReady ? "ready" : "pending" },
    {
      key: "timeline",
      label: "Timeline",
      status: timelineReady ? "ready" : "pending",
    },
    {
      key: "clip-video",
      label: "Clip Video",
      status: clipVideoStatus,
    },
    { key: "render-export", label: "Render/Export", status: "pending" },
  ];

  if (!scriptReady) {
    return {
      steps,
      primaryAction: { kind: "generate-script", label: "Generate Script" },
    };
  }

  if (!timelineReady) {
    return {
      steps,
      primaryAction: { kind: "generate-timeline", label: "Generate Timeline" },
    };
  }

  if (hasTimelineClipEntry) {
    if (resolvedVideos?.ready) {
      return {
        steps,
        primaryAction: { kind: "open-timeline", label: "Render/Export" },
      };
    }
    if (resolvedVideos && resolvedVideos.missing_clip_count > 0) {
      return {
        steps,
        primaryAction: { kind: "open-clip", label: "Handle Missing Clips" },
      };
    }
    return {
      steps,
      primaryAction: { kind: "open-clip", label: "Handle Clip Video" },
    };
  }

  if (activeTab !== "timeline") {
    return {
      steps,
      primaryAction: { kind: "open-timeline", label: "Back to Timeline" },
    };
  }

  return {
    steps,
    primaryAction: { kind: "open-storyboard", label: "View Storyboard References" },
  };
}

function clipVideoStepStatus(
  timelineReady: boolean,
  workflowStatus: WorkflowStatus,
  resolvedVideos?: TimelineResolvedVideoListResponse | null,
): WorkflowStepStatus {
  if (!timelineReady) return "pending";
  if (resolvedVideos) {
    if (resolvedVideos.ready) return "ready";
    if (resolvedVideos.generating_clip_count > 0) return "generating";
    return "pending";
  }
  return workflowStatus.storyboard === "ready" ? "ready" : "pending";
}

export function productionStatusLabel(status: WorkflowStepStatus) {
  if (status === "ready") return "Ready";
  if (status === "generating") return "Generating";
  return "Pending";
}

export function productionStatusTone(
  status: WorkflowStepStatus,
): "green" | "amber" | "gray" {
  if (status === "ready") return "green";
  if (status === "generating") return "amber";
  return "gray";
}

export function scriptOptionLabel(script: Script) {
  const hasVersionInTitle = /\(v[\d.]+\)$/.test(script.title || "");
  const versionSuffix =
    script.version && !hasVersionInTitle ? ` (v${script.version})` : "";
  return `${script.title}${versionSuffix}`;
}
