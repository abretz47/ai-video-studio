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
      await deleteCharacter(characterId, "User manual delete");
    }
  };

  if (loading && characters.length === 0) {
    return <OperatorState title="Loading temporary characters..." />;
  }

  return (
    <div className="space-y-4">
      {showAutoCreated && autoCreatedCharacters.length > 0 ? (
        <OperatorState
          title={`Automatically created ${autoCreatedCharacters.length}Temporary Characters`}
          detail="These characters were detected from script dialogue and can be completed with image and voice resources."
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
          title="Temporary Role Management"
          subtitle="Manage temporary characters that appear in this episode, such as couriers and passersby"
          action={
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(true)}
              className={operatorButtonClass("primary")}
            >
              AddCharacter
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
            <OperatorState title="No temporary characters yet" detail="Click Add Character to create one." />
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
            Total {total}Temporary Characters
          </div>
        ) : null}
      </OperatorPanel>

      {isCreateModalOpen ? (
        <CharacterFormModal
          mode="create"
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreate}
          title="AddTemporary Characters"
        />
      ) : null}
      {editingCharacter ? (
        <CharacterFormModal
          mode="edit"
          isOpen
          onClose={() => setEditingCharacter(null)}
          onSubmit={(data) => handleUpdate(editingCharacter.id, data)}
          initialData={editingCharacter}
          title="Edit Temporary Characters"
        />
      ) : null}
    </div>
  );
}
