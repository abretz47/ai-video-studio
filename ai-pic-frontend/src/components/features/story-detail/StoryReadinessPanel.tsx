"use client";

import { useState } from "react";
import type {
  QuickFixResponse,
  ReadinessCheck,
  ReadinessResult,
} from "@/utils/api/types";
import {
  OperatorState,
  StatusPill,
  operatorButtonClass,
} from "@/components/shared";

interface StoryReadinessPanelProps {
  readiness: ReadinessResult | null;
  loading: boolean;
  error: string | null;
  quickFixLoading: boolean;
  onRefreshReadiness: () => void;
  onQuickFix: (dryRun: boolean) => Promise<QuickFixResponse | null>;
}

const fixableNames = new Set([
  "synopsis_present",
  "main_conflict_present",
  "setting_present",
  "world_building_present",
]);

const severityTone = (check: ReadinessCheck) => {
  if (check.passed) return "green";
  if (check.severity === "CRITICAL" || check.severity === "ERROR") return "red";
  if (check.severity === "WARNING") return "amber";
  return "blue";
};

export function StoryReadinessPanel({
  readiness,
  loading,
  error,
  quickFixLoading,
  onRefreshReadiness,
  onQuickFix,
}: StoryReadinessPanelProps) {
  const [showAllChecks, setShowAllChecks] = useState(false);
  const [quickFixPreview, setQuickFixPreview] =
    useState<QuickFixResponse | null>(null);

  if (loading) return <OperatorState title="Checking generation readiness..." />;
  if (error) {
    return (
      <OperatorState
        title={`Readiness check failed: ${error}`}
        tone="red"
        action={
          <button
            type="button"
            onClick={onRefreshReadiness}
            className={operatorButtonClass("secondary")}
          >
            Retry
          </button>
        }
      />
    );
  }
  if (!readiness) {
    return (
      <OperatorState
        title="Generation readiness has not been checked yet"
        action={
          <button
            type="button"
            onClick={onRefreshReadiness}
            className={operatorButtonClass("secondary")}
          >
            Start Check
          </button>
        }
      />
    );
  }

  const failedChecks = readiness.checks.filter((check) => !check.passed);
  const displayChecks = showAllChecks ? readiness.checks : failedChecks;
  const hasFixableIssues = readiness.checks.some(
    (check) => !check.passed && fixableNames.has(check.name),
  );

  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm font-medium text-gray-950">
              {readiness.summary}
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <StatusPill tone={readiness.ready ? "green" : "amber"}>
                Passed {readiness.passed_count}
              </StatusPill>
              <StatusPill tone={readiness.failed_count ? "red" : "gray"}>
                Failed {readiness.failed_count}
              </StatusPill>
              {readiness.warnings.length ? (
                <StatusPill tone="amber">
                  Warnings {readiness.warnings.length}
                </StatusPill>
              ) : null}
            </div>
          </div>
          <button
            type="button"
            onClick={onRefreshReadiness}
            className={operatorButtonClass("ghost")}
          >
            Refresh
          </button>
        </div>
      </div>

      {displayChecks.length ? (
        <div className="space-y-2">
          {displayChecks.map((check) => (
            <CheckItem key={check.name} check={check} />
          ))}
        </div>
      ) : (
        <OperatorState title="All checks passed" tone="green" />
      )}

      {readiness.passed_count > 0 ? (
        <button
          type="button"
          onClick={() => setShowAllChecks((value) => !value)}
          className={operatorButtonClass("ghost")}
        >
          {showAllChecks ? "Show only failed items" : `Show all ${readiness.checks.length} items`}
        </button>
      ) : null}

      {hasFixableIssues && !readiness.ready ? (
        <QuickFixBox
          preview={quickFixPreview}
          loading={quickFixLoading}
          onPreview={async () => setQuickFixPreview(await onQuickFix(true))}
          onCancel={() => setQuickFixPreview(null)}
          onApply={async () => {
            await onQuickFix(false);
            setQuickFixPreview(null);
            onRefreshReadiness();
          }}
        />
      ) : null}

      {!readiness.can_proceed ? (
        <OperatorState
          title="Critical issues block episode continuation"
          detail="Please resolve critical items first."
          tone="red"
        />
      ) : null}
    </div>
  );
}

function CheckItem({ check }: { check: ReadinessCheck }) {
  return (
    <div className="rounded-md border border-gray-200 bg-white p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-medium text-gray-900">{check.message}</div>
          {!check.passed && check.suggestion ? (
            <div className="mt-1 text-xs text-gray-500">{check.suggestion}</div>
          ) : null}
        </div>
        <StatusPill tone={severityTone(check)}>{check.severity}</StatusPill>
      </div>
    </div>
  );
}

function QuickFixBox({
  preview,
  loading,
  onPreview,
  onCancel,
  onApply,
}: {
  preview: QuickFixResponse | null;
  loading: boolean;
  onPreview: () => Promise<void>;
  onCancel: () => void;
  onApply: () => Promise<void>;
}) {
  if (!preview) {
    return (
      <button
        type="button"
        onClick={() => void onPreview()}
        disabled={loading}
        className={operatorButtonClass("primary")}
      >
        {loading ? "Generating..." : "Preview Fixes"}
      </button>
    );
  }
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
      <div className="text-sm font-medium text-gray-950">
        Will fix {preview.improvement.fixed_count} items
      </div>
      <div className="mt-2 space-y-1 text-xs text-gray-600">
        {preview.fixes_applied.slice(0, 4).map((fix, index) => (
          <div key={index}>
            {fix.field}: {fix.new_value.slice(0, 60)}
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <button
          type="button"
          onClick={() => void onApply()}
          disabled={loading}
          className={operatorButtonClass("primary")}
        >
          Confirm Apply
        </button>
        <button
          type="button"
          onClick={onCancel}
          className={operatorButtonClass("secondary")}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
