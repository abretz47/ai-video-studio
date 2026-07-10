"use client";

import type { EpisodeCharacter } from "@/utils/api/types";
import { StatusPill, operatorButtonClass } from "@/components/shared";
import { episodeCharacterDisplayName } from "./episodeCharacterDisplay";

interface CharacterRowProps {
  character: EpisodeCharacter;
  onEdit: () => void;
  onDelete: () => void;
}

export function CharacterRow({
  character,
  onEdit,
  onDelete,
}: CharacterRowProps) {
  const importanceLabels = ["", "Minor", "Important", "Main", "Core", "Key"];
  const displayName = episodeCharacterDisplayName(character);

  return (
    <div className="p-4 hover:bg-gray-50">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-gray-900">{displayName}</h3>
            <StatusPill tone={character.importance >= 4 ? "blue" : "gray"}>
              {importanceLabels[character.importance] || "Minor"}
            </StatusPill>
            {character.role_type && (
              <StatusPill tone="gray">{character.role_type}</StatusPill>
            )}
          </div>

          <div className="mt-2 space-y-1 text-sm">
            {character.personality && (
              <div>
                <span className="font-medium text-gray-700">Personality:</span>
                <span className="text-gray-600">{character.personality}</span>
              </div>
            )}
            {character.background && (
              <div>
                <span className="font-medium text-gray-700">Background:</span>
                <span className="text-gray-600">{character.background}</span>
              </div>
            )}
            {character.appearance_override && (
              <div>
                <span className="font-medium text-gray-700">Appearance:</span>
                <span className="text-gray-600">
                  {character.appearance_override}
                </span>
              </div>
            )}
            {character.voice_config_override && (
              <div>
                <span className="font-medium text-gray-700">Voice:</span>
                <span className="text-gray-600">
                  {character.voice_config_override.provider} /{" "}
                  {character.voice_config_override.voice_id}
                </span>
              </div>
            )}
            {character.scene_appearances &&
              character.scene_appearances.length > 0 && (
                <div>
                  <span className="font-medium text-gray-700">
                    Appears in Scenes:
                  </span>
                  <span className="text-gray-600">
                    Scene {character.scene_appearances.join(", ")}
                  </span>
                </div>
              )}
          </div>

          <div className="mt-2 text-xs text-gray-500">
            Linked Virtual IP: {character.virtual_ip_business_id} · Created{" "}
            {new Date(character.created_at).toLocaleDateString()}
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          <button
            type="button"
            onClick={onEdit}
            className={operatorButtonClass("secondary")}
          >
            Edit
          </button>
          <button
            type="button"
            onClick={onDelete}
            className={operatorButtonClass("ghost", "text-red-700")}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
