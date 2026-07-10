"use client";

import type { ReactNode } from "react";
import {
  OperatorSectionHeader,
  operatorButtonClass,
} from "@/components/shared";
import { GenerationTaskStatusLine } from "@/components/shared/notifications";
import type { EpisodeGenForm } from "@/hooks/useStoryDetail";
import {
  EpisodeContextPackPreview,
  type EpisodeContextPackPreviewProps,
} from "./EpisodeContextPackPreview";
import { EpisodeGeneratePanelFields } from "./EpisodeGeneratePanelFields";

interface EpisodeGeneratePanelProps {
  genOpen: boolean;
  setGenOpen: (open: boolean) => void;
  genForm: EpisodeGenForm;
  setGenForm: React.Dispatch<React.SetStateAction<EpisodeGenForm>>;
  useAsync: boolean;
  setUseAsync: (value: boolean) => void;
  promptPreview: string;
  onPreviewPrompt: () => void;
  onGenerate: () => void;
  canGenerate?: boolean;
  contextPackPreviewProps: EpisodeContextPackPreviewProps;
  readinessPanel?: ReactNode;
  episodesTask?: {
    taskId: number;
    phase: string;
    error: string | null;
  } | null;
}

export function EpisodeGeneratePanel({
  genOpen,
  setGenOpen,
  genForm,
  setGenForm,
  useAsync,
  setUseAsync,
  promptPreview,
  onPreviewPrompt,
  onGenerate,
  canGenerate = true,
  contextPackPreviewProps,
  readinessPanel,
  episodesTask,
}: EpisodeGeneratePanelProps) {
  return (
    <div className="space-y-4">
      <GenerationTaskStatusLine label="Episode" task={episodesTask} />
      <OperatorSectionHeader
        title="Generate Episode"
        subtitle="Inherit the current IP and story context"
        className="border border-gray-200 bg-white"
        action={
          <button
            type="button"
            onClick={() => setGenOpen(!genOpen)}
            className={operatorButtonClass("ghost")}
          >
            {genOpen ? "Collapse" : "Expand"}
          </button>
        }
      />
      {genOpen && (
        <div className="space-y-4">
          {readinessPanel}

          <EpisodeGeneratePanelFields
            genForm={genForm}
            setGenForm={setGenForm}
          />

          <div className="flex items-center gap-4">
            <label className="text-sm text-gray-700 flex items-center gap-2">
              <input
                type="checkbox"
                checked={useAsync}
                onChange={(e) => setUseAsync(e.target.checked)}
              />{" "}
              Async Task
            </label>
          </div>

          <EpisodeContextPackPreview {...contextPackPreviewProps} />

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onPreviewPrompt}
              className={operatorButtonClass("secondary")}
            >
              Prompt Preview
            </button>
            <button
              type="button"
              onClick={onGenerate}
              disabled={!canGenerate}
              className={operatorButtonClass("primary")}
              title={!canGenerate ? "Please fix critical readiness issues first" : undefined}
            >
              Start Generation
            </button>
          </div>
          {promptPreview && (
            <div className="mt-3 whitespace-pre-wrap rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-700">
              {promptPreview}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
