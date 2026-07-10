"use client";

import { useState } from "react";

import { t } from "@/lib/i18n";
import { operatorButtonClass } from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals";
import {
  GenerationTaskStatusLine,
  useToast,
} from "@/components/shared/notifications";
import { useGenerationTaskTracker } from "@/hooks/useGenerationTaskTracker";
import { storyStructureAPI } from "@/utils/api/endpoints";

import { EnvironmentGenerationFields } from "./EnvironmentGenerationFields";
import { EMPTY_GENERATION, type GenerationFormState } from "./types";

interface EnvironmentSidePanelProps {
  envKey: string;
  onImageUploaded: (imageUrl: string) => void;
  onImagesGenerated?: () => void | Promise<void>;
  variant?: "card" | "embedded";
}

export function EnvironmentSidePanel({
  envKey,
  onImageUploaded,
  onImagesGenerated,
  variant = "card",
}: EnvironmentSidePanelProps) {
  const { showAlert } = useAlertModal();
  const { notify } = useToast();
  const tracker = useGenerationTaskTracker<"environment-images">({
    labels: { "environment-images": t("environments.sidePanel.taskLabel", "Environment Reference Images") },
    onCompleted: () => onImagesGenerated?.(),
    onNotify: notify,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [generation, setGeneration] = useState<GenerationFormState>({
    ...EMPTY_GENERATION,
    enabled: true,
  });
  const [generating, setGenerating] = useState(false);

  const handleUpload = async () => {
    if (!selectedFile || !envKey) {
      showAlert({ message: t("environments.sidePanel.selectImage", "Please select an image file"), variant: "warning" });
      return;
    }
    try {
      setUploading(true);
      const res = await storyStructureAPI.uploadEnvironmentImage(
        envKey,
        selectedFile,
      );
      if (res.success && res.data) {
        onImageUploaded(res.data.url);
        setSelectedFile(null);
        showAlert({ message: t("common.uploadSuccess", "Upload successful"), variant: "success" });
      } else {
        showAlert({ message: res.error || t("common.uploadFailed", "Upload failed"), variant: "error" });
      }
    } catch (error) {
      console.error(error);
      showAlert({ message: t("common.uploadFailed", "Upload failed"), variant: "error" });
    } finally {
      setUploading(false);
    }
  };

  const handleGenerate = async () => {
    if (!envKey) {
      showAlert({ message: t("environments.sidePanel.missingEnvironment", "Environment information is missing"), variant: "warning" });
      return;
    }
    try {
      setGenerating(true);
      const res = await storyStructureAPI.generateEnvironmentImagesAsync(
        envKey,
        {
          prompt: generation.prompt || undefined,
          model: generation.model || undefined,
          generation_profile: generation.generation_profile || undefined,
          count: generation.count,
          size: generation.size || undefined,
          aspect_ratio: generation.aspect_ratio || undefined,
          seed: generation.seed,
          steps: generation.steps,
          cfg_scale: generation.cfg_scale,
          negative_prompt: generation.negative_prompt || undefined,
          style: generation.style || undefined,
          reference_images:
            generation.reference_images.length > 0
              ? generation.reference_images
              : undefined,
        },
      );
      if (res.success && res.data) {
        notify(
          t("environments.sidePanel.taskSubmitted", "Environment reference image task #{taskId} submitted. The image list will refresh automatically when it completes.").replace("{taskId}", String(res.data.task_id)),
          "info",
        );
        tracker.track("environment-images", res.data.task_id);
      } else {
        showAlert({ message: res.error || t("common.generateFailed", "Generation failed"), variant: "error" });
      }
    } catch (error) {
      console.error(error);
      showAlert({ message: t("common.generateFailed", "Generation failed"), variant: "error" });
    } finally {
      setGenerating(false);
    }
  };

  const containerClassName =
    variant === "embedded"
      ? "space-y-5"
      : "space-y-5 rounded-lg border border-gray-200 bg-white p-4";

  return (
    <div className={containerClassName}>
      <div className="min-w-0">
        <h3 className="text-sm font-semibold text-gray-950">{t("environments.sidePanel.uploadTitle", "Upload Reference Image")}</h3>
        <p className="mt-0.5 text-xs text-gray-500">
          {t("environments.sidePanel.uploadDescription", "Common image formats are supported and stored in OSS automatically.")}
        </p>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          className="mt-3 w-full text-xs text-gray-600"
        />
        <button
          type="button"
          onClick={handleUpload}
          disabled={uploading || !selectedFile}
          className={operatorButtonClass("primary", "mt-3 w-full")}
        >
          {uploading ? t("common.uploading", "Uploading...") : t("environments.sidePanel.uploadButton", "Upload Image")}
        </button>
      </div>

      <div className="min-w-0 space-y-3 border-t border-gray-200 pt-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-950">{t("environments.sidePanel.generateTitle", "AI Generate Reference Images")}</h3>
          <p className="mt-0.5 text-xs text-gray-500">
            {t("environments.sidePanel.generateDescription", "Optional prompt. If left blank, generation uses the environment description.")}
          </p>
        </div>
        <EnvironmentGenerationFields
          envKey={envKey}
          generation={generation}
          setGeneration={setGeneration}
          compact
          showToggle={false}
          withDivider={false}
        />
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className={operatorButtonClass("primary", "w-full")}
        >
          {generating ? t("environments.sidePanel.submittingTask", "Submitting Task...") : t("environments.sidePanel.createTask", "Create Generation Task")}
        </button>
        <GenerationTaskStatusLine
          label={t("environments.sidePanel.taskLabel", "Environment Reference Images")}
          task={tracker.tasks["environment-images"]}
        />
      </div>
    </div>
  );
}
