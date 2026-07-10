"use client";

import type { ImageGenerationFormState } from "@/hooks/useVirtualIPImages";

interface ImageGenerationOptionsFieldsProps {
  generateForm: ImageGenerationFormState;
  setGenerateForm: React.Dispatch<
    React.SetStateAction<ImageGenerationFormState>
  >;
  maxCount?: number;
}

export function ImageGenerationOptionsFields({
  generateForm,
  setGenerateForm,
  maxCount,
}: ImageGenerationOptionsFieldsProps) {
  const effectiveMaxCount =
    typeof maxCount === "number" && maxCount > 0 ? maxCount : 4;
  const countOptions = Array.from(
    { length: effectiveMaxCount },
    (_, index) => index + 1,
  );

  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Image Category
        </label>
        <select
          value={generateForm.category}
          onChange={(e) =>
            setGenerateForm((prev) => ({ ...prev, category: e.target.value }))
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="portrait">Portrait</option>
          <option value="full_body">Full Body</option>
          <option value="scene">Scene</option>
          <option value="action">Action</option>
          <option value="emotion">Emotion</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Generation Count
        </label>
        <select
          value={generateForm.count ?? 1}
          onChange={(e) =>
            setGenerateForm((prev) => ({
              ...prev,
              count: Math.min(
                effectiveMaxCount,
                Math.max(1, Number(e.target.value) || 1),
              ),
            }))
          }
          disabled={effectiveMaxCount <= 1}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {countOptions.map((value) => (
            <option key={value} value={value}>
              {value} images
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Up to {effectiveMaxCount} images images per run; some models may return multiple candidates.
        </p>
      </div>

      <div className="md:col-span-3">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional prompts (optional, comma separated)
        </label>
        <input
          type="text"
          value={generateForm.additional_prompts}
          onChange={(e) =>
            setGenerateForm((prev) => ({
              ...prev,
              additional_prompts: e.target.value,
            }))
          }
          placeholder="For example: smiling, sunny, outdoors"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="md:col-span-3">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={generateForm.is_default}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                is_default: e.target.checked,
              }))
            }
            className="mr-2"
          />
          <span className="text-sm text-gray-700">Set as Default Image</span>
        </label>
      </div>
    </>
  );
}
