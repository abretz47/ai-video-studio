"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { AlertOptions } from "@/components/shared/modals";
import { useToast } from "@/components/shared/notifications";
import { timelineAPI } from "@/utils/api/endpoints";
import type {
  TimelineRenderJobResponse,
  TimelineRenderType,
  TimelineResponse,
} from "@/utils/api/types";
import type { TimelineRenderReadiness } from "./EpisodeTimelineRenderModel";

export function useTimelineRenderJobs({
  selectedTimelineSpec,
  renderReadiness,
  showAlert,
}: {
  selectedTimelineSpec: TimelineResponse | null;
  renderReadiness: TimelineRenderReadiness;
  showAlert: (options: AlertOptions) => void;
}) {
  const [renderJobs, setRenderJobs] = useState<TimelineRenderJobResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRenderJobs = useCallback(async () => {
    if (!selectedTimelineSpec?.id) {
      setRenderJobs([]);
      setError(null);
      return;
    }
    setLoading(true);
    try {
      const res = await timelineAPI.listTimelineRenderJobs(selectedTimelineSpec.id);
      if (res.success && res.data) {
        setRenderJobs(res.data.items || []);
        setError(null);
      } else {
        setError(res.error || "Failed to load render tasks");
      }
    } finally {
      setLoading(false);
    }
  }, [selectedTimelineSpec?.id]);

  useEffect(() => {
    void loadRenderJobs();
  }, [loadRenderJobs]);

  const latestJob = renderJobs[0] || null;
  useEffect(() => {
    if (
      !latestJob ||
      (latestJob.status !== "queued" && latestJob.status !== "running")
    ) {
      return;
    }
    const timer = setInterval(() => void loadRenderJobs(), 4000);
    return () => clearInterval(timer);
  }, [latestJob, loadRenderJobs]);

  const { notify } = useToast();
  const prevJobStatusRef = useRef<{ id: number; status: string } | null>(null);
  useEffect(() => {
    const prev = prevJobStatusRef.current;
    if (latestJob) {
      prevJobStatusRef.current = { id: latestJob.id, status: latestJob.status };
    }
    if (!latestJob || !prev || prev.id !== latestJob.id) return;
    if (prev.status === latestJob.status) return;
    const wasActive = prev.status === "queued" || prev.status === "running";
    if (!wasActive) return;
    if (latestJob.status === "succeeded") {
      notify(
        `Render complete (job #${latestJob.id}); the final cut is ready and can be downloaded from the render panel`,
        "success",
      );
    } else if (latestJob.status === "failed") {
      notify(`Render failed (job #${latestJob.id}); see the render panel for details`, "error");
    }
  }, [latestJob, notify]);

  const queueRender = useCallback(
    async (renderType: TimelineRenderType, forceNewAttempt = false) => {
      if (!selectedTimelineSpec?.id) {
        showAlert({ message: "Please generate the timeline first", variant: "warning" });
        return;
      }
      if (!renderReadiness.ready) {
        showAlert({
          message: renderReadiness.videoClipCount
            ? `${renderReadiness.missingClips.length} clips are still missing video assets`
            : "The current timeline has no renderable video track",
          variant: "warning",
        });
        return;
      }

      setBusy(true);
      try {
        const res = await timelineAPI.queueTimelineRender(selectedTimelineSpec.id, {
          timeline_version: selectedTimelineSpec.version,
          render_type: renderType,
          preset: {
            fps: selectedTimelineSpec.spec?.fps ?? 24,
            resolution: selectedTimelineSpec.spec?.resolution ?? "1080x1920",
          },
          force_new_attempt: forceNewAttempt,
        });
        if (res.success && res.data) {
          setRenderJobs((prev) => [
            res.data as TimelineRenderJobResponse,
            ...prev.filter((job) => job.id !== res.data?.id),
          ]);
          setError(null);
          showAlert({
            message: `Render task created (render_job_id=${res.data.id})`,
            variant: "info",
          });
          void loadRenderJobs();
        } else {
          setError(res.error || "Failed to create render task");
          showAlert({
            message: res.error || "Failed to create render task",
            variant: "error",
          });
        }
      } finally {
        setBusy(false);
      }
    },
    [loadRenderJobs, renderReadiness, selectedTimelineSpec, showAlert],
  );

  const restartRenderJob = useCallback(
    async (renderJobId: number) => {
      if (!selectedTimelineSpec?.id) return;
      setBusy(true);
      try {
        const res = await timelineAPI.restartTimelineRenderJob(
          selectedTimelineSpec.id,
          renderJobId,
        );
        if (res.success && res.data) {
          setError(null);
          showAlert({
            message: `Render restarted (render_job_id=${res.data.id})`,
            variant: "info",
          });
          void loadRenderJobs();
        } else {
          setError(res.error || "Failed to restart render job");
          showAlert({
            message: res.error || "Failed to restart render job",
            variant: "error",
          });
        }
      } finally {
        setBusy(false);
      }
    },
    [loadRenderJobs, selectedTimelineSpec, showAlert],
  );

  return {
    renderJobs,
    latestJob,
    loading,
    busy,
    error,
    queueRender,
    restartRenderJob,
    reloadRenderJobs: loadRenderJobs,
  };
}
