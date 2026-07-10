"use client";

import type { Dispatch, SetStateAction } from "react";
import type {
  EpisodeCharacterCreate,
  EpisodeCharacterUpdate,
} from "@/utils/api/types";

export function CharacterCommonFields<
  T extends EpisodeCharacterCreate | EpisodeCharacterUpdate,
>({
  formData,
  setFormData,
}: {
  formData: T;
  setFormData: Dispatch<SetStateAction<T>>;
}) {
  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Character Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          required
          value={formData.character_name || ""}
          onChange={(e) =>
            setFormData({ ...formData, character_name: e.target.value })
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="For example: courier, doctor, passerby"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Character Type
          </label>
          <select
            value={formData.role_type || "temporary"}
            onChange={(e) =>
              setFormData({ ...formData, role_type: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="temporary">Temporary Characters</option>
            <option value="guest">Guest Role</option>
            <option value="extra">Extra</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Importance (1-5)
          </label>
          <input
            type="number"
            min="1"
            max="5"
            value={formData.importance || 1}
            onChange={(e) =>
              setFormData({
                ...formData,
                importance: Number(e.target.value),
              })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Personality Description
        </label>
        <textarea
          value={formData.personality || ""}
          onChange={(e) =>
            setFormData({ ...formData, personality: e.target.value })
          }
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="For example: warm, optimistic, diligent at work"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Background Story
        </label>
        <textarea
          value={formData.background || ""}
          onChange={(e) =>
            setFormData({ ...formData, background: e.target.value })
          }
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="For example: employee of a courier company responsible for this neighborhood"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Additional Appearance Notes
        </label>
        <textarea
          value={formData.appearance_override || ""}
          onChange={(e) =>
            setFormData({ ...formData, appearance_override: e.target.value })
          }
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="For example: wearing a uniform and carrying a delivery bag"
        />
      </div>
    </>
  );
}
