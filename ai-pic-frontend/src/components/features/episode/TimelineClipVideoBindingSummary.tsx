"use client";

import type { EpisodeCharacter } from "@/utils/api/types";
import { episodeCharacterDisplayName } from "./episodeCharacterDisplay";

export function TimelineClipVideoBindingSummary({
  episodeCharacters,
  selectedCharacterVirtualIpIds,
  selectedCharacterReferenceUrls,
  selectedEnvironmentReferenceUrls,
}: {
  episodeCharacters: EpisodeCharacter[];
  selectedCharacterVirtualIpIds: number[];
  selectedCharacterReferenceUrls: string[];
  selectedEnvironmentReferenceUrls: string[];
}) {
  const characterLabels = selectedCharacterLabels(
    episodeCharacters,
    selectedCharacterVirtualIpIds,
  );
  const hasAnyBinding =
    characterLabels.length > 0 ||
    selectedCharacterReferenceUrls.length > 0 ||
    selectedEnvironmentReferenceUrls.length > 0;

  return (
    <div
      aria-label="Video generation binding context"
      className="rounded-md border border-blue-100 bg-blue-50/60 px-2.5 py-2 text-[11px] text-gray-700"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="text-xs font-semibold text-gray-900">
          Video generation binding context
        </div>
        <span
          className={[
            "shrink-0 rounded-full px-2 py-0.5 font-medium",
            hasAnyBinding
              ? "bg-blue-100 text-blue-700"
              : "bg-gray-100 text-gray-600",
          ].join(" ")}
        >
          {hasAnyBinding ? "Bindings included" : "Pending"}
        </span>
      </div>
      <div className="mt-2 grid gap-1">
        <BindingLine
          label="Character IP"
          value={characterLabels.length ? characterLabels.join(", ") : "Not bound"}
          ready={characterLabels.length > 0}
        />
        <BindingLine
          label="IP images"
          value={`${selectedCharacterReferenceUrls.length} images`}
          ready={selectedCharacterReferenceUrls.length > 0}
        />
        <BindingLine
          label="Environment images"
          value={`${selectedEnvironmentReferenceUrls.length} images`}
          ready={selectedEnvironmentReferenceUrls.length > 0}
        />
      </div>
      <div className="mt-2 leading-4 text-gray-500">
        {hasAnyBinding
          ? "The video task will include the selected IPs and environment images above."
          : "Bind character IPs and environment images in the clip storyboard above first, and the video task will include them."}
      </div>
    </div>
  );
}

function BindingLine({
  label,
  value,
  ready,
}: {
  label: string;
  value: string;
  ready: boolean;
}) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2">
      <span className="truncate">
        {label}: {value}
      </span>
      <span className={ready ? "text-blue-700" : "text-gray-500"}>
        {ready ? "Bound" : "Pending"}
      </span>
    </div>
  );
}

function selectedCharacterLabels(
  episodeCharacters: EpisodeCharacter[],
  selectedCharacterVirtualIpIds: number[],
) {
  return selectedCharacterVirtualIpIds.map((virtualIpId) => {
    const character = episodeCharacters.find(
      (item) => item.virtual_ip_id === virtualIpId,
    );
    return character
      ? episodeCharacterDisplayName(character)
      : `IP ${virtualIpId}`;
  });
}
