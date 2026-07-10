"use client";

import type { EpisodeCharacter } from "@/utils/api/types";
import { episodeCharacterDisplayName } from "./episodeCharacterDisplay";

export function TimelineClipSharedReferenceContext({
  episodeCharacters,
  selectedCharacterVirtualIpIds,
  selectedCharacterReferenceUrls,
  selectedEnvironmentReferenceUrls,
  manualReferenceImages,
  onManualReferenceImagesChange,
}: {
  episodeCharacters: EpisodeCharacter[];
  selectedCharacterVirtualIpIds: number[];
  selectedCharacterReferenceUrls: string[];
  selectedEnvironmentReferenceUrls: string[];
  manualReferenceImages: string;
  onManualReferenceImagesChange: (value: string) => void;
}) {
  const labels = selectedCharacterVirtualIpIds.map((virtualIpId) => {
    const character = episodeCharacters.find(
      (item) => item.virtual_ip_id === virtualIpId,
    );
    return character ? episodeCharacterDisplayName(character) : `IP ${virtualIpId}`;
  });

  return (
    <section
      aria-label="Clip Shared Reference Context"
      className="mb-2 grid gap-2 rounded-md border border-slate-200 bg-white p-2 text-[11px] text-slate-700"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold text-slate-900">
          Clip Shared Reference Context
        </span>
        <span className="text-slate-500">Used for storyboard, start/end frames, and video tasks</span>
      </div>
      <div className="grid gap-1 min-[720px]:grid-cols-3">
        <span>Character IP: {labels.length ? labels.join("、") : "Not linked"}</span>
        <span>IP Images: {selectedCharacterReferenceUrls.length} images</span>
        <span>Environment Images: {selectedEnvironmentReferenceUrls.length} images</span>
      </div>
      <label className="grid gap-1 text-xs text-slate-700">
        <span>Additional reference image URLs (optional, one per line)</span>
        <textarea
          aria-label="Additional Reference Image URL"
          value={manualReferenceImages}
          onChange={(event) =>
            onManualReferenceImagesChange(event.currentTarget.value)
          }
          onInput={(event) =>
            onManualReferenceImagesChange(event.currentTarget.value)
          }
          rows={2}
          className="resize-none rounded-md border border-slate-200 px-2 py-1.5 text-xs outline-none focus:border-slate-400"
          placeholder="https://..."
        />
      </label>
    </section>
  );
}
