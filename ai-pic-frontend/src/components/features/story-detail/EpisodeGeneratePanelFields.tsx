"use client";

import type { Dispatch, ReactNode, SetStateAction } from "react";
import {
  MarketingFields,
  MultiModelSelector,
  operatorInputClass,
  operatorSelectClass,
  operatorTextareaClass,
} from "@/components/shared";
import type { EpisodeGenForm } from "@/hooks/useStoryDetail";

export function EpisodeGeneratePanelFields({
  genForm,
  setGenForm,
}: {
  genForm: EpisodeGenForm;
  setGenForm: Dispatch<SetStateAction<EpisodeGenForm>>;
}) {
  return (
    <>
      <div className="grid grid-cols-1 gap-3">
        <NumberField
          label="Generate Episode"
          min={1}
          max={100}
          value={genForm.episode_count}
          onChange={(value) =>
            setGenForm((prev) => ({ ...prev, episode_count: value || 1 }))
          }
        />
        <NumberField
          label="Duration per episode (minutes)"
          min={1}
          max={120}
          value={genForm.episode_duration}
          onChange={(value) =>
            setGenForm((prev) => ({ ...prev, episode_duration: value || 30 }))
          }
        />
        <SelectField
          label="Complexity"
          value={genForm.plot_complexity}
          options={[
            ["simple", "Simple"],
            ["medium", "Medium"],
            ["complex", "Complex"],
          ]}
          onChange={(value) =>
            setGenForm((prev) => ({ ...prev, plot_complexity: value }))
          }
        />
        <SelectField
          label="Pacing"
          value={genForm.pacing}
          options={[
            ["slow", "Slow"],
            ["medium", "Medium"],
            ["fast", "Fast"],
          ]}
          onChange={(value) => setGenForm((prev) => ({ ...prev, pacing: value }))}
        />
        <MultiModelSelector
          label="Model"
          value={genForm.model ? [genForm.model] : []}
          onChange={(ids) =>
            setGenForm((prev) => ({ ...prev, model: ids[0] || "" }))
          }
          modelType="text"
          multiple={false}
          helperText="Leave empty to let the backend recommend the best model"
        />
        <div>
          <FieldLabel>Temperature ({genForm.temperature.toFixed(1)})</FieldLabel>
          <input
            type="range"
            min={0}
            max={1.5}
            step={0.1}
            value={genForm.temperature}
            onChange={(event) =>
              setGenForm((prev) => ({
                ...prev,
                temperature: parseFloat(event.target.value),
              }))
            }
            className="w-full"
          />
        </div>
      </div>
      <MarketingFields
        form={genForm}
        setForm={setGenForm}
        title="Market / Micro-genre / Pacing Template"
        idPrefix="episode"
      />
      <div>
        <FieldLabel>Additional Requirements</FieldLabel>
        <textarea
          value={genForm.additional_requirements}
          onChange={(event) =>
            setGenForm((prev) => ({
              ...prev,
              additional_requirements: event.target.value,
            }))
          }
          rows={2}
          className={operatorTextareaClass("w-full")}
        />
      </div>
    </>
  );
}

function NumberField({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(parseInt(event.target.value, 10))}
        className={operatorInputClass("w-full")}
      />
    </div>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<[string, string]>;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={operatorSelectClass("w-full")}
      >
        {options.map(([optionValue, labelText]) => (
          <option key={optionValue} value={optionValue}>
            {labelText}
          </option>
        ))}
      </select>
    </div>
  );
}

function FieldLabel({ children }: { children: ReactNode }) {
  return (
    <label className="mb-1 block text-xs font-medium text-gray-600">
      {children}
    </label>
  );
}
