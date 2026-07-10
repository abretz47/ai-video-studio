"use client";
import { HookTagBadge } from "./hooks/HookTagBadge";

export type StoryboardFrame = {
  frame_id?: string;
  frame_number?: number;
  scene_number?: number | string;
  shot_type?: string;
  camera_movement?: string;
  composition?: string;
  description?: string;
  duration_seconds?: number;
  ai_prompt?: string;
  reference_images?: string[];
  image_url?: string;
  video_url?: string;
  generation_source?: string;
  generation_method?: string;
  generation_model?: string;
  beat_id?: number;
  shot_id?: number;
  shot_number?: string;
  /** Hook tag: hook/reversal/payoff/cliffhanger, etc. */
  hook_tag?: string;
  /** Hook intensity: low/medium/high */
  hook_intensity?: string;
  /** Associated ad asset ID */
  ad_snippet_id?: string;
  /** Timeline start (milliseconds) */
  start_ms?: number;
  /** Timeline end (milliseconds) */
  end_ms?: number;
  generated_at?: string;
  updated_at?: string;
};

const SceneTag = ({ label }: { label: string }) => (
  <span className="rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs text-gray-600">
    {label}
  </span>
);

export const formatText = (
  value: unknown,
  fallback = "No content yet",
  max = 160,
) => {
  if (!value) return fallback;
  const raw = typeof value === "string" ? value : JSON.stringify(value);
  const clean = raw.replace(/\n+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max)}…` : clean;
};

/** Format milliseconds as MM:SS.ms */
const formatMs = (ms?: number): string => {
  if (ms === undefined || ms === null) return "—";
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  const millis = ms % 1000;
  return `${minutes.toString().padStart(2, "0")}:${seconds
    .toString()
    .padStart(2, "0")}.${Math.floor(millis / 100)}`;
};

export const FrameCard = ({ frame }: { frame: StoryboardFrame }) => (
  <article className="rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700">
    <header className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-gray-800">
          Storyboard {frame.frame_number}
        </span>
        {/* Hook Tag */}
        {frame.hook_tag && (
          <HookTagBadge
            hookType={frame.hook_tag}
            intensity={frame.hook_intensity}
            showLabel={true}
          />
        )}
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-500">
        {frame.shot_number && (
          <SceneTag label={`Shot #${frame.shot_number}`} />
        )}
        {frame.shot_id && <SceneTag label={`Shot ID ${frame.shot_id}`} />}
        {frame.beat_id && <SceneTag label={`Beat #${frame.beat_id}`} />}
        {frame.shot_type && <SceneTag label={frame.shot_type} />}
        {frame.generation_method && (
          <SceneTag label={frame.generation_method} />
        )}
      </div>
    </header>
    <p className="mt-2 text-xs text-gray-600">
      {formatText(frame.description, "No description", 180)}
    </p>
    <dl className="mt-2 grid grid-cols-2 gap-x-1 gap-y-1 text-[11px] text-gray-500">
      <div>
        <dt className="inline text-gray-400">Camera movement: </dt>
        <dd className="inline">{frame.camera_movement || "—"}</dd>
      </div>
      <div>
        <dt className="inline text-gray-400">Composition: </dt>
        <dd className="inline">{frame.composition || "—"}</dd>
      </div>
      <div>
        <dt className="inline text-gray-400">Duration: </dt>
        <dd className="inline">{frame.duration_seconds || "—"}s</dd>
      </div>
      <div>
        <dt className="inline text-gray-400">Model: </dt>
        <dd className="inline">{frame.generation_model || "—"}</dd>
      </div>
      {(frame.start_ms !== undefined || frame.end_ms !== undefined) && (
        <div className="col-span-2">
          <dt className="inline text-gray-400">Time range: </dt>
          <dd className="inline">
            {formatMs(frame.start_ms)} - {formatMs(frame.end_ms)}
          </dd>
        </div>
      )}
    </dl>
    {frame.ai_prompt && (
      <div className="mt-2 rounded bg-white/70 p-2 text-[11px] text-gray-500">
        <div className="mb-1 font-medium text-gray-600">AI Prompt</div>
        <p className="whitespace-pre-wrap">{frame.ai_prompt}</p>
      </div>
    )}
    {(frame.image_url || frame.video_url) && (
      <div className="mt-2 flex gap-3 text-xs">
        {frame.image_url && (
          <a
            href={frame.image_url}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 hover:text-blue-800"
          >
            View Image
          </a>
        )}
        {frame.video_url && (
          <a
            href={frame.video_url}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 hover:text-blue-800"
          >
            View Video
          </a>
        )}
      </div>
    )}
  </article>
);
