"use client";

import { t } from "@/lib/i18n";
import type { Script } from "@/utils/api/types";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
  operatorTableClass,
  operatorTableHeadClass,
  operatorTableRowClass,
} from "@/components/shared";
import {
  asRecord,
  buildCsv,
  getValue,
  toAdSnippets,
  toHookPlan,
  toNumber,
  toStringList,
} from "./scriptTrafficUtils";

interface ScriptTrafficTabProps {
  script: Script;
}

export function ScriptTrafficTab({ script }: ScriptTrafficTabProps) {
  const extra = asRecord(script.extra_metadata) ?? {};
  const params = asRecord(script.generation_params) ?? {};
  const scoring = asRecord(extra.scoring) ?? {};
  const marketRegion = getValue(extra, params, "market_region") as string | undefined;
  const microGenre = getValue(extra, params, "micro_genre") as string | undefined;
  const twistDensity = getValue(extra, params, "twist_density") as string | undefined;
  const cliffhangerPlan = toStringList(getValue(extra, params, "cliffhanger_plan"));
  const hookPlanRaw = getValue(extra, params, "hook_plan");
  const hookPlan = toHookPlan(hookPlanRaw);
  const hookPlanText = typeof hookPlanRaw === "string" ? hookPlanRaw : undefined;
  const adSnippets = toAdSnippets(getValue(extra, params, "ad_snippets"));
  const scorecard =
    asRecord(getValue(extra, params, "scorecard")) ||
    asRecord(getValue(extra, params, "script_score")) ||
    asRecord(getValue(extra, params, "hook_score")) ||
    asRecord(scoring.script_score);
  const overallScore = toNumber(
    scorecard?.overall_score ??
      scorecard?.score ??
      getValue(extra, params, "overall_score"),
  );
  const dimensionScores = asRecord(scorecard?.dimension_scores ?? scorecard?.scores);
  const strengths = toStringList(scorecard?.strengths ?? getValue(extra, params, "strengths"));
  const risks = toStringList(scorecard?.risks ?? getValue(extra, params, "risk_notes"));
  const rewriteGuidance = toStringList(
    scorecard?.rewrite_guidance ?? getValue(extra, params, "rewrite_guidance"),
  );

  const handleExport = () => {
    if (adSnippets.length === 0) return;
    const rows = adSnippets.map((snippet, idx) => ({
      asset_id: `asset-${idx + 1}`,
      duration_seconds: snippet.duration_seconds,
      hook: snippet.hook,
      visual_summary: snippet.visual_summary,
      call_to_action: snippet.call_to_action,
      market_region: marketRegion,
      micro_genre: microGenre,
    }));
    const blob = new Blob([buildCsv(rows)], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `traffic-sheet-${script.business_id || script.id}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <OperatorPanel>
        <OperatorSectionHeader title={t("script.traffic.scoreTitle", "Traffic Score")}
          subtitle={t("script.traffic.scoreSubtitle", "Market, micro-genre, and hook scoring")} />
        <div className="grid gap-3 p-4 md:grid-cols-3">
          <Metric label={t("script.traffic.marketGenre", "Market / Micro-genre")} value={marketRegion || t("common.unspecified", "Unspecified")} sub={microGenre || t("common.unspecified", "Unspecified")} />
          <Metric label={t("script.traffic.twistDensity", "Twist density")} value={twistDensity || t("common.emptyDash", "—")} />
          <Metric label={t("script.traffic.overallScore", "Overall score")} value={overallScore != null ? overallScore.toFixed(2) : t("common.emptyDash", "—")} />
        </div>
      </OperatorPanel>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperatorPanel>
          <OperatorSectionHeader title={t("script.traffic.breakdownTitle", "Score Breakdown")}
            subtitle={t("script.traffic.breakdownSubtitle", "Dimension scores and strengths")} />
          <div className="space-y-3 p-4">
            {dimensionScores ? (
              Object.entries(dimensionScores).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{key}</span>
                  <StatusPill tone="blue">{toNumber(value)?.toFixed(2) ?? String(value)}</StatusPill>
                </div>
              ))
            ) : (
              <OperatorState title={t("script.traffic.noBreakdown", "No score breakdown yet")} />
            )}
            <TextList title={t("script.traffic.strengths", "Strengths")} items={strengths} />
          </div>
        </OperatorPanel>
        <OperatorPanel>
          <OperatorSectionHeader title={t("script.traffic.riskTitle", "Risk Notes")}
            subtitle={t("script.traffic.riskSubtitle", "Risks and revision suggestions")} />
          <div className="space-y-3 p-4">
            <TextList title={t("script.traffic.risks", "Risks")} items={risks} empty={t("script.traffic.noRiskNotes", "No risk notes")}/>
            <TextList title={t("script.traffic.rewriteGuidance", "Revision Guidance")} items={rewriteGuidance} />
          </div>
        </OperatorPanel>
      </div>

      <OperatorPanel>
        <OperatorSectionHeader title={t("script.traffic.hookPlanTitle", "Hook / Pacing Plan")}
          subtitle={t("script.traffic.hookPlanSubtitle", "Generation params and extra metadata")} />
        <div className="grid gap-3 p-4 md:grid-cols-3">
          <Metric label={t("script.traffic.openingHook", "Opening hook")} value={hookPlan?.opening_hook || hookPlanText || t("common.emptyDash", "—")} />
          <Metric label={t("script.traffic.escalation", "Escalation")} value={hookPlan?.escalation_plan || t("common.emptyDash", "—")} />
          <Metric label={t("script.traffic.payoff", "Payoff")} value={hookPlan?.payoff_plan || t("common.emptyDash", "—")} />
        </div>
        <div className="space-y-3 px-4 pb-4">
          <TextList
            title={t("script.traffic.keyReversals", "Key Reversals")}
            items={(hookPlan?.key_reversals || []).map((beat) =>
              `${beat.description}${beat.timing ? ` (${beat.timing})` : ""}`,
            )}
          />
          <TextList title={t("script.traffic.cliffhangerPlan", "Cliffhangers")}
            items={cliffhangerPlan} />
        </div>
      </OperatorPanel>

      <OperatorPanel>
        <OperatorSectionHeader
          title={t("script.traffic.assetListTitle", "Traffic Asset List")}
          subtitle={t("script.traffic.assetCount", "{count} items").replace("{count}", String(adSnippets.length))}
          action={
            <button
              type="button"
              onClick={handleExport}
              disabled={adSnippets.length === 0}
              className={operatorButtonClass("secondary")}
            >
              {t("script.traffic.exportCsv", "Export CSV")}
            </button>
          }
        />
        {adSnippets.length === 0 ? (
          <div className="p-4"><OperatorState title={t("script.traffic.noAssets", "No traffic asset data yet")} /></div>
        ) : (
          <div className="overflow-x-auto p-4">
            <table className={operatorTableClass}>
              <thead className={operatorTableHeadClass}>
                <tr>
                  <th className="px-3 py-2 text-left">{t("common.duration", "Duration")}</th>
                  <th className="px-3 py-2 text-left">{t("script.traffic.coreHook", "Core Hook")}</th>
                  <th className="px-3 py-2 text-left">{t("script.traffic.visualSummary", "Visual Summary")}</th>
                  <th className="px-3 py-2 text-left">CTA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {adSnippets.map((snippet, idx) => (
                  <tr key={idx} className={operatorTableRowClass}>
                    <td className="px-3 py-2">{snippet.duration_seconds || t("common.emptyDash", "—")}s</td>
                    <td className="px-3 py-2">{snippet.hook}</td>
                    <td className="px-3 py-2">{snippet.visual_summary || t("common.emptyDash", "—")}</td>
                    <td className="px-3 py-2">{snippet.call_to_action || t("common.emptyDash", "—")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </OperatorPanel>
    </div>
  );
}

function Metric({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-2 text-sm font-medium text-gray-950">{value}</div>
      {sub ? <div className="mt-1 text-xs text-gray-500">{sub}</div> : null}
    </div>
  );
}

function TextList({ title, items, empty }: { title: string; items: string[]; empty?: string }) {
  if (!items.length && !empty) return null;
  return (
    <div>
      <div className="mb-2 text-xs font-medium text-gray-500">{title}</div>
      {items.length ? (
        <div className="space-y-1">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-700">
              {item}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-xs text-gray-500">{empty}</div>
      )}
    </div>
  );
}
