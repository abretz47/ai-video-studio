"use client";

import {
  ModelSelector,
  OperatorModalFrame,
  OperatorTabs,
  OperatorToolbar,
  operatorButtonClass,
} from "@/components/shared";

type ScriptSubTab = "overview" | "scenes";

export function ScriptTabToolbar({
  activeSubTab,
  setActiveSubTab,
  onOpenRegenerate,
  regenerating,
  canRegenerate,
}: {
  activeSubTab: ScriptSubTab;
  setActiveSubTab: (tab: ScriptSubTab) => void;
  onOpenRegenerate: () => void;
  regenerating?: boolean;
  canRegenerate: boolean;
}) {
  return (
    <OperatorToolbar>
      <OperatorTabs
        tabs={[
          { key: "overview", label: "Overview" },
          { key: "scenes", label: "Scenes" },
        ]}
        active={activeSubTab}
        onChange={setActiveSubTab}
      />
      {canRegenerate ? (
        <button
          type="button"
          onClick={onOpenRegenerate}
          disabled={regenerating}
          className={operatorButtonClass("secondary")}
        >
          {regenerating ? "Regenerating..." : "Regenerate script"}
        </button>
      ) : null}
    </OperatorToolbar>
  );
}

export function ScriptRegenerateModal({
  open,
  model,
  setModel,
  regenerating,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  model: string;
  setModel: (model: string) => void;
  regenerating?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;
  return (
    <OperatorModalFrame
      title="Regenerate script"
      subtitle="Create a new script using the latest classification optimizations"
      footer={
        <>
          <button
            type="button"
            onClick={onCancel}
            className={operatorButtonClass("secondary")}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={regenerating}
            className={operatorButtonClass("primary")}
          >
            Confirm regeneration
          </button>
        </>
      }
    >
      <ModelSelector
        value={model}
        onChange={setModel}
        label="Select model"
        helperText="Leave blank to use the existing model setting"
        allowAuto
        autoLabel="Use existing model"
        modelType="text"
      />
    </OperatorModalFrame>
  );
}
