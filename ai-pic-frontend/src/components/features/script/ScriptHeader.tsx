"use client";

import type { ReactNode } from "react";
import { t } from "@/lib/i18n";
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
        title={t("script.header.title", "Script Asset")}
        subtitle={t("script.header.subtitle", "Script #{id}").replace("{id}", String(script.id))}
        action={
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onNavigateToEpisode}
              className={operatorButtonClass("secondary")}
            >
              {t("script.header.backToEpisode", "Back to episode")}
            </button>
            <button
              type="button"
              onClick={onNavigateToTimeline}
              className={operatorButtonClass("secondary")}
            >
              {t("script.header.openTimeline", "Open timeline")}
            </button>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowExportMenu(!showExportMenu)}
                className={operatorButtonClass("primary")}
              >
                {t("script.header.exportScript", "Export script")}
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
                      {t("script.header.exportFormat", "Export {format}").replace("{format}", format.toUpperCase())}
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
              {script.format_type?.toUpperCase() || t("common.script", "Script")} ·{" "}
              {script.language?.toUpperCase()} · {t("common.version", "Version")} {script.version || "1.0"}
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <InfoCard
            label={t("script.header.wordCount", "Word count")}
            value={script.word_count || 0}
            hint={t("script.header.wordCountHint", "Word count")}
          />
          <InfoCard
            label={t("script.header.characterCount", "Character count")}
            value={script.character_count || 0}
            hint={t("script.header.characterCountHint", "Character count")}
          />
          <InfoCard
            label={t("script.header.pageCount", "Pages")}
            value={script.page_count || 0}
            hint={t("script.header.pageCountHint", "Estimated pages")}
          />
          <InfoCard
            label={t("common.status", "Status")}
            value={
              script.status === "published"
                ? t("common.status.published", "Published")
                : script.status === "approved"
                ? t("common.status.approved", "Approved")
                : t("common.status.draft", "Draft")
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
                ? t("script.header.draftHint", "Editable")
                : script.status === "approved"
                ? t("script.header.approvedHint", "Pending publish")
                : t("script.header.publishedHint", "No revision needed")
            }
          />
        </div>
        <div className="mt-4 grid grid-cols-1 gap-2 text-xs text-gray-500 md:grid-cols-2">
          <div>{t("common.createdAt", "Created")}: {formatDate(script.created_at)}</div>
          <div>{t("common.updatedAt", "Updated")}: {formatDate(script.updated_at)}</div>
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
