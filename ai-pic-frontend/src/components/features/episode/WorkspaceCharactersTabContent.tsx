"use client";

import { useState } from "react";
import { useEpisodeCharacters } from "@/hooks/useEpisodeCharacters";
import type {
  AutoCreatedCharacter,
  EpisodeCharacter,
  EpisodeCharacterCreate,
  EpisodeCharacterUpdate,
} from "@/utils/api/types";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  operatorButtonClass,
} from "@/components/shared";
import { CharacterFormModal } from "./CharacterFormModal";
import { CharacterRow } from "./CharacterRow";

interface WorkspaceCharactersTabContentProps {
  episodeId: number | string;
  autoCreatedCharacters?: AutoCreatedCharacter[];
}

export function WorkspaceCharactersTabContent({
  episodeId,
  autoCreatedCharacters = [],
}: WorkspaceCharactersTabContentProps) {
  const {
    characters,
    loading,
    error,
    total,
    createCharacter,
    updateCharacter,
    deleteCharacter,
  } = useEpisodeCharacters({ episodeId, autoLoad: true });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingCharacter, setEditingCharacter] =
    useState<EpisodeCharacter | null>(null);
  const [showAutoCreated, setShowAutoCreated] = useState(
    autoCreatedCharacters.length > 0,
  );

  const handleCreate = async (data: EpisodeCharacterCreate) => {
    const result = await createCharacter(data);
    if (result) setIsCreateModalOpen(false);
  };

  const handleUpdate = async (
    characterId: number | string,
    data: EpisodeCharacterUpdate,
  ) => {
    const result = await updateCharacter(characterId, data);
    if (result) setEditingCharacter(null);
  };

  const handleDelete = async (characterId: number | string) => {
    if (confirm("Are you sure you want to delete this temporary character?")) {
      await deleteCharacter(characterId, "Deleted manually by user");
    }
  };

  if (loading && characters.length === 0) {
    return <OperatorState title="Loading temporary characters..." />;
  }

  return (
    <div className="space-y-4">
      {showAutoCreated && autoCreatedCharacters.length > 0 ? (
        <OperatorState
          title={`${autoCreatedCharacters.length} temporary characters were created automatically`}
          detail="These characters were identified from script dialogue. You can continue refining their image and voice assets."
          tone="blue"
          action={
            <button
              type="button"
              onClick={() => setShowAutoCreated(false)}
              className={operatorButtonClass("ghost")}
            >
              Close
            </button>
          }
        />
      ) : null}

      <OperatorPanel>
        <OperatorSectionHeader
          title="Temporary character management"
          subtitle="Manage temporary characters appearing in this episode, such as the Courier and passersby"
          action={
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(true)}
              className={operatorButtonClass("primary")}
            >
              Add character
            </button>
          }
        />
        {error ? (
          <div className="p-4">
            <OperatorState title={error} tone="red" />
          </div>
        ) : null}
        {characters.length === 0 ? (
          <div className="p-4">
            <OperatorState title="No temporary characters yet" detail="Click Add character to create one." />
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {characters.map((character) => (
              <CharacterRow
                key={character.id}
                character={character}
                onEdit={() => setEditingCharacter(character)}
                onDelete={() => handleDelete(character.id)}
              />
            ))}
          </div>
        )}
        {total > 0 ? (
          <div className="border-t border-gray-200 px-4 py-3 text-center text-xs text-gray-500">
            {total} temporary characters in total
          </div>
        ) : null}
      </OperatorPanel>

      {isCreateModalOpen ? (
        <CharacterFormModal
          mode="create"
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreate}
          title="Add temporary character"
        />
      ) : null}
      {editingCharacter ? (
        <CharacterFormModal
          mode="edit"
          isOpen
          onClose={() => setEditingCharacter(null)}
          onSubmit={(data) => handleUpdate(editingCharacter.id, data)}
          initialData={editingCharacter}
          title="Edit temporary character"
        />
      ) : null}
    </div>
  );
}
