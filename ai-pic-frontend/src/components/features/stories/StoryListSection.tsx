"use client";

import Link from "next/link";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
  operatorSelectClass,
} from "@/components/shared";
import { GENRES, STATUSES } from "@/hooks/useStories";
import type { Story, StoryCharacter } from "@/utils/api/types";
import { storyDisplayText } from "./StoryProductionModel";
import { storyCharacterDisplayName } from "./StoryProductionDetailParts";

interface StoryListSectionProps {
  stories: Story[];
  loading: boolean;
  selectedGenre: string;
  onSelectedGenreChange: (value: string) => void;
  selectedStatus: string;
  onSelectedStatusChange: (value: string) => void;
  onOpenGenerateForm: () => void;
  onDelete: (businessId: string) => void;
}

export function StoryListSection({
  stories,
  loading,
  selectedGenre,
  onSelectedGenreChange,
  selectedStatus,
  onSelectedStatusChange,
  onOpenGenerateForm,
  onDelete,
}: StoryListSectionProps) {
  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title="Story List"
        subtitle={`${stories.length} stories`}
        action={
          <StoryFilters
            selectedGenre={selectedGenre}
            onSelectedGenreChange={onSelectedGenreChange}
            selectedStatus={selectedStatus}
            onSelectedStatusChange={onSelectedStatusChange}
          />
        }
      />

      {loading ? (
        <div className="p-4">
          <OperatorState title="Loading story list..." />
        </div>
      ) : stories.length === 0 ? (
        <StoryEmptyState onOpenGenerateForm={onOpenGenerateForm} />
      ) : (
        <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
          {stories.map((story) => (
            <StoryProjectCard
              key={story.business_id || story.id}
              story={story}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </OperatorPanel>
  );
}

function StoryFilters({
  selectedGenre,
  onSelectedGenreChange,
  selectedStatus,
  onSelectedStatusChange,
}: {
  selectedGenre: string;
  onSelectedGenreChange: (value: string) => void;
  selectedStatus: string;
  onSelectedStatusChange: (value: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <select
        value={selectedGenre}
        onChange={(event) => onSelectedGenreChange(event.target.value)}
        className={operatorSelectClass("w-32")}
        aria-label="Filter stories by genre"
      >
        <option value="">All genres</option>
        {GENRES.map((genre) => (
          <option key={genre.value} value={genre.value}>
            {genre.label}
          </option>
        ))}
      </select>
      <select
        value={selectedStatus}
        onChange={(event) => onSelectedStatusChange(event.target.value)}
        className={operatorSelectClass("w-32")}
        aria-label="Filter stories by status"
      >
        <option value="">All statuses</option>
        {STATUSES.map((status) => (
          <option key={status.value} value={status.value}>
            {status.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function StoryEmptyState({
  onOpenGenerateForm,
}: {
  onOpenGenerateForm: () => void;
}) {
  return (
    <div className="p-4">
      <OperatorState
        title="No stories yet"
        detail="Create a story from IP first, then open its detail page to generate episodes."
        action={
          <button
            type="button"
            onClick={onOpenGenerateForm}
            className={operatorButtonClass("primary")}
          >
            Create from IP
          </button>
        }
      />
    </div>
  );
}

function StoryProjectCard({
  story,
  onDelete,
}: {
  story: Story;
  onDelete: (businessId: string) => void;
}) {
  const storyKey = story.business_id || String(story.id);
  const linkedCharacters = story.story_characters || story.characters || [];

  return (
    <article className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-gray-950">
            {story.title}
          </h3>
          <p className="mt-1 text-xs text-gray-500">
            {story.genre || "Uncategorized"}
            {story.theme ? ` · ${story.theme}` : ""}
          </p>
        </div>
        <StatusPill tone={story.status === "published" ? "green" : "gray"}>
          {story.status || "draft"}
        </StatusPill>
      </div>

      <p className="mt-4 line-clamp-3 text-sm leading-6 text-gray-600">
        {storyDisplayText(story.synopsis, story.premise)}
      </p>

      <StoryCharacterChips characters={linkedCharacters} />

      <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-3">
        <span className="text-xs text-gray-500">
          Updated {new Date(story.updated_at).toLocaleDateString("zh-CN")}
        </span>
        <div className="flex gap-2">
          <Link
            href={`/stories/${storyKey}?generate=episodes#episode-generation`}
            className={operatorButtonClass("primary", "whitespace-nowrap")}
          >
            Generate Episodes
          </Link>
          <Link
            href={`/stories/${storyKey}`}
            className={operatorButtonClass("ghost", "whitespace-nowrap")}
          >
            Details
          </Link>
          <button
            type="button"
            onClick={() => onDelete(storyKey)}
            className="h-8 whitespace-nowrap rounded-md px-2 text-xs font-medium text-red-600 hover:bg-red-50"
          >
            Delete
          </button>
        </div>
      </div>
    </article>
  );
}

function StoryCharacterChips({ characters }: { characters: StoryCharacter[] }) {
  if (!characters.length) {
    return (
      <div className="mt-4">
        <span className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700">
          No linked IP yet
        </span>
      </div>
    );
  }

  return (
    <div className="mt-4 flex flex-wrap gap-2">
      {characters.slice(0, 3).map((character) => (
        <span
          key={character.id}
          className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-600"
        >
          IP: {storyCharacterDisplayName(character)}
        </span>
      ))}
      {characters.length > 3 ? (
        <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-600">
          +{characters.length - 3}
        </span>
      ) : null}
    </div>
  );
}
