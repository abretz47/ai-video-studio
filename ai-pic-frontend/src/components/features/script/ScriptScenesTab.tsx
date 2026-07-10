"use client";

import { t } from "@/lib/i18n";
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
        <OperatorContextRail
          title={t("script.scenes.sceneList", "Scene List")}
          subtitle={t("script.scenes.sceneCount", "{count} total").replace("{count}", String(props.scenes.length))}
        >
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
                      {t("common.sceneWithNumber", "Scene {number}").replace("{number}", String(sceneNumber))}
                    </span>
                    <StatusPill tone="gray">
                      {t("script.scenes.dialogueCount", "{count} lines").replace("{count}", String(filterByScene(props.dialogues, sceneNumber).length))}
                    </StatusPill>
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs text-gray-500">
                    {formatText(scene.description, t("common.noDescription", "No description"), 100)}
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
              title={
                props.activeScene
                  ? t("common.sceneWithNumber", "Scene {number}").replace("{number}", String(activeNumber || ""))
                  : t("script.scenes.sceneDetails", "Scene Details")
              }
              subtitle={props.activeScene?.location || t("script.scenes.selectScenePrompt", "Select a scene on the left to view details")}
            />
            <div className="space-y-4 p-4">
              {props.activeScene ? (
                <>
                  <p className="text-sm leading-6 text-gray-700">
                    {formatText(props.activeScene.description, t("script.scenes.noSceneDescription", "No scene description"), 500)}
                  </p>
                  <ContentBlock title={t("script.overview.dialogue", "Dialogue")} items={sceneDialogues} empty={t("script.scenes.noDialogue", "No dialogue")}/>
                  <ContentBlock title={t("script.overview.stageDirections", "Stage Directions")} items={sceneDirections} empty={t("script.scenes.noStageDirections", "No stage directions")}/>
                </>
              ) : (
                <OperatorState title={t("script.scenes.selectScene", "Select a scene")} detail={t("script.scenes.selectSceneDetail", "Use the list on the left to locate script scenes.")} />
              )}
            </div>
          </OperatorPanel>
        </OperatorMainCanvas>
      }
      inspector={
        <OperatorInspector
          title={t("script.scenes.structureCheck", "Structure Check")}
          subtitle={t("script.scenes.structureSubtitle", "Beats, shots, and normalized scenes")}
          action={
            <button
              type="button"
              onClick={() => props.setShowStructureEditor(!props.showStructureEditor)}
              className={operatorButtonClass("secondary")}
            >
              {props.showStructureEditor
                ? t("common.collapse", "Collapse")
                : t("common.edit", "Edit")}
            </button>
          }
        >
          {props.structureLoading ? <OperatorState title={t("script.scenes.loadingStructuredScenes", "Loading structured scenes...")} /> : null}
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
              {typeof item === "string"
                ? item
                : `${item.character || t("common.character", "Character")}: ${item.content || ""}`}
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
    return <OperatorState title={t("script.scenes.noNormalizedScene", "No normalized scene matched")} tone="amber" />;
  }
  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
        <div className="text-sm font-medium text-gray-950">
          {scene.slug_line || t("common.sceneWithNumber", "Scene {number}").replace("{number}", String(scene.scene_number))}
        </div>
        <div className="mt-1 text-xs text-gray-500">
          {t("script.scenes.beatAndShotCount", "Beats {beats} · Shots {shots}").replace("{beats}", String(beats?.length || 0)).replace("{shots}", String(shots?.length || 0))}
        </div>
      </div>
    </div>
  );
}
