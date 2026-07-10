"use client";

import type { Task as APITask } from "@/utils/api/types";

import type { PersistedStyleInfo } from "./utils";
import { asRecord, renderJson } from "./utils";

type TaskDetailsProps = {
  task: APITask;
  persistedStyle?: PersistedStyleInfo;
  persistedLoading?: boolean;
};

export function TaskDetails({
  task,
  persistedStyle,
  persistedLoading,
}: TaskDetailsProps) {
  const params = asRecord(task.parameters) ?? ({} as Record<string, unknown>);
  const agentRun = params.agent_run;

  return (
    <div className="mt-4 rounded border border-gray-200 bg-gray-50 p-3 text-xs text-gray-700 space-y-3">
      <div className="flex flex-wrap items-center gap-4">
        <span className="font-medium">TaskID：{task.id}</span>
        {task.result_file_path ? (
          <span className="break-all">Result: {task.result_file_path}</span>
        ) : null}
      </div>

      {(() => {
        const run = asRecord(agentRun);
        if (!run) return null;

        const outline = asRecord(run.outline);
        const episodes = Array.isArray(run.episodes) ? run.episodes : null;

        const renderRun = (label: string, value: unknown) => {
          const record = asRecord(value);
          if (!record) return null;
          const prompt =
            typeof record.prompt === "string" ? record.prompt : null;
          const provider = record.provider_used;
          const model = record.model_used;
          const usage = record.usage;
          const reasoning = record.reasoning;
          const reasoningTrace = record.reasoning_trace;
          const method = record.generation_method;
          const plan = record.plan;
          const frames = Array.isArray(record.frames) ? record.frames : null;
          const planFixes = record.plan_fixes;

          return (
            <div className="rounded border border-gray-200 bg-white p-2">
              <div className="font-medium text-gray-800">{label}</div>
              <div className="mt-1 break-all">
                provider：{String(provider || "—")}
              </div>
              <div className="mt-1 break-all">
                model：{String(model || "—")}
              </div>
              {method ? (
                <div className="mt-1 break-all">method：{String(method)}</div>
              ) : null}
              {usage ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    usage
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {renderJson(usage)}
                  </pre>
                </details>
              ) : null}
              {reasoningTrace || reasoning ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    reasoning_trace
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {renderJson(reasoningTrace ?? reasoning)}
                  </pre>
                </details>
              ) : null}
              {planFixes ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    plan_fixes
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {renderJson(planFixes)}
                  </pre>
                </details>
              ) : null}
              {plan ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    plan
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {renderJson(plan)}
                  </pre>
                </details>
              ) : null}
              {frames ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    frames ({frames.length})
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {renderJson(frames)}
                  </pre>
                </details>
              ) : null}
              {prompt ? (
                <details className="mt-1">
                  <summary className="cursor-pointer text-gray-700">
                    prompt
                  </summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-gray-50 p-2 border border-gray-200">
                    {prompt}
                  </pre>
                </details>
              ) : null}
            </div>
          );
        };

        return (
          <div>
            <div className="font-medium text-gray-800">Agent Execution Trace</div>
            <div className="mt-2 space-y-2">
              {outline
                ? renderRun("Outline", outline)
                : renderRun("This Run", run)}
              {episodes && episodes.length ? (
                <details>
                  <summary className="cursor-pointer text-gray-700">
                    Episode Runs ({episodes.length})
                  </summary>
                  <div className="mt-2 space-y-2">
                    {episodes.map((item, idx) => {
                      const rec = asRecord(item);
                      const epNum = rec?.episode_number;
                      const label = epNum
                        ? `Episode ${String(epNum)}`
                        : `Episode ${idx + 1}item`;
                      return <div key={idx}>{renderRun(label, item)}</div>;
                    })}
                  </div>
                </details>
              ) : null}
            </div>
          </div>
        );
      })()}

      <div>
        <div className="font-medium text-gray-800">Parameters</div>
        <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-white p-2 border border-gray-200">
          {renderJson(task.parameters)}
        </pre>
      </div>

      {(() => {
        const presetId = params.style_preset_id;
        const spec = params.style_spec;
        if (!presetId && !spec) return null;
        return (
          <div>
            <div className="font-medium text-gray-800">Requested Style</div>
            <div className="mt-1 break-all">
              Preset: {String(presetId || "—")}
            </div>
            <div className="mt-1 break-all">Spec: {renderJson(spec)}</div>
          </div>
        );
      })()}

      <div>
        <div className="font-medium text-gray-800">Persisted Style</div>
        {persistedLoading ? (
          <div className="mt-1 text-gray-500">Loading...</div>
        ) : persistedStyle?.error ? (
          <div className="mt-1 text-red-600">{persistedStyle.error}</div>
        ) : persistedStyle ? (
          <>
            <div className="mt-1 break-all">Source: {persistedStyle.source}</div>
            <div className="mt-1 break-all">
              Spec: {renderJson(persistedStyle.style_spec)}
            </div>
            <div className="mt-1 break-all">
              Resolution: {renderJson(persistedStyle.style_spec_resolution)}
            </div>
          </>
        ) : (
          <div className="mt-1 text-gray-500">(Not loaded)</div>
        )}
      </div>
    </div>
  );
}
