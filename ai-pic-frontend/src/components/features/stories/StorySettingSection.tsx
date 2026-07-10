"use client";

import type { Dispatch, SetStateAction } from "react";
import type { VirtualIP } from "@/utils/api/types";
import type { StoryGenerationForm } from "@/utils/storyOptions";
import { STORY_ASPECT_RATIOS } from "@/utils/storyOptions";
import { CharacterSelector } from "./CharacterSelector";

interface StorySettingSectionProps {
  virtualIPs: VirtualIP[];
  generateForm: StoryGenerationForm;
  setGenerateForm: Dispatch<SetStateAction<StoryGenerationForm>>;
  onCharacterToggle: (characterId: number) => void;
  onNavigateToVirtualIP: () => void;
}

export function StorySettingSection({
  virtualIPs,
  generateForm,
  setGenerateForm,
  onCharacterToggle,
  onNavigateToVirtualIP,
}: StorySettingSectionProps) {
  return (
    <div className="space-y-4">
      <CharacterSelector
        virtualIPs={virtualIPs}
        selectedIds={generateForm.character_ids}
        onToggle={onCharacterToggle}
        onNavigateToVirtualIP={onNavigateToVirtualIP}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Period
          </label>
          <input
            type="text"
            value={generateForm.setting_time}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                setting_time: e.target.value,
              }))
            }
            placeholder="e.g. modern, ancient, future"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Default Aspect Ratio
          </label>
          <select
            value={generateForm.default_aspect_ratio}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                default_aspect_ratio: e.target
                  .value as StoryGenerationForm["default_aspect_ratio"],
              }))
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {STORY_ASPECT_RATIOS.map((ratio) => (
              <option key={ratio.value} value={ratio.value}>
                {ratio.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Used by default for storyboard images/videos and can be overridden during generation
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={generateForm.setting_location}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                setting_location: e.target.value,
              }))
            }
            placeholder="e.g. school, city, countryside"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Worldbuilding
        </label>
        <textarea
          value={generateForm.world_building}
          onChange={(e) =>
            setGenerateForm((prev) => ({
              ...prev,
              world_building: e.target.value,
            }))
          }
          placeholder="Describe the story's world and background"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Requirements
        </label>
        <textarea
          value={generateForm.additional_requirements}
          onChange={(e) =>
            setGenerateForm((prev) => ({
              ...prev,
              additional_requirements: e.target.value,
            }))
          }
          placeholder="Other special requirements or preferences"
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}
