"use client";

import { useEffect, useState } from "react";
import { operatorButtonClass } from "@/components/shared";
import { timelineAPI } from "@/utils/api/endpoints";
import type { TimelineResponse } from "@/utils/api/types";
import type { StoryboardSupportFrame } from "./WorkspaceStoryboardSupportModel";
import {
  buildShotPlanPromptLayerPatch,
  emptyShotPlanPromptLayers,
  type ShotPlanMotionPoint,
  type ShotPlanPromptLayers,
} from "./WorkspaceStoryboardPromptLayers";

type ShowAlert = (options: {
  message: string;
  variant: "info" | "success" | "warning" | "error";
}) => void;

type LayerTextKey = Exclude<
  keyof ShotPlanPromptLayers,
  "motionTimeline" | "promptMethod"
>;

const LAYER_TEXT_FIELDS: Array<{ key: LayerTextKey; label: string }> = [
  { key: "directionAnchor", label: "Direction Anchor" },
  { key: "aestheticReference", label: "Aesthetic Reference" },
  { key: "shotType", label: "Shot Type" },
  { key: "cameraMovement", label: "Camera Movement" },
  { key: "compositionGeometry", label: "Composition Geometry" },
  { key: "emotionalLanding", label: "Emotional Landing" },
];

export function PromptLayerEditor({
  frame,
  selectedTimelineSpec,
  showAlert,
  onTimelineUpdated,
}: {
  frame: StoryboardSupportFrame;
  selectedTimelineSpec?: TimelineResponse | null;
  showAlert?: ShowAlert;
  onTimelineUpdated?: (timeline: TimelineResponse) => void;
}) {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState<ShotPlanPromptLayers>(
    frame.promptLayers ?? emptyShotPlanPromptLayers(),
  );

  useEffect(() => {
    setDraft(frame.promptLayers ?? emptyShotPlanPromptLayers());
  }, [frame.promptLayers]);

  const canSave = Boolean(selectedTimelineSpec && frame.clipId && !saving);
  const handleSave = async () => {
    if (!selectedTimelineSpec || !frame.clipId) return;
    const patchedSpec = buildShotPlanPromptLayerPatch(
      selectedTimelineSpec,
      frame.clipId,
      draft,
    );
    if (!patchedSpec) {
      showAlert?.({ message: "No editable timeline clip was found", variant: "warning" });
      return;
    }

    setSaving(true);
    try {
      const response = await timelineAPI.updateTimeline(
        selectedTimelineSpec.id,
        {
          expected_version: selectedTimelineSpec.version,
          spec: patchedSpec,
        },
      );
      if (!response.success || !response.data) {
        showAlert?.({
          message: response.error || "Failed to save five-layer prompt",
          variant: "error",
        });
        return;
      }
      onTimelineUpdated?.(response.data);
      showAlert?.({ message: "Five-layer prompt saved", variant: "success" });
      setOpen(false);
    } catch (error) {
      showAlert?.({
        message:
          error instanceof Error
            ? `Failed to save five-layer prompt：${error.message}`
            : "Failed to save five-layer prompt",
        variant: "error",
      });
    } finally {
      setSaving(false);
    }
  };

  if (!selectedTimelineSpec || !frame.clipId) return null;

  return (
    <div className="mt-3">
      <button
        type="button"
        className={operatorButtonClass("secondary")}
        onClick={() => setOpen((value) => !value)}
      >
        {open ? "Collapse five-layer editor" : "Edit five-layer prompt"}
      </button>
      {open ? (
        <div className="mt-3 grid gap-2 rounded-md border border-gray-200 bg-white p-3">
          {LAYER_TEXT_FIELDS.slice(0, 5).map((field) => (
            <LayerTextArea
              key={field.key}
              label={field.label}
              value={draft[field.key]}
              onChange={(value) =>
                setDraft((prev) => ({ ...prev, [field.key]: value }))
              }
            />
          ))}
          <MotionTimelineEditor
            points={draft.motionTimeline}
            onChange={(motionTimeline) =>
              setDraft((prev) => ({ ...prev, motionTimeline }))
            }
          />
          {LAYER_TEXT_FIELDS.slice(5).map((field) => (
            <LayerTextArea
              key={field.key}
              label={field.label}
              value={draft[field.key]}
              onChange={(value) =>
                setDraft((prev) => ({ ...prev, [field.key]: value }))
              }
            />
          ))}
          <button
            type="button"
            disabled={!canSave}
            className={operatorButtonClass("primary")}
            onClick={handleSave}
          >
            {saving ? "Saving..." : "Save five-layer prompt"}
          </button>
        </div>
      ) : null}
    </div>
  );
}

function LayerTextArea({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-1 text-[11px] font-medium text-gray-700">
      {label}
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-14 rounded-md border border-gray-200 p-2 text-xs font-normal text-gray-800"
      />
    </label>
  );
}

function MotionTimelineEditor({
  points,
  onChange,
}: {
  points: ShotPlanMotionPoint[];
  onChange: (points: ShotPlanMotionPoint[]) => void;
}) {
  const rows = points.length
    ? points
    : emptyShotPlanPromptLayers().motionTimeline;
  return (
    <div className="grid gap-1 text-[11px] font-medium text-gray-700">
      Second-level action axis
      <div className="grid gap-2">
        {rows.map((point, index) => (
          <div
            key={index}
            className="grid grid-cols-[84px_minmax(0,1fr)] gap-2"
          >
            <input
              type="number"
              value={point.atMs}
              min={0}
              onChange={(event) =>
                onChange(
                  rows.map((item, itemIndex) =>
                    itemIndex === index
                      ? { ...item, atMs: Number(event.target.value) }
                      : item,
                  ),
                )
              }
              className="rounded-md border border-gray-200 px-2 text-xs font-normal text-gray-800"
            />
            <input
              value={point.action}
              onChange={(event) =>
                onChange(
                  rows.map((item, itemIndex) =>
                    itemIndex === index
                      ? { ...item, action: event.target.value }
                      : item,
                  ),
                )
              }
              className="rounded-md border border-gray-200 px-2 text-xs font-normal text-gray-800"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
