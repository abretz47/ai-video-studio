"use client";

import { t } from "@/lib/i18n";
import { StatusPill } from "@/components/shared";
import type {
  StoryCharacter,
  VirtualIPEnvironmentLink,
} from "@/utils/api/types";

export function ReadyCell({ ready }: { ready: boolean }) {
  return (
    <td className="px-4 py-4">
      <StatusPill tone={ready ? "green" : "gray"}>
        {ready
          ? t("common.status.ready", "Ready")
          : t("common.status.notStarted", "Not started")}
      </StatusPill>
    </td>
  );
}

export function CharacterChip({ character }: { character: StoryCharacter }) {
  const name = storyCharacterDisplayName(character, t("stories.detail.unnamedIp", "Unnamed IP"));
  return (
    <span className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600">
      IP: {name}
    </span>
  );
}

export function storyCharacterDisplayName(
  character: StoryCharacter,
  fallback = t("stories.detail.unnamed", "Unnamed"),
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
        {t("stories.detail.environmentPending", "Environment assets pending")}
      </span>
    );
  }

  return (
    <>
      <span className="rounded-md border border-green-200 bg-green-50 px-2 py-1 text-xs text-green-700">
        {t("stories.detail.environmentAssetsCount", "{count} environment assets").replace("{count}", String(items.length))}
      </span>
      {items.slice(0, 3).map((link) => (
        <span
          key={link.environment_id}
          className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600"
        >
          {t("stories.detail.sceneLabel", "Scene")}: {link.environment.name}
        </span>
      ))}
    </>
  );
}
