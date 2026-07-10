"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { operatorButtonClass, operatorSelectClass } from "@/components/shared";
import { timelineAPI } from "@/utils/api/endpoints";
import type {
  TimelineClipReworkAction,
  TimelineClipReworkRequest,
} from "@/utils/api/types";

type NotifyVariant = "success" | "error" | "warning" | "info";

const ACTION_OPTIONS: Array<{
  value: TimelineClipReworkAction;
  label: string;
}> = [
  { value: "re_dub", label: "Re-dub" },
  { value: "re_cut", label: "Re-cut" },
  { value: "re_render", label: "Re-render" },
];

const ROLE_OPTIONS: Record<TimelineClipReworkAction, string[]> = {
  re_dub: ["source_audio"],
  re_cut: ["storyboard_video", "generated_video", "render_output"],
  re_render: ["generated_video", "render_output"],
};

export function buildTimelineClipReworkPayload({
  expectedVersion,
  action,
  mediaAssetId,
  assetRole,
  reason,
}: {
  expectedVersion: number;
  action: TimelineClipReworkAction;
  mediaAssetId: number;
  assetRole?: string | null;
  reason?: string | null;
}): TimelineClipReworkRequest {
  const payload: TimelineClipReworkRequest = {
    expected_version: expectedVersion,
    action,
    media_asset_id: mediaAssetId,
  };
  const role = assetRole?.trim();
  if (role) payload.asset_role = role;
  const cleanedReason = reason?.trim();
  if (cleanedReason) payload.reason = cleanedReason;
  return payload;
}

export function TimelineClipReworkControls({
  timelineId,
  timelineVersion,
  clipId,
  onRecorded,
  onNotify,
}: {
  timelineId?: number | string | null;
  timelineVersion?: number | null;
  clipId?: string | null;
  onRecorded?: () => void | Promise<void>;
  onNotify?: (message: string, variant: NotifyVariant) => void;
}) {
  const [action, setAction] = useState<TimelineClipReworkAction>("re_render");
  const [assetRole, setAssetRole] = useState("");
  const [mediaAssetId, setMediaAssetId] = useState("");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (assetRole && !ROLE_OPTIONS[action].includes(assetRole)) {
      setAssetRole("");
    }
  }, [action, assetRole]);

  const parsedMediaAssetId = parseMediaAssetId(mediaAssetId);
  const canSubmit = Boolean(
    timelineId &&
      timelineVersion &&
      clipId &&
      parsedMediaAssetId &&
      !submitting,
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!timelineId || !timelineVersion || !clipId) {
      const message = "The current clip lacks a stable Timeline context";
      setSubmitError(message);
      onNotify?.(message, "warning");
      return;
    }
    if (!parsedMediaAssetId) {
      const message = "Please enter a valid media_asset_id";
      setSubmitError(message);
      onNotify?.(message, "warning");
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    const payload = buildTimelineClipReworkPayload({
      expectedVersion: timelineVersion,
      action,
      mediaAssetId: parsedMediaAssetId,
      assetRole,
      reason,
    });
    try {
      const res = await timelineAPI.reworkTimelineClip(
        timelineId,
        clipId,
        payload,
      );
      if (!res.success || !res.data) {
        const message = res.error || "Failed to record clip rework asset";
        setSubmitError(message);
        onNotify?.(message, "error");
        return;
      }
      setMediaAssetId("");
      setReason("");
      await onRecorded?.();
      onNotify?.("Clip rework asset recorded", "success");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="mt-2" onSubmit={handleSubmit}>
      <div className="grid gap-2">
        <select
          value={action}
          onChange={(event) =>
            setAction(event.target.value as TimelineClipReworkAction)
          }
          className={operatorSelectClass("w-full")}
        >
          {ACTION_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="grid grid-cols-[1fr_1fr] gap-2">
          <input
            type="number"
            min={1}
            value={mediaAssetId}
            onChange={(event) => setMediaAssetId(event.target.value)}
            placeholder="media_asset_id"
            className="rounded-md border border-gray-200 px-2 py-1.5 text-xs outline-none focus:border-gray-400"
          />
          <select
            value={assetRole}
            onChange={(event) => setAssetRole(event.target.value)}
            className={operatorSelectClass("w-full")}
          >
            <option value="">DefaultCharacter</option>
            {ROLE_OPTIONS[action].map((role) => (
              <option key={role} value={role}>
                {assetRoleLabel(role)}
              </option>
            ))}
          </select>
        </div>
        <input
          type="text"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          placeholder="Reason"
          className="rounded-md border border-gray-200 px-2 py-1.5 text-xs outline-none focus:border-gray-400"
        />
        {submitError ? (
          <div className="text-xs text-red-600">{submitError}</div>
        ) : null}
        <button
          type="submit"
          disabled={!canSubmit}
          className={operatorButtonClass("secondary", "w-full")}
        >
          {submitting ? "Recording..." : "Record Rework Asset"}
        </button>
      </div>
    </form>
  );
}

function parseMediaAssetId(value: string) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

function assetRoleLabel(role: string) {
  const labels: Record<string, string> = {
    source_audio: "Source Audio",
    storyboard_video: "Storyboard Video",
    generated_video: "Generated Video",
    render_output: "Render Output",
  };
  return labels[role] || role;
}
