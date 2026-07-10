"use client";

import type { ReactNode } from "react";
import type { Script } from "@/utils/api/types";
import { formatDate } from "@/hooks/useScriptDetail";
import {
  OperatorPanel,
  OperatorSectionHeader,
  operatorButtonClass,
} from "@/components/shared";

interface ScriptHeaderProps {
  script: Script;
  showExportMenu: boolean;
  setShowExportMenu: (show: boolean) => void;
  onExport: (format: string) => void;
  onNavigateToEpisode: () => void;
  onNavigateToTimeline: () => void;
}

export function ScriptHeader({
  script,
  showExportMenu,
  setShowExportMenu,
  onExport,
  onNavigateToEpisode,
  onNavigateToTimeline,
}: ScriptHeaderProps) {
  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title="Script asset"
        subtitle={`Script #${script.id}`}
        action={
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onNavigateToEpisode}
              className={operatorButtonClass("secondary")}
            >
              Back to episode
            </button>
            <button
              type="button"
              onClick={onNavigateToTimeline}
              className={operatorButtonClass("secondary")}
            >
              Go to timeline
            </button>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowExportMenu(!showExportMenu)}
                className={operatorButtonClass("primary")}
              >
                Export script
              </button>
              {showExportMenu && (
                <div className="absolute right-0 z-10 mt-2 w-36 overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg">
                  {["txt", "pdf", "docx"].map((format) => (
                    <button
                      key={format}
                      type="button"
                      onClick={() => onExport(format)}
                      className="block w-full px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50"
                    >
                      Export {format.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        }
      />
      <div className="p-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <h1 className="truncate text-lg font-semibold text-gray-950">
              {script.title}
            </h1>
            <p className="mt-1 text-xs text-gray-500">
              {script.format_type?.toUpperCase() || "SCRIPT"} ·{" "}
              {script.language?.toUpperCase()} · Version {script.version || "1.0"}
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <InfoCard
            label="Word count"
            value={script.word_count || 0}
            hint="Word total"
          />
          <InfoCard
            label="Character count"
            value={script.character_count || 0}
            hint="Character total"
          />
          <InfoCard
            label="Page count"
            value={script.page_count || 0}
            hint="Estimated pages"
          />
          <InfoCard
            label="Status"
            value={
              script.status === "published"
                ? "Published"
                : script.status === "approved"
                ? "Approved"
                : "Draft"
            }
            tone={
              script.status === "published"
                ? "success"
                : script.status === "approved"
                ? "warning"
                : "default"
            }
            hint={
              script.status === "draft"
                ? "Editable"
                : script.status === "approved"
                ? "Pending publication"
                : "No changes needed"
            }
          />
        </div>
        <div className="mt-4 grid grid-cols-1 gap-2 text-xs text-gray-500 md:grid-cols-2">
          <div>Created at: {formatDate(script.created_at)}</div>
          <div>Updated at: {formatDate(script.updated_at)}</div>
        </div>
      </div>
    </OperatorPanel>
  );
}

function InfoCard({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: "default" | "success" | "warning";
}) {
  const toneClass =
    tone === "success"
      ? "border-green-200 bg-green-50 text-green-700"
      : tone === "warning"
      ? "border-yellow-200 bg-yellow-50 text-yellow-700"
      : "border-gray-200 bg-gray-50 text-gray-900";
  return (
    <div className={`rounded-md border p-3 ${toneClass}`}>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-6">{value}</div>
      {hint && <div className="mt-1 text-xs text-gray-500">{hint}</div>}
    </div>
  );
}
