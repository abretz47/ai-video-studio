import { useCallback, useEffect, useMemo, useState } from "react";

import { aiAPI } from "@/utils/api/endpoints";
import { AIModelType } from "@/utils/api/types";
import { virtualIPImageAPI } from "@/utils/api/endpoints";
import { useAvailableModels } from "@/hooks/useAvailableModels";
import { useStylePresets } from "@/hooks/useStylePresets";
import { extractImageUi } from "@/utils/modelUi";

import type { ImageGenerationFormState } from "./virtualIpImageTypes";

interface UseVirtualIPImageGenerationOptions {
  virtualIPId: number | null;
  showAlert: (opts: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
    title?: string;
    confirmText?: string;
    onConfirm?: () => void;
  }) => void;
  router: { push: (path: string) => void };
  onTaskCreated?: (taskId: number) => void;
}

export function useVirtualIPImageGeneration({
  virtualIPId,
  showAlert,
  router,
  onTaskCreated,
}: UseVirtualIPImageGenerationOptions) {
  const [generating, setGenerating] = useState(false);
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [generateForm, setGenerateForm] = useState<ImageGenerationFormState>({
    style: "realistic",
    style_preset_id: "",
    style_spec: {},
    category: "portrait",
    model: "",
    generation_profile: undefined,
    additional_prompts: "",
    is_default: false,
    count: 1,
    aspect_ratio: undefined,
    reference_images: [],
  });

  const fetchModels = useCallback(
    () => aiAPI.getAvailableModels({ type: AIModelType.Image }),
    [],
  );
  const { models: availableModels, defaultModel: recommendedModel } =
    useAvailableModels({
      fetcher: fetchModels,
      modelType: AIModelType.Image,
      cacheKey: `virtual-ip-image:${virtualIPId}`,
    });

  const selectedModel = useMemo(
    () =>
      availableModels.find(
        (model) => model.model_id === (generateForm.model || recommendedModel),
      ),
    [availableModels, generateForm.model, recommendedModel],
  );

  useEffect(() => {
    if (generateForm.model) return;
    const firstModelId =
      recommendedModel ||
      (availableModels.length > 0 ? availableModels[0].model_id : "");
    if (!firstModelId) return;
    setGenerateForm((prev) =>
      prev.model ? prev : { ...prev, model: firstModelId },
    );
  }, [availableModels, recommendedModel, generateForm.model]);

  const imageUi = useMemo(() => extractImageUi(selectedModel), [selectedModel]);

  useEffect(() => {
    setGenerateForm((prev) => {
      let changed = false;
      const next = { ...prev };
      if (!prev.size && imageUi.defaultSize) {
        next.size = imageUi.defaultSize;
        changed = true;
      }
      if (imageUi.supportsAspectRatio) {
        if (!prev.aspect_ratio && imageUi.defaultAspectRatio) {
          next.aspect_ratio = imageUi.defaultAspectRatio;
          changed = true;
        }
      } else if (prev.aspect_ratio) {
        next.aspect_ratio = undefined;
        changed = true;
      }
      return changed ? next : prev;
    });
  }, [
    imageUi.defaultAspectRatio,
    imageUi.defaultSize,
    imageUi.supportsAspectRatio,
  ]);

  const resolutionOptions = useMemo(
    () =>
      imageUi.sizeOptions.map((value) => ({
        value,
        label: value.toUpperCase?.() ? value.toUpperCase() : value,
      })),
    [imageUi.sizeOptions],
  );

  const aspectRatioOptions = useMemo(
    () => (imageUi.supportsAspectRatio ? imageUi.aspectRatioOptions : []),
    [imageUi.aspectRatioOptions, imageUi.supportsAspectRatio],
  );

  const { presets: stylePresets } = useStylePresets();
  const selectedStylePreset = useMemo(() => {
    if (!generateForm.style_preset_id) return undefined;
    return stylePresets.find(
      (p) => p.preset_id === generateForm.style_preset_id,
    );
  }, [generateForm.style_preset_id, stylePresets]);

  const handleGenerateImage = async () => {
    if (!virtualIPId) {
      showAlert({ message: "Virtual IP has not loaded yet", variant: "error" });
      return;
    }
    try {
      setGenerating(true);
      const modelToUse =
        generateForm.model ||
        recommendedModel ||
        (availableModels.length > 0 ? availableModels[0].model_id : "");

      if (!modelToUse) {
        showAlert({
          message: "The model list has not loaded yet. Please try again.",
          variant: "warning",
        });
        return;
      }

      const response = await virtualIPImageAPI.generateImageAsync(virtualIPId, {
        ...generateForm,
        model: modelToUse,
        style_spec:
          generateForm.style_spec &&
          Object.keys(generateForm.style_spec).length > 0
            ? generateForm.style_spec
            : undefined,
      });

      if (response.success && response.data) {
        onTaskCreated?.(response.data.task_id);
        setShowGenerateForm(false);
        setGenerateForm({
          style: "realistic",
          style_preset_id: "",
          style_spec: {},
          category: "portrait",
          model: recommendedModel || "",
          generation_profile: undefined,
          additional_prompts: "",
          is_default: false,
          count: 1,
          size: imageUi.defaultSize,
          aspect_ratio: imageUi.supportsAspectRatio
            ? imageUi.defaultAspectRatio || undefined
            : undefined,
          reference_images: [],
        });
        showAlert({
          title: "Image generation task created",
          message:
            "The task is running in the background. The image list will refresh automatically when it finishes. Go to the task management page?",
          variant: "success",
          confirmText: "Go to Tasks",
          onConfirm: () => router.push("/tasks"),
        });
      } else {
        throw new Error(response.error || "AI image generation failed");
      }
    } catch (error) {
      console.error("AI image generation failed:", error);
      showAlert({
        message: `AI image generation failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        variant: "error",
      });
    } finally {
      setGenerating(false);
    }
  };

  return {
    generateForm,
    setGenerateForm,
    generating,
    showGenerateForm,
    setShowGenerateForm,
    availableModels,
    recommendedModel,
    selectedModel,
    supportsAspectRatio: imageUi.supportsAspectRatio,
    resolutionOptions,
    aspectRatioOptions,
    fetchModels,
    stylePresets,
    selectedStylePreset,
    handleGenerateImage,
  };
}
