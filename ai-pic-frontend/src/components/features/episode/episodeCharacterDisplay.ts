import type { EpisodeCharacter } from "@/utils/api/types";

export function episodeCharacterDisplayName(
  character: EpisodeCharacter,
  fallback = "UntitledCharacter",
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
