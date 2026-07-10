"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { t } from "@/lib/i18n";
import {
  CreationOverlay,
  operatorButtonClass,
  operatorInputClass,
  operatorSelectClass,
} from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import { storyStructureAPI } from "@/utils/api/endpoints";
import type { Environment, EnvironmentCreate } from "@/utils/api/types";

import { EnvironmentGenerationFields } from "./EnvironmentGenerationFields";
import {
  EMPTY_ENV_FORM,
  EMPTY_GENERATION,
  type EnvironmentFormState,
  type GenerationFormState,
} from "./types";

interface EnvironmentCreateOverlayProps {
  open: boolean;
  onClose: () => void;
  onCreated: (env: Environment) => void;
}

export function EnvironmentCreateOverlay({
  open,
  onClose,
  onCreated,
}: EnvironmentCreateOverlayProps) {
  const { showAlert } = useAlertModal();
  const [formState, setFormState] = useState<EnvironmentFormState>(EMPTY_ENV_FORM);
  const [generation, setGeneration] =
    useState<GenerationFormState>(EMPTY_GENERATION);
  const [creating, setCreating] = useState(false);

  const resetForm = useCallback(() => {
    setFormState(EMPTY_ENV_FORM);
    setGeneration(EMPTY_GENERATION);
  }, []);

  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open, resetForm]);

  const updateField = <K extends keyof EnvironmentFormState>(
    key: K,
    value: EnvironmentFormState[K],
  ) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!formState.name.trim()) {
      showAlert({ message: t("environments.create.nameRequired", "Please enter a name"), variant: "warning" });
      return;
    }

    try {
      setCreating(true);
      const payload: EnvironmentCreate = {
        name: formState.name.trim(),
        category: formState.category || undefined,
        tags: formState.tags?.filter(Boolean),
        description: formState.description?.trim() || undefined,
        reference_images: formState.reference_images?.filter(Boolean),
      };
      const res = await storyStructureAPI.createEnvironment(payload);
      if (!res.success || !res.data) {
        showAlert({ message: res.error || t("common.createFailed", "Create failed"), variant: "error" });
        return;
      }

      const created = res.data;
      onCreated(created);

      if (generation.enabled) {
        const envKey = created.business_id || created.id;
        const genRes = await storyStructureAPI.generateEnvironmentImagesAsync(
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
          },
        );
        if (genRes.success) {
          showAlert({
            message: t("environments.create.successWithGeneration", "Created successfully and submitted the reference image generation task"),
            variant: "success",
          });
        } else {
          showAlert({
            message: `${t("environments.create.successButGenerationFailed", "Created successfully, but image task submission failed")}: ${genRes.error || t("common.pleaseRetryLater", "please try again later")}`,
            variant: "warning",
          });
        }
      } else {
        showAlert({ message: t("common.createSuccess", "Created successfully"), variant: "success" });
      }

      resetForm();
      onClose();
    } catch (error) {
      console.error(error);
      showAlert({ message: t("common.createFailed", "Create failed"), variant: "error" });
    } finally {
      setCreating(false);
    }
  };

  return (
    <CreationOverlay
      open={open}
      title={t("environments.create.title", "Create Environment")}
      subtitle={t("environments.create.subtitle", "Create reusable environment assets")}
      onClose={onClose}
      widthClassName="max-w-5xl"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
          {t("environments.create.notice", "After creation, the environment enters the asset pool and can be bound to specific scenes during episode production.")}
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700">
              {t("common.name", "Name")} *
            </label>
            <input
              type="text"
              value={formState.name}
              onChange={(e) => updateField("name", e.target.value)}
              className={operatorInputClass("w-full")}
              placeholder={t("environments.create.namePlaceholder", "For example: office, campus, shopping mall")}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700">
              {t("common.category", "Category")}
            </label>
            <select
              value={formState.category}
              onChange={(e) => updateField("category", e.target.value)}
              className={operatorSelectClass("w-full")}
            >
              <option value="indoor">{t("environments.create.indoor", "Indoor")}</option>
              <option value="outdoor">{t("environments.create.outdoor", "Outdoor")}</option>
              <option value="other">{t("environments.create.other", "Other")}</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700">
              {t("environments.create.tagsLabel", "Tags (comma separated)")}
            </label>
            <input
              type="text"
              value={(formState.tags || []).join(", ")}
              onChange={(e) =>
                updateField(
                  "tags",
                  e.target.value
                    .split(",")
                    .map((t) => t.trim())
                    .filter(Boolean),
                )
              }
              className={operatorInputClass("w-full")}
              placeholder={t("environments.create.tagsPlaceholder", "modern, office building, open plan")}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700">
              {t("environments.create.referencesLabel", "Reference Image URLs (comma separated)")}
            </label>
            <input
              type="text"
              value={(formState.reference_images || []).join(", ")}
              onChange={(e) =>
                updateField(
                  "reference_images",
                  e.target.value
                    .split(",")
                    .map((t) => t.trim())
                    .filter(Boolean),
                )
              }
              className={operatorInputClass("w-full")}
              placeholder="http://.../bg1.png, http://.../bg2.png"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-700">
            {t("common.description", "Description")}
          </label>
          <textarea
            value={formState.description}
            onChange={(e) => updateField("description", e.target.value)}
            className={operatorInputClass(
              "h-auto min-h-20 w-full py-2 text-sm",
            )}
            rows={3}
            placeholder={t("environments.create.descriptionPlaceholder", "Briefly describe the environment's mood, lighting, and style")}
          />
        </div>

        <EnvironmentGenerationFields
          envKey=""
          generation={generation}
          setGeneration={setGeneration}
        />

        <div className="flex justify-end gap-3 border-t pt-4">
          <button
            type="button"
            onClick={() => {
              resetForm();
              onClose();
            }}
            className={operatorButtonClass("secondary")}
          >
            {t("common.cancel", "Cancel")}
          </button>
          <button
            type="submit"
            disabled={creating}
            className={operatorButtonClass("primary")}
          >
            {creating ? t("environments.create.creating", "Creating...") : t("environments.create.submit", "Create Environment")}
          </button>
        </div>
      </form>
    </CreationOverlay>
  );
}
