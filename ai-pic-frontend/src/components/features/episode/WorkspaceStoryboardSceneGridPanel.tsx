"use client";

import { OperatorPanel, OperatorSectionHeader } from "@/components/shared";
import type { NormalizedScene } from "@/utils/api/types";
import {
  SceneGridCharacterPicker,
  SceneGridResult,
} from "./WorkspaceStoryboardSceneGridParts";
import { useWorkspaceSceneGridGeneration } from "./useWorkspaceSceneGridGeneration";

type ShowAlert = (options: {
  message: string;
  variant: "info" | "success" | "warning" | "error";
}) => void;

const GRID_SIZE_OPTIONS = [6, 9, 12, 16];

export function WorkspaceStoryboardSceneGridPanel({
  episodeKey,
  selectedScriptId,
  normalizedScenes,
  showAlert,
}: {
  episodeKey?: string;
  selectedScriptId?: number | null;
  normalizedScenes: NormalizedScene[];
  showAlert?: ShowAlert;
}) {
  const {
    expanded,
    setExpanded,
    grids,
    sceneNumber,
    setSceneNumber,
    sceneNumbers,
    gridSize,
    setGridSize,
    imageModel,
    setImageModel,
    characters,
    selectedIpIds,
    setSelectedIpIds,
    environmentUrls,
    setEnvironmentUrls,
    submitting,
    sheetActive,
    videoActive,
    currentGrid,
    handleGenerateSheet,
    handleGenerateVideo,
  } = useWorkspaceSceneGridGeneration({
    episodeKey,
    selectedScriptId,
    normalizedScenes,
    showAlert,
  });

  if (!selectedScriptId || !sceneNumbers.length) return null;

  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title="Scene Storyboard Grid"
        subtitle="Generate a storyboard grid image for each scene, then use Seedance to create a continuous final cut from the grid"
        action={
          <button
            type="button"
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-800"
            onClick={() => setExpanded((prev) => !prev)}
          >
            {expanded ? "Collapse" : "Expand"}
          </button>
        }
      />
      {!expanded ? null : (
        <>
          <div className="mt-4 flex flex-wrap items-end gap-3 text-sm">
            <label className="flex flex-col gap-1 text-xs text-gray-600">
              Scene
              <select
                className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                value={sceneNumber ?? ""}
                onChange={(event) => setSceneNumber(Number(event.target.value))}
              >
                {sceneNumbers.map((value) => (
                  <option key={value} value={value}>
                    Scene {value}
                    {grids[String(value)]?.image_url ? " · Generated" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs text-gray-600">
              Grid Count
              <select
                className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                value={gridSize}
                onChange={(event) => setGridSize(Number(event.target.value))}
              >
                {GRID_SIZE_OPTIONS.map((value) => (
                  <option key={value} value={value}>
                    {value} Panels
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs text-gray-600">
              Image Model
              <select
                className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                value={imageModel}
                onChange={(event) => setImageModel(event.target.value)}
              >
                <option value="codex:gpt-image-2">gpt-image-2 (Codex)</option>
                <option value="gpt-image-2">gpt-image-2 (API key)</option>
                <option value="">Default Route</option>
              </select>
            </label>
            <button
              type="button"
              className="rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
              disabled={submitting || sheetActive}
              onClick={() => void handleGenerateSheet()}
            >
              {sheetActive ? "Generating Grid…" : "Generate Storyboard Grid"}
            </button>
            <button
              type="button"
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-800 disabled:opacity-50"
              disabled={submitting || videoActive || !currentGrid?.image_url}
              onClick={() => void handleGenerateVideo()}
            >
              {videoActive ? "Generating Final Cut…" : "Generate Final Cut from Grid"}
            </button>
          </div>

          <SceneGridCharacterPicker
            characters={characters}
            selectedIpIds={selectedIpIds}
            onToggle={(ipId, checked) =>
              setSelectedIpIds((prev) =>
                checked
                  ? [...prev, ipId]
                  : prev.filter((value) => value !== ipId),
              )
            }
          />

          <label className="mt-3 flex flex-col gap-1 text-xs text-gray-600">
            Environment Reference Image URLs (optional, separated by commas or new lines; leave blank to auto-fill from the scene environment)
            <input
              className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              placeholder="https://…"
              value={environmentUrls}
              onChange={(event) => setEnvironmentUrls(event.target.value)}
            />
          </label>

          {currentGrid ? (
            <SceneGridResult grid={currentGrid} sceneNumber={sceneNumber} />
          ) : null}
        </>
      )}
    </OperatorPanel>
  );
}
