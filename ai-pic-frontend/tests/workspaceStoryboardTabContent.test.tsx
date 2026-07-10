import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import { cleanup, render } from "@testing-library/react";
import { JSDOM } from "jsdom";

import { WorkspaceStoryboardTabContent } from "../src/components/features/episode/WorkspaceStoryboardTabContent";
import type {
  TimelineResolvedVideoListResponse,
  TimelineResponse,
} from "../src/utils/api/types";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost",
});
(globalThis as any).window = dom.window;
(globalThis as any).self = dom.window;
(globalThis as any).document = dom.window.document;
(globalThis as any).HTMLElement = dom.window.HTMLElement;
(globalThis as any).localStorage = dom.window.localStorage;

const timelineWithVideo = {
  id: 8,
  business_id: "timeline_8",
  episode_id: 1,
  script_id: 131,
  title: "Timeline",
  status: "draft",
  version: 3,
  created_at: "2026-06-03T00:00:00Z",
  updated_at: "2026-06-03T00:00:00Z",
  spec: {
    spec_version: "timeline.v1",
    episode_id: 1,
    script_id: 131,
    version: 3,
    tracks: [
      {
        track_type: "video",
        clips: [
          {
            clip_id: "video_scene_1_beat_1_001",
            track_type: "video",
            start_ms: 0,
            end_ms: 1200,
          },
        ],
      },
    ],
  },
} satisfies TimelineResponse;

const timelineWithAudio = {
  ...timelineWithVideo,
  spec: {
    ...timelineWithVideo.spec,
    duration_ms: 1200,
    source: {
      episode_audio: {
        oss_url: "https://example.com/episode-audio.mp3",
        duration_seconds: 1.2,
        generated_at: "2026-06-04T08:00:00Z",
        version: 2,
      },
    },
    tracks: [
      {
        track_type: "dialogue",
        clips: [
          {
            clip_id: "dialogue_scene_1_beat_1_001",
            track_type: "dialogue",
            start_ms: 0,
            end_ms: 1200,
            duration_ms: 1200,
            text: "native dialogue",
          },
        ],
      },
      ...timelineWithVideo.spec.tracks,
    ],
  },
} satisfies TimelineResponse;

