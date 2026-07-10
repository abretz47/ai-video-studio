"use client";

import type {
  NormalizedScene,
  NormalizedShot,
  SceneBeat,
  Script,
} from "@/utils/api/types";
import type {
  ScriptDialogue,
  ScriptDirection,
  ScriptScene,
} from "@/hooks/useScriptDetail";
import { toSceneNumber } from "@/hooks/useScriptDetail";
import { formatText } from "@/components/features/StoryboardFrameCard";
import {
  OperatorContextRail,
  OperatorInspector,
  OperatorListRow,
  OperatorMainCanvas,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  OperatorWorkspace,
  StatusPill,
  operatorButtonClass,
} from "@/components/shared";
import { SceneStructurePanel, type SceneNode } from "../SceneStructurePanel";

interface ScriptScenesTabProps {
  script: Script;
  scenes: ScriptScene[];
  dialogues: ScriptDialogue[];
  directions: ScriptDirection[];
  focusedScene: number | null;
  setFocusedScene: (scene: number) => void;
  activeScene: ScriptScene | null;
  selectedNormalizedScene: NormalizedScene | undefined;
  sceneBeats: SceneBeat[] | undefined;
  sceneShots: NormalizedShot[] | undefined;
  structureLoading: boolean;
  structureError: string | null;
  showStructureEditor: boolean;
  setShowStructureEditor: (show: boolean) => void;
  canEditStructure: boolean;
  setStructuredScenes: (scenes: SceneNode[]) => void;
}

export function ScriptScenesTab(props: ScriptScenesTabProps) {
  const activeNumber = toSceneNumber(props.activeScene?.scene_number);
  const sceneDialogues = filterByScene(props.dialogues, activeNumber);
  const sceneDirections = filterByScene(props.directions, activeNumber);

  return (
    <OperatorWorkspace
      variant="rail-main-inspector"
      className="h-[calc(100vh-18rem)] min-h-[560px]"
      rail={
        <OperatorContextRail title="Scene List" subtitle={`${props.scenes.length} total`}>
          <div className="space-y-2">
            {props.scenes.map((scene, index) => {
              const sceneNumber = toSceneNumber(scene.scene_number) ?? index + 1;
              return (
                <OperatorListRow
                  key={`${sceneNumber}-${index}`}
                  selected={props.focusedScene === sceneNumber}
                  onClick={() => props.setFocusedScene(sceneNumber)}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-gray-950">
                      Scene {sceneNumber}
                    </span>
                    <StatusPill tone="gray">
                      {filterByScene(props.dialogues, sceneNumber).length} lines
                    </StatusPill>
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs text-gray-500">
                    {formatText(scene.description, "No description yet", 100)}
                  </p>
                </OperatorListRow>
              );
            })}
          </div>
        </OperatorContextRail>
      }
      main={
        <OperatorMainCanvas className="space-y-4">
          <OperatorPanel>
            <OperatorSectionHeader
              title={props.activeScene ? `Scene ${activeNumber || ""}` : "Scene Details"}
              subtitle={props.activeScene?.location || "Select a scene on the left to view details"}
            />
            <div className="space-y-4 p-4">
              {props.activeScene ? (
                <>
                  <p className="text-sm leading-6 text-gray-700">
                    {formatText(props.activeScene.description, "No scene description yet", 500)}
                  </p>
                  <ContentBlock title="Dialogue" items={sceneDialogues} empty="No dialogue yet" />
                  <ContentBlock title="Stage Directions" items={sceneDirections} empty="No stage directions yet" />
                </>
              ) : (
                <OperatorState title="Select a scene" detail="Use the list on the left to navigate script scenes." />
              )}
            </div>
          </OperatorPanel>
        </OperatorMainCanvas>
      }
      inspector={
        <OperatorInspector
          title="Structure Check"
          subtitle="Beats, shots, and normalized scenes"
          action={
            <button
              type="button"
              onClick={() => props.setShowStructureEditor(!props.showStructureEditor)}
              className={operatorButtonClass("secondary")}
            >
              {props.showStructureEditor ? "Collapse" : "Edit"}
            </button>
          }
        >
          {props.structureLoading ? <OperatorState title="Loading structured scenes..." /> : null}
          {props.structureError ? <OperatorState title={props.structureError} tone="red" /> : null}
          <StructureSummary
            scene={props.selectedNormalizedScene}
            beats={props.sceneBeats}
            shots={props.sceneShots}
          />
          {props.showStructureEditor ? (
            <div className="mt-4">
              <SceneStructurePanel
                scriptId={props.script.id}
                canEdit={props.canEditStructure}
                onStructureLoaded={props.setStructuredScenes}
              />
            </div>
          ) : null}
        </OperatorInspector>
      }
    />
  );
}

function filterByScene<T extends string | { scene_number?: unknown }>(
  items: T[],
  sceneNumber?: number,
) {
  if (!sceneNumber) return [];
  return items.filter((item) => {
    if (typeof item === "string") return false;
    const candidate = item.scene_number;
    return toSceneNumber(
      typeof candidate === "string" || typeof candidate === "number"
        ? candidate
        : undefined,
    ) === sceneNumber;
  });
}

function ContentBlock({
  title,
  items,
  empty,
}: {
  title: string;
  items: Array<string | { character?: string; content?: string }>;
  empty: string;
}) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
      <div className="mt-2 space-y-2">
        {items.length ? (
          items.map((item, index) => (
            <div key={index} className="rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-700">
              {typeof item === "string" ? item : `${item.character || "Character"}: ${item.content || ""}`}
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

function StructureSummary({
  scene,
  beats,
  shots,
}: {
  scene?: NormalizedScene;
  beats?: SceneBeat[];
  shots?: NormalizedShot[];
}) {
  if (!scene) {
    return <OperatorState title="No normalized scene matched" tone="amber" />;
  }
  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
        <div className="text-sm font-medium text-gray-950">
          {scene.slug_line || `Scene ${scene.scene_number}`}
        </div>
        <div className="mt-1 text-xs text-gray-500">
          Beats {beats?.length || 0} · Shots {shots?.length || 0}
        </div>
      </div>
    </div>
  );
}
