"use client";

import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import {
  GenerationProfileSelect,
  ImageGenAdvancedFields,
  ModelUiFields,
  MultiModelSelector,
  operatorInputClass,
  operatorSelectClass,
} from "@/components/shared";
import { AIModelType, type AIModel } from "@/utils/api/types";
import { extractImageGenUi } from "@/utils/modelUi";
import type { GenerationFormState } from "./types";
import { EnvironmentReferenceImagesField } from "./EnvironmentReferenceImagesField";

interface EnvironmentGenerationFieldsProps {
  envKey: string;
  generation: GenerationFormState;
  setGeneration: Dispatch<SetStateAction<GenerationFormState>>;
  showToggle?: boolean;
  toggleLabel?: string;
  withDivider?: boolean;
  compact?: boolean;
}

export function EnvironmentGenerationFields({
  envKey,
  generation,
  setGeneration,
  showToggle = true,
  toggleLabel = "Automatically generate reference images after creation (optional model settings)",
  withDivider = true,
  compact = false,
}: EnvironmentGenerationFieldsProps) {
  const [availableModels, setAvailableModels] = useState<AIModel[]>([]);
  const selectedModel = useMemo(
    () => availableModels.find((model) => model.model_id === generation.model),
    [availableModels, generation.model],
  );
  const imageGenUi = useMemo(
    () => extractImageGenUi(selectedModel, "text_to_image"),
    [selectedModel],
  );
  const supportsReferenceImages =
    Boolean(envKey) && imageGenUi.supportsExtraImages;
  const maxReferenceImages = imageGenUi.maxReferenceImages;
  const maxCount = imageGenUi.maxCount;
  const effectiveMaxCount =
    typeof maxCount === "number" && maxCount > 0 ? maxCount : 4;
  const countOptions = useMemo(
    () => Array.from({ length: effectiveMaxCount }, (_, index) => index + 1),
    [effectiveMaxCount],
  );
  const showFields = showToggle ? generation.enabled : true;
  const bodyClass = compact
    ? "flex min-w-0 flex-col gap-3"
    : "grid grid-cols-1 gap-4 md:grid-cols-2";
  const spanClass = compact ? "min-w-0 w-full" : "min-w-0 md:col-span-2";

  const updateField = <K extends keyof GenerationFormState>(
    key: K,
    value: GenerationFormState[K],
  ) => {
    setGeneration((prev) => ({ ...prev, [key]: value }));
  };

  useEffect(() => {
    if (supportsReferenceImages) return;
    if (generation.reference_images.length === 0) return;
    setGeneration((prev) => ({ ...prev, reference_images: [] }));
  }, [generation.reference_images.length, setGeneration, supportsReferenceImages]);

  useEffect(() => {
    if (!supportsReferenceImages) return;
    if (typeof maxReferenceImages !== "number" || maxReferenceImages <= 0)
      return;
    if (generation.reference_images.length <= maxReferenceImages) return;
    setGeneration((prev) => ({
      ...prev,
      reference_images: prev.reference_images.slice(-maxReferenceImages),
    }));
  }, [generation.reference_images, maxReferenceImages, setGeneration, supportsReferenceImages]);

  useEffect(() => {
    if (typeof maxCount !== "number" || maxCount <= 0) return;
    if (generation.count <= maxCount) return;
    setGeneration((prev) => ({ ...prev, count: maxCount }));
  }, [generation.count, maxCount, setGeneration]);

  return (
    <div className={`${withDivider ? "border-t border-gray-200 pt-4" : ""} space-y-4`}>
      {showToggle && (
        <label className="flex items-center gap-2 text-xs font-medium text-gray-700">
          <input
            type="checkbox"
            checked={generation.enabled}
            onChange={(e) => updateField("enabled", e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          {toggleLabel}
        </label>
      )}

      {showFields && (
        <div className={bodyClass}>
          <div className={spanClass}>
            <label className="mb-1 block whitespace-nowrap text-xs font-medium text-gray-700">
              {compact ? "Prompt (optional)" : "Additional prompt (optional)"}
            </label>
            <textarea
              value={generation.prompt}
              onChange={(e) => updateField("prompt", e.target.value)}
              rows={compact ? 2 : 3}
              className={operatorInputClass(
                `h-auto w-full py-2 text-sm ${compact ? "min-h-16" : "min-h-20"}`,
              )}
              placeholder="Leave blank to use the environment name/description"
            />
          </div>
          {supportsReferenceImages ? (
            <EnvironmentReferenceImagesField
              envKey={envKey}
              value={generation.reference_images}
              maxSelection={maxReferenceImages}
              onChange={(next) => {
                const max = maxReferenceImages;
                const clamped =
                  typeof max === "number" && max > 0 ? next.slice(-max) : next;
                updateField("reference_images", clamped);
              }}
            />
          ) : null}
          <div className="min-w-0">
            <MultiModelSelector
              label="AI Model"
              value={generation.model ? [generation.model] : []}
              onChange={(ids) => updateField("model", ids[0] || "")}
              modelType={AIModelType.Image}
              cacheKey="environment-text-to-image"
              allowAuto={false}
              multiple={false}
              autoSelectDefault
              helperText={
                selectedModel?.capabilities?.join(", ") ||
                "Choose a model for generating environment reference images"
              }
              className="space-y-1"
              onModelsLoaded={(models, defaultModel) => {
                setAvailableModels(models);
                setGeneration((prev) => {
                  if (prev.model) return prev;
                  const nextModel = defaultModel || models[0]?.model_id || "";
                  return nextModel ? { ...prev, model: nextModel } : prev;
                });
              }}
            />
          </div>
          <div className="min-w-0">
            <GenerationProfileSelect
              modelId={generation.model}
              mode="text_to_image"
              value={generation.generation_profile || undefined}
              onChange={(next) => updateField("generation_profile", next || "")}
            />
          </div>
          <div className="min-w-0">
            <label className="mb-1 block whitespace-nowrap text-xs font-medium text-gray-700">
              Style
            </label>
            <select
              value={generation.style}
              onChange={(e) => updateField("style", e.target.value)}
              className={operatorSelectClass("w-full")}
            >
              <option value="realistic">Realistic</option>
              <option value="anime">Anime</option>
              <option value="cartoon">Cartoon</option>
            </select>
          </div>
          <div className="min-w-0">
            <label className="mb-1 block whitespace-nowrap text-xs font-medium text-gray-700">
              Number of Images
            </label>
            <select
              value={generation.count}
              onChange={(e) =>
                updateField(
                  "count",
                  Math.min(
                    effectiveMaxCount,
                    Math.max(1, Number(e.target.value) || 1),
                  ),
                )
              }
              disabled={effectiveMaxCount <= 1}
              className={operatorSelectClass("w-full")}
            >
              {countOptions.map((value) => (
                <option key={value} value={value}>
                  {value} images
                </option>
              ))}
            </select>
          </div>
          <div className={spanClass}>
            <ModelUiFields
              mode="image"
              model={selectedModel}
              value={{
                size: generation.size,
                aspect_ratio: generation.aspect_ratio || undefined,
              }}
              onChange={(next) => {
                if (next.size !== undefined)
                  updateField("size", next.size || "");
                if (next.aspect_ratio !== undefined) {
                  updateField("aspect_ratio", next.aspect_ratio || "");
                }
              }}
            />
          </div>
          <div className={spanClass}>
            <ImageGenAdvancedFields
              mode="text_to_image"
              model={selectedModel}
              value={{
                seed: generation.seed,
                steps: generation.steps,
                cfg_scale: generation.cfg_scale,
                negative_prompt: generation.negative_prompt,
              }}
              onChange={(next) =>
                setGeneration((prev) => ({
                  ...prev,
                  seed: next.seed,
                  steps: next.steps,
                  cfg_scale: next.cfg_scale,
                  negative_prompt: next.negative_prompt,
                }))
              }
            />
          </div>
        </div>
      )}
    </div>
  );
}
