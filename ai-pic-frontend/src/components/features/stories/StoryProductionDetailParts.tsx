"use client";

import { StatusPill } from "@/components/shared";
import type {
  StoryCharacter,
  VirtualIPEnvironmentLink,
} from "@/utils/api/types";

export function ReadyCell({ ready }: { ready: boolean }) {
  return (
    <td className="px-4 py-4">
      <StatusPill tone={ready ? "green" : "gray"}>
        {ready ? "Ready" : "Not started"}
      </StatusPill>
    </td>
  );
}

export function CharacterChip({ character }: { character: StoryCharacter }) {
  const name = storyCharacterDisplayName(character, "Unnamed IP");
  return (
    <span className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600">
      IP: {name}
    </span>
  );
}

export function storyCharacterDisplayName(
  character: StoryCharacter,
  fallback = "Unnamed",
) {
  return (
    [
      character.character_name,
      character.display_name,
      character.name,
      character.virtual_ip_name,
    ]
      .find((value) => typeof value === "string" && value.trim())
      ?.trim() || fallback
  );
}

export function StoryEnvironmentCoverage({
  links,
}: {
  links: VirtualIPEnvironmentLink[];
}) {
  const unique = new Map<number, VirtualIPEnvironmentLink>();
  links.forEach((link) => unique.set(link.environment_id, link));
  const items = Array.from(unique.values());

  if (!items.length) {
    return (
      <span className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700">
        Environment pending integration
      </span>
    );
  }

  return (
    <>
      <span className="rounded-md border border-green-200 bg-green-50 px-2 py-1 text-xs text-green-700">
        {items.length} environment assets
      </span>
      {items.slice(0, 3).map((link) => (
        <span
          key={link.environment_id}
          className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600"
        >
          Scene: {link.environment.name}
        </span>
      ))}
    </>
  );
}
