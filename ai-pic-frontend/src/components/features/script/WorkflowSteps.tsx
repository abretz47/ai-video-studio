"use client";

import { t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorSectionHeader,
  operatorButtonClass,
} from "@/components/shared";

interface WorkflowStepsProps {
  onGoToSceneDetails: () => void;
  onGoToSceneStructure: () => void;
  onGoToTimelineSupport: () => void;
}

export function WorkflowSteps({
  onGoToSceneDetails,
  onGoToSceneStructure,
  onGoToTimelineSupport,
}: WorkflowStepsProps) {
  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title={t("script.workflow.title", "Production Entry Points")}
        subtitle={t("script.workflow.subtitle", "Text, structure, and storyboard entry points in one place")}
      />
      <div className="grid gap-3 p-4 md:grid-cols-3">
        <StepCard
          label={t("script.workflow.sceneText", "Scene text details")}
          detail={t("script.workflow.sceneTextDetail", "Review dialogue and stage directions.")}
          onClick={onGoToSceneDetails}
        />
        <StepCard
          label={t("script.workflow.structuredScenes", "Structured scenes / shots")}
          detail={t("script.workflow.structuredScenesDetail", "Adjust beats and shot ordering.")}
          onClick={onGoToSceneStructure}
        />
        <StepCard
          label={t("script.workflow.timeline", "Timeline mainline")}
          detail={t("script.workflow.timelineDetail", "Jump from the timeline into storyboard support and asset replacement.")}
          onClick={onGoToTimelineSupport}
        />
      </div>
    </OperatorPanel>
  );
}

function StepCard({
  label,
  detail,
  onClick,
}: {
  label: string;
  detail: string;
  onClick: () => void;
}) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
      <div className="text-sm font-medium text-gray-950">{label}</div>
      <p className="mt-1 text-xs text-gray-500">{detail}</p>
      <button
        type="button"
        onClick={onClick}
        className={operatorButtonClass("secondary", "mt-3")}
      >
        {t("common.open", "Open")}
      </button>
    </div>
  );
}
