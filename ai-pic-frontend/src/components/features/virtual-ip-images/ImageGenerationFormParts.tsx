"use client";

import { operatorButtonClass } from "@/components/shared";

interface ImageGenerationActionsProps {
  generating: boolean;
  onGenerate: () => void;
  onCancel: () => void;
}

export function ImageGenerationActions({
  generating,
  onGenerate,
  onCancel,
}: ImageGenerationActionsProps) {
  return (
    <div className="flex flex-wrap gap-2 border-t border-gray-200 pt-3">
      <button
        type="button"
        onClick={onGenerate}
        disabled={generating}
        className={operatorButtonClass("primary")}
      >
        {generating ? "Submitting..." : "Submit Generation Task"}
      </button>
      <button
        type="button"
        onClick={onCancel}
        className={operatorButtonClass("secondary")}
      >
        Cancel
      </button>
    </div>
  );
}
