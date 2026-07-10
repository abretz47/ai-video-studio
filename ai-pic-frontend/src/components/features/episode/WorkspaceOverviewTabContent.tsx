"use client";

import type { Episode } from "@/utils/api/types";
import {
  OperatorPanel,
  OperatorSectionHeader,
  StatusPill,
} from "@/components/shared";

interface PlotPoint {
  timing?: string;
  description?: string;
}

interface Conflict {
  intensity?: string;
  description?: string;
}

interface WorkspaceOverviewTabContentProps {
  episode: Episode;
  scriptSceneCount?: number;
}

export function WorkspaceOverviewTabContent({
  episode,
  scriptSceneCount,
}: WorkspaceOverviewTabContentProps) {
  const plotPoints = normalizeList<PlotPoint>(episode.plot_points);
  const conflicts = normalizeList<Conflict>(episode.conflicts);
  const characterArcs = episode.character_arcs || {};
  const sceneCount =
    typeof scriptSceneCount === "number" && scriptSceneCount >= 0
      ? scriptSceneCount
      : episode.scene_count;

  return (
    <div className="space-y-4">
      <OperatorPanel>
        <OperatorSectionHeader title="Episode Overview" subtitle="Basic information and generation summary" />
        <div className="space-y-4 p-4">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Metric label="Episode" value={`Episode ${episode.episode_number}`} />
            <Metric label="Duration" value={`${episode.duration_minutes || "—"} minutes`} />
            <Metric label="Scene Count" value={`${sceneCount || "—"}`} />
            <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
              <div className="text-xs text-gray-500">Status</div>
              <div className="mt-2">
                <StatusPill tone={episode.status === "published" ? "green" : "amber"}>
                  {episode.status === "published" ? "Published" : episode.status || "Draft"}
                </StatusPill>
              </div>
            </div>
          </div>
          {episode.summary ? (
            <p className="whitespace-pre-wrap text-sm leading-6 text-gray-700">
              {episode.summary}
            </p>
          ) : null}
        </div>
      </OperatorPanel>

      <OperatorPanel>
        <OperatorSectionHeader title="Story Beats" subtitle="plot points / conflicts" />
        <div className="grid gap-4 p-4 lg:grid-cols-2">
          <ListBlock
            title="Story Beats"
            items={plotPoints.map((point) =>
              point.timing ? `${point.timing}: ${point.description || ""}` : point.description || "",
            )}
            empty="No story beats yet"
          />
          <ListBlock
            title="Conflict Points"
            items={conflicts.map((conflict) =>
              conflict.intensity
                ? `${conflict.intensity}: ${conflict.description || ""}`
                : conflict.description || "",
            )}
            empty="No conflict points yet"
          />
        </div>
      </OperatorPanel>

      {Object.keys(characterArcs).length || episode.tags?.length ? (
        <OperatorPanel>
          <OperatorSectionHeader title="Characters and Tags" subtitle="Character arcs, tags, and metadata" />
          <div className="space-y-4 p-4">
            {Object.entries(characterArcs).map(([character, arc]) => (
              <div key={character} className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="text-sm font-medium text-gray-950">{character}</div>
                <div className="mt-1 text-xs text-gray-600">
                  {typeof arc === "string" ? arc : JSON.stringify(arc)}
                </div>
              </div>
            ))}
            {episode.tags?.length ? (
              <div className="flex flex-wrap gap-2">
                {episode.tags.map((tag, index) => (
                  <StatusPill key={`${tag}-${index}`} tone="gray">
                    {tag}
                  </StatusPill>
                ))}
              </div>
            ) : null}
          </div>
        </OperatorPanel>
      ) : null}
    </div>
  );
}

function normalizeList<T extends { description?: string }>(value: unknown): T[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => {
    if (item && typeof item === "object") return item as T;
    if (typeof item === "string") return { description: item } as T;
    return { description: JSON.stringify(item) } as T;
  });
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-gray-950">{value}</div>
    </div>
  );
}

function ListBlock({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <div>
      <div className="text-sm font-semibold text-gray-900">{title}</div>
      <div className="mt-2 space-y-2">
        {items.length ? (
          items.map((item, index) => (
            <div key={index} className="rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-700">
              {item || "-"}
            </div>
          ))
        ) : (
          <div className="rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-500">
            {empty}
          </div>
        )}
      </div>
    </div>
  );
}
