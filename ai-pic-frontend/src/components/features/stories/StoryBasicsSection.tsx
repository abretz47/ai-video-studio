"use client";

import { useState, type Dispatch, type SetStateAction } from "react";
import { t } from "@/lib/i18n";
import type { StoryGenerationForm, StoryFormat } from "@/utils/storyOptions";
import { AIModelType } from "@/utils/api/types";
import { MarketingFields, MultiModelSelector } from "@/components/shared";
import { PACING_TEMPLATES } from "@/utils/marketingTemplates";
import { SHORT_DRAMA_STORY_TEMPLATES } from "@/utils/shortDramaTemplates";
import { STORY_FORMATS, STORY_GENRES } from "@/utils/storyOptions";

interface StoryBasicsSectionProps {
  generateForm: StoryGenerationForm;
  setGenerateForm: Dispatch<SetStateAction<StoryGenerationForm>>;
}

export function StoryBasicsSection({
  generateForm,
  setGenerateForm,
}: StoryBasicsSectionProps) {
  const [storyTemplateId, setStoryTemplateId] = useState("");

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.titleLabel", "Story title *")}
          </label>
          <input
            type="text"
            value={generateForm.title}
            onChange={(e) =>
              setGenerateForm((prev) => ({ ...prev, title: e.target.value }))
            }
            placeholder={t("stories.basics.titlePlaceholder", "Enter a story title")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.genreLabel", "Story genre")}
          </label>
          <select
            value={generateForm.genre}
            onChange={(e) =>
              setGenerateForm((prev) => ({ ...prev, genre: e.target.value }))
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {STORY_GENRES.map((genre) => (
              <option key={genre.value} value={genre.value}>
                {genre.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.formatLabel", "Story format")}
          </label>
          <select
            value={generateForm.story_format}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                story_format: e.target.value as StoryFormat,
              }))
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {STORY_FORMATS.map((format) => (
              <option key={format.value} value={format.value}>
                {format.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {t("stories.basics.formatHelper", "Selecting a format automatically applies the matching backend prompt variant (short drama / series / film).")}
          </p>
        </div>

        {generateForm.story_format === "short_drama" ? (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t("stories.basics.templateLabel", "Short drama story template (optional)")}
            </label>
            <select
              value={storyTemplateId}
              onChange={(e) => {
                const value = e.target.value;
                setStoryTemplateId(value);
                const template = SHORT_DRAMA_STORY_TEMPLATES.find(
                  (item) => item.id === value,
                );
                if (!template) return;

                setGenerateForm((prev) => {
                  const next: StoryGenerationForm = {
                    ...prev,
                    ...template.defaults,
                    story_format: "short_drama",
                  };
                  const pacingId = template.defaults.pacing_template;
                  if (pacingId) {
                    const pacing = PACING_TEMPLATES.find(
                      (item) => item.id === pacingId,
                    );
                    if (pacing) {
                      next.pacing_template = pacing.id;
                      next.hook_plan = pacing.hookPlan;
                      next.twist_density = pacing.twistDensity ?? "";
                      next.cliffhanger_plan = pacing.cliffhangerPlan ?? [];
                      next.ad_snippets = pacing.adSnippets ?? [];
                    }
                  }
                  return next;
                });
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t("stories.basics.noTemplate", "No template")}</option>
              {SHORT_DRAMA_STORY_TEMPLATES.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {SHORT_DRAMA_STORY_TEMPLATES.find(
                (item) => item.id === storyTemplateId,
              )?.description || t("stories.basics.templateHelper", "Selecting a template auto-fills market, micro-genre, pacing, and extra requirements.")}
            </p>
          </div>
        ) : null}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.themeLabel", "Theme")}
          </label>
          <input
            type="text"
            value={generateForm.theme}
            onChange={(e) =>
              setGenerateForm((prev) => ({ ...prev, theme: e.target.value }))
            }
            placeholder={t("stories.basics.themePlaceholder", "For example: friendship, growth, adventure")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.audienceLabel", "Target audience")}
          </label>
          <input
            type="text"
            value={generateForm.target_audience}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                target_audience: e.target.value,
              }))
            }
            placeholder={t("stories.basics.audiencePlaceholder", "For example: teens, adults, female audience")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <MarketingFields
        form={generateForm}
        setForm={setGenerateForm}
        title={t("stories.basics.marketingTitle", "Market / micro-genre / pacing template")}
        idPrefix="story"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.durationLabel", "Estimated total duration (minutes)")}
          </label>
          <input
            type="number"
            value={generateForm.duration_minutes}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                duration_minutes: parseInt(e.target.value) || 30,
              }))
            }
            min="1"
            max="300"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <MultiModelSelector
          label={t("stories.basics.modelLabel", "Select model")}
          value={generateForm.model ? [generateForm.model] : []}
          onChange={(ids) =>
            setGenerateForm((prev) => ({ ...prev, model: ids[0] || "" }))
          }
          modelType={AIModelType.Text}
          multiple={false}
          helperText={t("stories.basics.modelHelper", "Leave empty to let the backend choose the best provider and model automatically (JSON Schema-capable models are recommended for story generation).")}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("stories.basics.temperatureLabel", "Temperature (0.0 - 1.5)")}
          </label>
          <input
            type="range"
            min="0"
            max="1.5"
            step="0.1"
            value={generateForm.temperature ?? 0.7}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                temperature: parseFloat(e.target.value),
              }))
            }
            className="w-full"
          />
          <div className="text-sm text-gray-600">
            {t("stories.basics.temperatureCurrent", "Current temperature: {value}").replace("{value}", generateForm.temperature?.toFixed(1) ?? "0.7")}
          </div>
        </div>
      </div>
    </div>
  );
}
