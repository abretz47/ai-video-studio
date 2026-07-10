import {
  motionTimelineLabel,
  type ShotPlanPromptLayers,
} from "./WorkspaceStoryboardPromptLayers";

export function PromptLayerSummary({
  layers,
}: {
  layers: ShotPlanPromptLayers | null;
}) {
  if (!layers) return null;
  const motion = motionTimelineLabel(layers);
  return (
    <div className="mt-3 rounded-md border border-gray-200 bg-gray-50 p-3 text-[11px] text-gray-600">
      <div className="font-semibold text-gray-900">Five Prompt Layers</div>
      <div className="mt-2 grid gap-1 sm:grid-cols-2">
        <PromptLayerValue label="Direction" value={layers.directionAnchor} />
        <PromptLayerValue label="Reference" value={layers.aestheticReference} />
        <PromptLayerValue label="Composition" value={layers.compositionGeometry} />
        <PromptLayerValue label="Emotion" value={layers.emotionalLanding} />
      </div>
      {motion ? <div className="mt-2 text-gray-700">{motion}</div> : null}
    </div>
  );
}

function PromptLayerValue({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div>
      <span className="text-gray-500">{label}：</span>
      <span className="text-gray-800">{value}</span>
    </div>
  );
}
