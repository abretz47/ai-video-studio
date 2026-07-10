"use client";

import type { Script } from "@/utils/api/types";
import type {
  ScriptScene,
  ScriptDialogue,
  ScriptDirection,
} from "@/hooks/useScriptDetail";
import { toSceneNumber } from "@/hooks/useScriptDetail";
import { formatText } from "@/components/features/StoryboardFrameCard";
import { OperatorPanel, OperatorSectionHeader } from "@/components/shared";

interface ScriptOverviewTabProps {
  script: Script;
  scenes: ScriptScene[];
  dialogues: ScriptDialogue[];
  directions: ScriptDirection[];
}

export function ScriptOverviewTab({
  script,
  scenes,
  dialogues,
  directions,
}: ScriptOverviewTabProps) {
  return (
    <Section title="Script overview" description="Quick view of script content and core elements">
      <div className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold text-gray-700">Script excerpt</h3>
          <div className="mt-2 max-h-72 overflow-auto rounded-md border border-gray-200 bg-gray-50 p-3 text-xs leading-6 text-gray-700">
            {(script.content || "No content yet")
              .split("\n")
              .slice(0, 120)
              .map((line, idx) => (
                <p key={idx} className="whitespace-pre-wrap">
                  {line}
                </p>
              ))}
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-700">
              Scene summary ({scenes.length})
            </h3>
            <div className="mt-2 max-h-60 space-y-2 overflow-auto">
              {scenes.length === 0 && (
                <p className="text-sm text-gray-500">No structured scenes yet</p>
              )}
              {scenes.slice(0, 6).map((scene, idx) => (
                <div
                  key={idx}
                  className="rounded-md border border-gray-200 bg-gray-50 p-3 text-sm text-gray-700"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">
                      Scene {toSceneNumber(scene.scene_number) ?? idx + 1}
                    </span>
                    {scene.location && (
                      <span className="text-xs text-gray-500">
                        {scene.location}
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    {formatText(scene.description, "No description yet", 140)}
                  </p>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Dialogue
              </h4>
              <p className="mt-1 text-lg font-semibold text-gray-900">
                {dialogues.length}
              </p>
              {dialogues.slice(0, 2).map((dialogue, idx) => (
                <p key={idx} className="mt-1 text-xs text-gray-500">
                  {typeof dialogue === "string"
                    ? dialogue
                    : formatText(dialogue.content, "No dialogue yet", 80)}
                </p>
              ))}
            </div>
            <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Stage directions
              </h4>
              <p className="mt-1 text-lg font-semibold text-gray-900">
                {directions.length}
              </p>
              {directions.slice(0, 2).map((direction, idx) => (
                <p key={idx} className="mt-1 text-xs text-gray-500">
                  {typeof direction === "string"
                    ? direction
                    : formatText(direction.content, "No content yet", 80)}
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}

function Section({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <OperatorPanel>
      <OperatorSectionHeader title={title} subtitle={description} />
      {children}
    </OperatorPanel>
  );
}
