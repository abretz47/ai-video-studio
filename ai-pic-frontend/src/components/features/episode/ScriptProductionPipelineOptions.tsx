import type { ScriptGenerationRequest } from "@/utils/api/types";
import { OperatorState } from "@/components/shared";

interface ScriptProductionPipelineOptionsProps {
  generateForm: ScriptGenerationRequest;
  setGenerateForm: React.Dispatch<
    React.SetStateAction<ScriptGenerationRequest>
  >;
  useAsync: boolean;
}

export function ScriptProductionPipelineOptions({
  generateForm,
  setGenerateForm,
  useAsync,
}: ScriptProductionPipelineOptionsProps) {
  return (
    <div className="mb-4">
      <OperatorState
        title="Production Async Pipeline"
        detail="Async generation runs script scoring, automatic fixes, and can continue into audio tracks, timeline, and storyboard placeholders."
        action={
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={generateForm.auto_timeline_pipeline ?? true}
            disabled={!useAsync}
            onChange={(e) =>
              setGenerateForm((prev) => ({
                ...prev,
                auto_timeline_pipeline: e.target.checked,
                generation_mode: "production",
              }))
            }
          />
          Automatically generate timeline and storyboard placeholders
        </label>
        }
      />
    </div>
  );
}
