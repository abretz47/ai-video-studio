"use client";

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
        title="Production entry points"
        subtitle="Text, structure, and storyboard entry points are organized in one place"
      />
      <div className="grid gap-3 p-4 md:grid-cols-3">
        <StepCard
          label="Scene text details"
          detail="Review dialogue and stage directions."
          onClick={onGoToSceneDetails}
        />
        <StepCard
          label="Structured scenes / shots"
          detail="Adjust pacing and shot order."
          onClick={onGoToSceneStructure}
        />
        <StepCard
          label="Main timeline"
          detail="Enter storyboard assist and asset replacement from the timeline."
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
        Open
      </button>
    </div>
  );
}