describe("WorkspaceStoryboardTabContent", () => {
  afterEach(() => {
    cleanup();
  });

  it("surfaces clip-scoped storyboard management without whole-Timeline generation", async () => {
    const utils = render(
      <WorkspaceStoryboardTabContent
        episodeKey="episode_7"
        selectedScriptId={131}
        hasStoryboard={false}
        selectedTimelineSpec={timelineWithVideo}
        resolvedVideos={resolvedVideos("https://example.com/clip-ready.mp4")}
        selectedStoryboard={null}
        normalizedScenes={[]}
      />,
      { container: dom.window.document.body },
    );

    assert.equal(utils.queryByRole("button", { name: "Generate storyboard grid" }), null);
    assert.equal(utils.queryByText("Scene storyboard grid"), null);
    assert.equal(utils.queryByRole("button", { name: "Generate storyboard grid images" }), null);
    assert.equal(utils.queryByRole("button", { name: "Render final cut from grid images" }), null);
    assert.equal(utils.queryByRole("button", { name: "Generate storyboard" }), null);
    assert.equal(utils.queryByRole("button", { name: "Generate episode storyboard" }), null);
    assert.equal(utils.queryByText("Grid storyboard"), null);
    assert.equal(utils.queryByRole("button", { name: "Sync storyboard placeholders" }), null);
    assert.ok(utils.getByRole("heading", { name: "Full episode timeline" }));
    const supportShell = utils.container.querySelector(
      '[data-storyboard-support-shell="unframed"]',
    );
    assert.ok(supportShell);
    assert.doesNotMatch(supportShell.className, /rounded/);
    const supportTimeline = utils.container.querySelector(
      '[data-storyboard-support-timeline="true"]',
    );
    assert.ok(supportTimeline);
    assert.ok(supportTimeline.querySelector('[data-timeline="workspace"]'));
    assert.ok(supportTimeline.querySelector("[data-timeline-overview]"));
    assert.ok(utils.getByLabelText("Select Video 1 on the timeline"));
    assert.ok(utils.getByText("Clip storyboard management"));
    assert.ok(utils.getAllByText("Video 1").length >= 1);
    assert.ok(utils.getByText("Environment/IP pending binding"));
    assert.ok(utils.getByText("Storyboard pending generation"));
    const firstClipLink = utils.getByRole("link", {
      name: "Enter first clip storyboard",
    });
    assert.equal(
      firstClipLink.getAttribute("href"),
      "/episodes/episode_7/workspace?tab=timeline&scriptId=131&clipId=video_scene_1_beat_1_001",
    );
    assert.match(firstClipLink.className, /border-gray-200/);
    assert.doesNotMatch(firstClipLink.className, /bg-blue-600/);
    const link = utils.getByRole("link", { name: "Enter clip storyboard" });
    assert.equal(
      link.getAttribute("href"),
      "/episodes/episode_7/workspace?tab=timeline&scriptId=131&clipId=video_scene_1_beat_1_001",
    );
    assert.match(link.className, /border-gray-200/);
    assert.doesNotMatch(link.className, /bg-blue-600/);
    const video = await utils.findByLabelText(
      "Play clip video_scene_1_beat_1_001",
    );
    assert.equal(
      video.getAttribute("src"),
      "https://example.com/clip-ready.mp4",
    );
  });

  it("surfaces native Timeline context and audio playback on the storyboard tab", () => {
    const utils = render(
      <WorkspaceStoryboardTabContent
        episodeKey="episode_7"
        selectedScriptId={131}
        hasStoryboard={false}
        selectedAudioTimeline={{ version: 1, beats: [{ start_ms: 0 }] }}
        selectedTimelineSpec={timelineWithAudio}
        resolvedVideos={resolvedVideos(null)}
        selectedStoryboard={null}
        normalizedScenes={[]}
      />,
      { container: dom.window.document.body },
    );

    assert.equal(utils.getAllByText("Timeline 8 · v3").length, 2);
    assert.ok(utils.getByRole("heading", { name: "Full episode timeline" }));
    assert.ok(
      utils.container.querySelector(
        '[data-storyboard-support-timeline="true"]',
      ),
    );
    const timelineSummary = utils.container.querySelector(
      '[data-storyboard-support-timeline-summary="true"]',
    );
    assert.equal(
      timelineSummary?.getAttribute(
        "data-storyboard-support-timeline-summary-layout",
      ),
      "compact-strip",
    );
    assert.match(timelineSummary?.className || "", /border-t/);
    assert.doesNotMatch(timelineSummary?.className || "", /rounded-md/);
    assert.doesNotMatch(timelineSummary?.className || "", /\bp-3\b/);
    const contextStrip = utils.container.querySelector(
      '[data-storyboard-support-context-strip="inline"]',
    );
    assert.ok(contextStrip);
    assert.match(contextStrip.className || "", /border-t/);
    assert.doesNotMatch(contextStrip.className || "", /rounded-md/);
    assert.doesNotMatch(contextStrip.className || "", /\bgrid\b/);
    assert.equal(utils.queryByText("Timeline source"), null);
    assert.equal(utils.queryByText("Keyframes / Video"), null);
    const audioDetails = utils.container.querySelector(
      '[data-storyboard-support-audio="collapsed"]',
    ) as HTMLDetailsElement | null;
    assert.ok(audioDetails);
    assert.equal(audioDetails.open, false);
    assert.ok(utils.getByText("2 tracks · 2 clips"));
    assert.ok(utils.getByText("Duration 1.2s"));
    assert.equal(utils.queryByRole("button", { name: "Sync storyboard placeholders" }), null);
    const audio = utils.container.querySelector("audio");
    assert.equal(
      audio?.getAttribute("src"),
      "https://example.com/episode-audio.mp3",
    );
  });

  it("renders editable prompt-layer context for storyboard frames", () => {
    const utils = render(
      <WorkspaceStoryboardTabContent
        episodeKey="episode_7"
        selectedScriptId={131}
        hasStoryboard
        selectedTimelineSpec={timelineWithVideo}
        resolvedVideos={resolvedVideos(null)}
        selectedStoryboard={{
          frames: [
            {
              frame_id: "frame-1",
              frame_number: 1,
              timeline_clip_id: "video_scene_1_beat_1_001",
              start_ms: 0,
              end_ms: 1200,
              description: "Protagonist pushes open the lab door",
              shot_plan_prompt_layers: {
                direction_anchor: "Suspenseful entrance toward the lab doorway",
                aesthetic_reference: "IMAX film, Panavision C lens",
                composition_geometry: "Door on the center line, protagonist on the left third",
                motion_timeline: [
                  { at_ms: 0, action: "Protagonist reaches out to push the door" },
                  { at_ms: 1200, action: "Cold light spills through the crack in the door" },
                ],
                emotional_landing: "A tense pause in the cold light",
              },
            },
          ],
        }}
        normalizedScenes={[]}
      />,
      { container: dom.window.document.body },
    );

    assert.ok(utils.getByText("Five-layer prompts"));
    assert.ok(utils.getByText("Suspenseful entrance toward the lab doorway"));
    assert.ok(utils.getByText("0ms Protagonist reaches out to push the door / 1200ms Cold light spills through the crack in the door"));
  });

  it("falls back to audio timeline storyboard sync when native Timeline is absent", () => {
    const utils = render(
      <WorkspaceStoryboardTabContent
        episodeKey="episode_7"
        selectedScriptId={131}
        hasStoryboard={false}
        selectedAudioTimeline={{ version: 1, beats: [{ start_ms: 0 }] }}
        selectedTimelineSpec={null}
        selectedStoryboard={null}
        normalizedScenes={[]}
      />,
      { container: dom.window.document.body },
    );

    const button = utils.getByRole("button", { name: "Sync storyboard placeholders" });
    assert.equal(button.hasAttribute("disabled"), false);
    assert.ok(utils.getByRole("heading", { name: "Full episode timeline" }));
    assert.ok(utils.getByText("Audio timeline"));
    const supportTimeline = utils.container.querySelector(
      '[data-storyboard-support-timeline="true"]',
    );
    assert.ok(supportTimeline);
    assert.ok(supportTimeline.querySelector('[data-timeline="workspace"]'));
    assert.ok(
      supportTimeline.querySelector('[data-timeline-track-row="video"]'),
    );
  });
});

function resolvedVideos(url: string | null): TimelineResolvedVideoListResponse {
  return {
    timeline_id: 8,
    timeline_version: 3,
    ready: Boolean(url),
    video_clip_count: 1,
    missing_clip_count: url ? 0 : 1,
    generating_clip_count: 0,
    items: [
      {
        clip_id: "video_scene_1_beat_1_001",
        status: url ? "ready" : "missing",
        url,
        source: url ? "timeline_clip" : null,
        reason: url ? null : "missing_video_url",
        start_ms: 0,
        end_ms: 1200,
        duration_seconds: 1.2,
      },
    ],
  };
}
