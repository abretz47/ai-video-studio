import { t } from "@/lib/i18n";
import type { ProductionCanvasNode } from "./productionCanvasModel";

type MediaOutputValue = string | number | boolean | number[] | undefined;

function stringOutput(outputs: Record<string, unknown> | undefined, key: string) {
  const value = outputs?.[key];
  return typeof value === "string" ? value : "";
}

function numberOutput(outputs: Record<string, unknown> | undefined, key: string) {
  const value = outputs?.[key];
  return typeof value === "number" && Number.isFinite(value) ? String(value) : "";
}

function boolOutput(
  outputs: Record<string, unknown> | undefined,
  key: string,
  fallback: boolean,
) {
  const value = outputs?.[key];
  return typeof value === "boolean" ? value : fallback;
}

function frameIndexesText(outputs: Record<string, unknown> | undefined) {
  const value = outputs?.frame_indexes;
  return Array.isArray(value) ? value.join(", ") : "";
}

function parseFrameIndexes(value: string) {
  const indexes = value
    .split(",")
    .map((item) => Number.parseInt(item.trim(), 10))
    .filter((item, index, all) => Number.isInteger(item) && item >= 0 && all.indexOf(item) === index);
  return indexes.length ? indexes : undefined;
}

function parseNumber(value: string) {
  if (!value.trim()) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function TextField({
  label,
  onChange,
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  const handleValue = (target: HTMLInputElement) => onChange(target.value);
  return (
    <label className="min-w-0">
      <span className="text-[11px] font-semibold text-gray-600">{label}</span>
      <input
        aria-label={label}
        className="mt-1 h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs text-gray-800 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        value={value}
        onChange={(event) => handleValue(event.currentTarget)}
        onInput={(event) => handleValue(event.currentTarget)}
      />
    </label>
  );
}

export function ProductionCanvasMediaControls({
  node,
  onUpdateNodeOutputs,
}: {
  node?: ProductionCanvasNode;
  onUpdateNodeOutputs: (nodeId: string, patch: Record<string, MediaOutputValue>) => void;
}) {
  if (!node || (node.skill !== "image.candidates" && node.skill !== "video.candidates")) {
    return null;
  }

  const outputs = node.outputs;
  const update = (patch: Record<string, MediaOutputValue>) =>
    onUpdateNodeOutputs(node.id, patch);
  const isImage = node.skill === "image.candidates";

  return (
    <div className="border-t border-gray-100 pt-3">
      <div className="text-xs font-semibold text-gray-700">{t("canvas.media.title", "Media Execution Parameters")}</div>
      <div className="mt-2 grid gap-2">
        <TextField
          label={t("canvas.media.frameIndexes", "Media Frame Indexes")}
          value={frameIndexesText(outputs)}
          onChange={(value) => update({ frame_indexes: parseFrameIndexes(value) })}
        />
        <TextField
          label={t("canvas.media.model", "Media Model")}
          value={stringOutput(outputs, "model")}
          onChange={(value) => update({ model: value.trim() || undefined })}
        />
        {isImage ? (
          <>
            <TextField
              label={t("canvas.media.imageAspectRatio", "Image Aspect Ratio")}
              value={stringOutput(outputs, "aspect_ratio")}
              onChange={(value) => update({ aspect_ratio: value.trim() || undefined })}
            />
            <label className="flex items-center gap-2 text-xs text-gray-600">
              <input
                aria-label={t("canvas.media.requireReferenceImages", "Require Reference Images")}
                type="checkbox"
                checked={boolOutput(outputs, "require_reference_images", true)}
                onChange={(event) =>
                  update({ require_reference_images: event.currentTarget.checked })
                }
              />
              {t("canvas.media.requireReferenceImages", "Require Reference Images")}
            </label>
          </>
        ) : (
          <>
            <TextField
              label={t("canvas.media.videoDuration", "Video Duration")}
              value={numberOutput(outputs, "duration")}
              onChange={(value) => update({ duration: parseNumber(value) })}
            />
            <TextField
              label={t("canvas.media.videoFps", "Video FPS")}
              value={numberOutput(outputs, "fps")}
              onChange={(value) => update({ fps: parseNumber(value) })}
            />
            <TextField
              label={t("canvas.media.videoResolution", "Video Resolution")}
              value={stringOutput(outputs, "resolution")}
              onChange={(value) => update({ resolution: value.trim() || undefined })}
            />
            <TextField
              label={t("canvas.media.videoAspectRatio", "Video Aspect Ratio")}
              value={stringOutput(outputs, "ratio")}
              onChange={(value) => update({ ratio: value.trim() || undefined })}
            />
            <label className="flex items-center gap-2 text-xs text-gray-600">
              <input
                aria-label={t("canvas.media.fixedCamera", "Fixed Camera")}
                type="checkbox"
                checked={boolOutput(outputs, "camera_fixed", false)}
                onChange={(event) => update({ camera_fixed: event.currentTarget.checked })}
              />
              {t("canvas.media.fixedCamera", "Fixed Camera")}
            </label>
          </>
        )}
      </div>
    </div>
  );
}
