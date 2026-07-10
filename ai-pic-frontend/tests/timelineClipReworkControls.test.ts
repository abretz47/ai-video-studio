import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import React from "react";
import {
  cleanup,
  fireEvent,
  render,
  waitFor,
  within,
} from "@testing-library/react";
import { JSDOM } from "jsdom";

import {
  buildTimelineClipVideoReworkTaskPayload,
  isTimelineVideoClip,
  timelineClipStartEndFrameStatus,
  timelineClipStoryboardPanelIndex,
  timelineClipStoryboardSheetUrl,
} from "../src/components/features/episode/TimelineClipProviderReworkModel";
import { TimelineClipProviderReworkControls } from "../src/components/features/episode/TimelineClipProviderReworkControls";
import { buildTimelineClipReworkPayload } from "../src/components/features/episode/TimelineClipReworkControls";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost",
});
(globalThis as any).window = dom.window;
(globalThis as any).self = dom.window;
(globalThis as any).document = dom.window.document;
(globalThis as any).HTMLElement = dom.window.HTMLElement;
(globalThis as any).HTMLInputElement = dom.window.HTMLInputElement;
(globalThis as any).HTMLSelectElement = dom.window.HTMLSelectElement;
(globalThis as any).HTMLTextAreaElement = dom.window.HTMLTextAreaElement;
(globalThis as any).localStorage = dom.window.localStorage;

const originalFetch = globalThis.fetch;

describe("timeline clip rework controls", () => {
  afterEach(() => {
    cleanup();
    globalThis.fetch = originalFetch;
    localStorage.clear();
  });

  it("builds compact timeline clip rework payloads", () => {
    assert.deepEqual(
      buildTimelineClipReworkPayload({
        expectedVersion: 3,
        action: "re_render",
        mediaAssetId: 42,
        assetRole: " render_output ",
        reason: " cleaner export ",
      }),
      {
        expected_version: 3,
        action: "re_render",
        media_asset_id: 42,
        asset_role: "render_output",
        reason: "cleaner export",
      },
    );
  });

  it("builds provider video rework task payloads", () => {
    assert.deepEqual(
      buildTimelineClipVideoReworkTaskPayload({
        expectedVersion: 4,
        action: "re_cut",
        prompt: " steadier motion ",
        model: " keling:kling-v2 ",
        duration: 1.2,
        resolution: "1080p",
        ratio: "9:16",
        reason: " motion fix ",
      }),
      {
        expected_version: 4,
        action: "re_cut",
        prompt: "steadier motion",
        model: "keling:kling-v2",
        duration: 1.2,
        resolution: "1080p",
        ratio: "9:16",
        asset_role: "generated_video",
        reason: "motion fix",
        use_end_frame: true,
        return_last_frame: true,
      },
    );
  });

  it("builds provider video rework payloads with clip storyboard references", () => {
    assert.deepEqual(
      buildTimelineClipVideoReworkTaskPayload({
        expectedVersion: 5,
        action: "re_cut",
        model: "volcengine:doubao-seedance-2-0-260128",
        resolution: "720p",
        useClipStoryboard: true,
      }),
      {
        expected_version: 5,
        action: "re_cut",
        model: "volcengine:doubao-seedance-2-0-260128",
        resolution: "720p",
        asset_role: "generated_video",
        use_end_frame: false,
        return_last_frame: true,
        reference_mode: "clip_storyboard_panel",
        use_clip_storyboard: true,
      },
    );
  });

  it("recognizes native Timeline video clips only", () => {
    assert.equal(
      isTimelineVideoClip({
        id: "video-1",
        startMs: 0,
        endMs: 1000,
        label: "clip",
        type: "video",
        color: "#0f766e",
        meta: { track_type: "video" },
      }),
      true,
    );
    assert.equal(
      isTimelineVideoClip({
        id: "dialogue-1",
        startMs: 0,
        endMs: 1000,
        label: "line",
        type: "dialogue",
        color: "#2563eb",
        meta: { track_type: "dialogue" },
      }),
      false,
    );
  });

  it("reads clip storyboard panel indexes from selected timeline clips", () => {
    const item = {
      id: "video-1",
      startMs: 0,
      endMs: 1000,
      label: "clip",
      type: "video" as const,
      color: "#0f766e",
      meta: {
        track_type: "video",
        source_refs: {
          clip_storyboard: {
            panel_index: 4,
          },
        },
        clip_storyboard_sheet_asset_ref: {
          file_url: "https://cdn.example/clip-storyboard.png",
        },
      },
    };
    assert.equal(timelineClipStoryboardPanelIndex(item), 4);
    assert.equal(
      timelineClipStoryboardSheetUrl(item),
      "https://cdn.example/clip-storyboard.png",
    );
  });

  it("reports selected clip start and end keyframe readiness", () => {
    assert.deepEqual(timelineClipStartEndFrameStatus(null), {
      startReady: false,
      endReady: false,
      label: "Start/end frames pending",
    });
    assert.deepEqual(
      timelineClipStartEndFrameStatus(videoClipWithStoryboardPanel()),
      {
        startReady: true,
        endReady: true,
        label: "首尾帧已生成",
      },
    );
    assert.deepEqual(
      timelineClipStartEndFrameStatus(videoClipWithoutStartEndFrames()),
      {
        startReady: false,
        endReady: false,
        label: "Start/end frames pending",
      },
    );
  });

  it("renders storyboard reference and clip video as two separate cards", () => {
    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        videoModels: [
          {
            id: "doubao-seedance-2-0-260128",
            name: "Seedance 2.0",
            provider: "volcengine",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    assert.ok(utils.getByLabelText("Step 1 · Clip Storyboard"));
    assert.ok(utils.getByLabelText("Step 3 · Clip Video"));
    const chain = utils.getByLabelText("Clip image/video generation flow");
    assert.ok(within(chain).getByText("Select References / Bindings"));
    assert.ok(within(chain).getByText("Images: Storyboard Frames"));
    assert.ok(within(chain).getByText("Images: Start/End Frames"));
    assert.ok(within(chain).getByText("Video: Clip Video"));
    assert.ok(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    assert.ok(utils.getByRole("button", { name: "Generate/Rework This Clip Video" }));
    assert.ok(utils.getByLabelText("Video Reference Source"));
    assert.ok(utils.getByRole("option", { name: "分镜 Panel 4" }));
    assert.ok(utils.getByLabelText("Additional Reference Image URL"));
    assert.ok(utils.getByLabelText("Visual Style"));
    assert.ok(utils.getByLabelText("Storyboard panel count"));
    const storyboardModelSelect = utils.getByLabelText("StoryboardImage Generation Model");
    assert.ok(
      within(storyboardModelSelect).getByRole("option", {
        name: "Automatically select model",
      }),
    );
    const videoModelSelect = utils.getByLabelText("VideoModel");
    assert.ok(
      within(videoModelSelect).getByRole("option", { name: "Automatically select model" }),
    );
    assert.ok(within(videoModelSelect).getByRole("option", { name: "Seedance 2.0" }));
    assert.ok(utils.getByLabelText("Frame Ratio"));
    assert.ok(utils.getByRole("option", { name: "9:16" }));
    assert.ok(utils.getByLabelText("Rework Action"));
    assert.ok(utils.getByLabelText("Motion prompt override"));
    assert.ok(utils.getByText("Leave empty to use the timeline camera motion plan"));
  });

  it("shows shared references as a visible clip production context", async () => {
    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          { url: "https://cdn.example/interior-env.png", label: "室内环境" },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(utils.getByLabelText("Clip Shared Reference Context")));
    const sharedContext = utils.getByLabelText("Clip Shared Reference Context");
    assert.equal(sharedContext.closest("[data-clip-parameter-details]"), null);
    assert.ok(within(sharedContext).getByText("Used for storyboard, start/end frames, and video tasks"));
    assert.ok(within(sharedContext).getByText("Character IP: 快递员"));
    assert.ok(within(sharedContext).getByText("IP Images: 1 images"));
    assert.ok(within(sharedContext).getByText("Environment Images: 1 images"));
  });

  it("disables start-end video reference when keyframes are missing", () => {
    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithoutStartEndFrames(),
      }),
      { container: dom.window.document.body },
    );

    assert.ok(utils.getAllByText("Start/end frames pending").length >= 1);
    assert.ok(
      utils.getAllByText("Complete the clip storyboard and start/end frames before generating video").length >= 1,
    );
    assert.equal(
      (
        utils.getByRole("button", {
          name: "Generate/Rework This Clip Video",
        }) as HTMLButtonElement
      ).disabled,
      true,
    );
    assert.equal(
      (utils.getByRole("option", { name: /首尾帧/ }) as HTMLOptionElement)
        .disabled,
      true,
    );
  });

  it("requires both clip storyboard and keyframes before video generation", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 97, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithoutStoryboardPanel(),
      }),
      { container: dom.window.document.body },
    );

    const videoButton = utils.getByRole("button", {
      name: "Generate/Rework This Clip Video",
    }) as HTMLButtonElement;
    assert.equal(videoButton.disabled, true);
    assert.ok(
      utils.getAllByText("Complete the clip storyboard and start/end frames before generating video").length >= 1,
    );
    fireEvent.submit(videoButton.closest("form")!);
    await waitFor(() => assert.equal(calls.length, 0));
  });

  it("does not let manual references bypass the video generation image gate", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 98, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithoutStartEndFrames(),
      }),
      { container: dom.window.document.body },
    );

    fireEvent.input(utils.getByLabelText("Additional Reference Image URL"), {
      target: { value: "https://manual.example/ref.png" },
    });
    fireEvent.change(utils.getByLabelText("Video Reference Source"), {
      target: { value: "manual_refs" },
    });
    const videoButton = utils.getByRole("button", {
      name: "Generate/Rework This Clip Video",
    }) as HTMLButtonElement;
    assert.equal(videoButton.disabled, true);
    fireEvent.submit(videoButton.closest("form")!);
    await waitFor(() => assert.equal(calls.length, 0));
  });

  it("allows Timeline shot plan clips to generate video without extra keyframes", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 99, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithTimelineShotPlanOnly(),
      }),
      { container: dom.window.document.body },
    );

    const videoButton = utils.getByRole("button", {
      name: "Generate/Rework This Clip Video",
    }) as HTMLButtonElement;
    assert.equal(videoButton.disabled, false);
    fireEvent.click(videoButton);
    await waitFor(() => assert.equal(calls.length, 1));
    assert.equal(
      calls[0].url,
      "/api/v1/timelines/8/clips/video_scene_1_beat_1_001/rework/video",
    );
    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        action: "re_cut",
        resolution: "720p",
        asset_role: "generated_video",
        use_end_frame: true,
        return_last_frame: true,
      }),
    );
  });

  it("keeps storyboard and video submit paths clip-scoped from the two-step controls", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 88, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
      }),
      { container: dom.window.document.body },
    );

    fireEvent.input(utils.getByLabelText("Additional Reference Image URL"), {
      target: { value: "https://manual.example/ref.png" },
    });
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));
    assert.equal(
      calls[0].url,
      "/api/v1/timelines/8/clips/video_scene_1_beat_1_001/storyboard/generate",
    );
    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        reference_images: ["https://manual.example/ref.png"],
      }),
    );

    fireEvent.change(utils.getByLabelText("Video Reference Source"), {
      target: { value: "clip_storyboard_panel" },
    });
    fireEvent.click(utils.getByRole("button", { name: "Generate/Rework This Clip Video" }));
    await waitFor(() => assert.equal(calls.length, 2));
    assert.equal(
      calls[1].url,
      "/api/v1/timelines/8/clips/video_scene_1_beat_1_001/rework/video",
    );
    assert.equal(
      calls[1].init?.body,
      JSON.stringify({
        expected_version: 3,
        action: "re_cut",
        resolution: "720p",
        asset_role: "generated_video",
        use_end_frame: false,
        return_last_frame: true,
        reference_mode: "clip_storyboard_panel",
        use_clip_storyboard: true,
        reference_images: ["https://manual.example/ref.png"],
      }),
    );
  });

  it("submits selected role IP bindings with clip storyboard generation", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 90, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [
          episodeCharacter("林晚", 31),
          episodeCharacter("快递员", 32),
        ],
      }),
      { container: dom.window.document.body },
    );

    assert.ok(utils.getByText("Bind Character IP"));
    fireEvent.click(utils.getByLabelText("Bind Character IP 快递员"));
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
      }),
    );
  });

  it("submits the selected image model with clip storyboard generation", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 93, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        imageModels: [
          {
            id: "doubao-seedream-4-5-251128",
            model_id: "volcengine:doubao-seedream-4-5-251128",
            name: "Seedream 4.5",
            provider: "volcengine",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    fireEvent.change(utils.getByLabelText("StoryboardImage Generation Model"), {
      target: { value: "volcengine:doubao-seedream-4-5-251128" },
    });
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        model: "volcengine:doubao-seedream-4-5-251128",
      }),
    );
  });

  it("defaults role IP bindings from selected clip character names", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 96, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithCharacterNames(["快递员"]),
        episodeCharacters: [
          episodeCharacter("林晚", 31),
          episodeCharacter("快递员", 32),
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() =>
      assert.equal(
        (utils.getByLabelText("Bind Character IP 快递员") as HTMLInputElement)
          .checked,
        true,
      ),
    );
    assert.equal(
      (utils.getByLabelText("Bind Character IP 林晚") as HTMLInputElement).checked,
      false,
    );
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
      }),
    );
  });

  it("auto-selects default IP and environment thumbnails for storyboard generation", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 91, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          {
            url: "https://cdn.example/interior-env.png",
            label: "室内环境",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));
    assert.ok(utils.getByAltText("Selected IP Image 快递员 正面"));
    assert.ok(utils.getByAltText("SelectedEnvironment Image 室内环境"));
    assert.equal(utils.queryByLabelText("Select IP Image 快递员 正面"), null);
    const ipDialog = openReferencePicker(utils, "Select IP Image");
    assert.equal(
      within(ipDialog)
        .getByLabelText("Select IP Image 快递员 正面")
        .getAttribute("aria-pressed"),
      "true",
    );
    fireEvent.click(within(ipDialog).getByRole("button", { name: "Apply Selection" }));
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
        character_reference_images: ["https://cdn.example/courier-pose.png"],
        environment_reference_images: ["https://cdn.example/interior-env.png"],
      }),
    );
  });

  it("keeps reference image controls visible outside collapsed parameter menus", async () => {
    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          {
            url: "https://cdn.example/interior-env.png",
            label: "室内环境",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() =>
      assert.ok(utils.getByRole("button", { name: "Select IP Image" })),
    );

    const referenceControls = [
      utils.getByRole("button", { name: "Select IP Image" }),
      utils.getByRole("button", { name: "Select Environment Image" }),
      utils.getByLabelText("Additional Reference Image URL"),
      utils.getByLabelText("Video Reference Source"),
    ];

    for (const control of referenceControls) {
      assert.equal(control.closest("[data-clip-parameter-details]"), null);
    }
  });

  it("deselects default thumbnails and clears selections on demand", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 95, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          {
            url: "https://cdn.example/interior-env.png",
            label: "室内环境",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));
    assert.equal(utils.getAllByText("Selected 1/1").length, 2);
    const ipDialog = openReferencePicker(utils, "Select IP Image");
    fireEvent.click(within(ipDialog).getByLabelText("Select IP Image 快递员 正面"));
    fireEvent.click(within(ipDialog).getByRole("button", { name: "Apply Selection" }));
    fireEvent.click(utils.getByLabelText("Environment Image clear"));
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
      }),
    );
  });

  it("discards staged reference image changes when picker is cancelled", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 97, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));
    const ipDialog = openReferencePicker(utils, "Select IP Image");
    fireEvent.click(within(ipDialog).getByLabelText("Select IP Image 快递员 正面"));
    fireEvent.click(within(ipDialog).getByRole("button", { name: "Cancel" }));
    assert.ok(hasText(utils, "IP Images: 1 images"));

    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));
    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
        character_reference_images: ["https://cdn.example/courier-pose.png"],
      }),
    );
  });

  it("clears reference image selections from the picker footer", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 98, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));
    const ipDialog = openReferencePicker(utils, "Select IP Image");
    fireEvent.click(within(ipDialog).getByRole("button", { name: "Clear" }));
    fireEvent.click(within(ipDialog).getByRole("button", { name: "Apply Selection" }));
    assert.ok(hasText(utils, "IP 图：0 张"));

    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() => assert.equal(calls.length, 1));
    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
      }),
    );
  });

  it("shows and submits selected IP and environment bindings with video rework", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 93, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          {
            url: "https://cdn.example/interior-env.png",
            label: "室内环境",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));

    const videoBinding = utils.getByLabelText("Video generation binding context");
    assert.ok(videoBinding);
    assert.ok(within(videoBinding).getByText("Video generation binding context"));
    assert.ok(within(videoBinding).getByText("Bindings attached"));
    assert.ok(within(videoBinding).getByText("Character IP: 快递员"));
    assert.ok(within(videoBinding).getByText("IP Images: 1 images"));
    assert.ok(within(videoBinding).getByText("Environment Images: 1 images"));
    assert.ok(
      within(videoBinding).getByText("The video task will include the selected IP and environment images above."),
    );

    fireEvent.click(utils.getByRole("button", { name: "Generate/Rework This Clip Video" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        action: "re_cut",
        resolution: "720p",
        asset_role: "generated_video",
        use_end_frame: true,
        return_last_frame: true,
        character_virtual_ip_ids: [32],
        character_reference_images: ["https://cdn.example/courier-pose.png"],
        environment_reference_images: ["https://cdn.example/interior-env.png"],
      }),
    );
  });

  it("queues selected IP and environment bindings with keyframe generation", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 94, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
        storyboardEnvironmentImageOptions: [
          {
            url: "https://cdn.example/interior-env.png",
            label: "室内环境",
          },
        ],
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(hasText(utils, "IP Images: 1 images")));
    fireEvent.click(utils.getByRole("button", { name: "Generate Start/End Frames" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].url,
      "/api/v1/timelines/8/clips/video_scene_1_beat_1_001/keyframes/generate",
    );
    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        generation_profile: "clip_keyframes",
        aspect_ratio: "9:16",
        character_virtual_ip_ids: [32],
        character_reference_images: ["https://cdn.example/courier-pose.png"],
        environment_reference_images: ["https://cdn.example/interior-env.png"],
      }),
    );
  });

  it("loads selected environment details before showing environment thumbnails", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      if (String(url) === "/api/v1/story-structure/environments/1") {
        return new Response(
          JSON.stringify({
            id: 1,
            name: "办公室",
            reference_images: ["https://cdn.example/office-env.png"],
            created_at: "2026-06-09T00:00:00Z",
            updated_at: "2026-06-09T00:00:00Z",
          }),
          { status: 200, headers: { "content-type": "application/json" } },
        );
      }
      return new Response(JSON.stringify({ task_id: 92, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
        episodeCharacters: [episodeCharacter("快递员", 32)],
        environments: [
          {
            id: 1,
            name: "办公室",
            created_at: "2026-06-09T00:00:00Z",
            updated_at: "2026-06-09T00:00:00Z",
          },
        ],
        selectedEnvironmentId: 1,
        storyboardCharacterImageOptions: {
          32: [
            {
              url: "https://cdn.example/courier-pose.png",
              label: "快递员 正面",
            },
          ],
        },
      }),
      { container: dom.window.document.body },
    );

    await waitFor(() => assert.ok(utils.getByAltText("SelectedEnvironment Image 办公室 1")));
    const envDialog = openReferencePicker(utils, "Select Environment Image");
    assert.equal(
      within(envDialog)
        .getByLabelText("Select Environment Image 办公室 1")
        .getAttribute("aria-pressed"),
      "true",
    );
    fireEvent.click(within(envDialog).getByRole("button", { name: "Apply Selection" }));
    fireEvent.click(utils.getByRole("button", { name: "Generate Clip Storyboard" }));
    await waitFor(() =>
      assert.ok(
        calls.some((call) => String(call.url).includes("/storyboard/generate")),
      ),
    );

    const storyboardCall = calls.find((call) =>
      String(call.url).includes("/storyboard/generate"),
    );
    assert.equal(
      storyboardCall?.init?.body,
      JSON.stringify({
        expected_version: 3,
        panel_count: 4,
        style: "live_action",
        generation_profile: "clip_storyboard",
        size: "1536x1536",
        aspect_ratio: "1:1",
        character_virtual_ip_ids: [32],
        character_reference_images: ["https://cdn.example/courier-pose.png"],
        environment_reference_images: ["https://cdn.example/office-env.png"],
      }),
    );
  });

  it("submits manual reference images as an explicit generation choice", async () => {
    const calls: Array<{ url: string; init?: RequestInit }> = [];
    globalThis.fetch = (async (url: RequestInfo | URL, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      return new Response(JSON.stringify({ task_id: 89, status: "pending" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const utils = render(
      React.createElement(TimelineClipProviderReworkControls, {
        timelineId: 8,
        timelineVersion: 3,
        clipId: "video_scene_1_beat_1_001",
        item: videoClipWithStoryboardPanel(),
      }),
      { container: dom.window.document.body },
    );

    fireEvent.change(utils.getByLabelText("Video Reference Source"), {
      target: { value: "manual_refs" },
    });
    fireEvent.input(utils.getByLabelText("Additional Reference Image URL"), {
      target: {
        value: "https://manual.example/a.png\nhttps://manual.example/b.png",
      },
    });
    fireEvent.click(utils.getByRole("button", { name: "Generate/Rework This Clip Video" }));
    await waitFor(() => assert.equal(calls.length, 1));

    assert.equal(
      calls[0].init?.body,
      JSON.stringify({
        expected_version: 3,
        action: "re_cut",
        resolution: "720p",
        asset_role: "generated_video",
        use_end_frame: false,
        return_last_frame: true,
        reference_mode: "start_end",
        reference_images: [
          "https://manual.example/a.png",
          "https://manual.example/b.png",
        ],
      }),
    );
  });
});

function videoClipWithStoryboardPanel() {
  return {
    id: "video-1",
    startMs: 0,
    endMs: 1000,
    label: "clip",
    type: "video" as const,
    color: "#0f766e",
    meta: {
      track_type: "video",
      source_refs: {
        clip_storyboard: {
          panel_index: 4,
        },
      },
      clip_storyboard_sheet_asset_ref: {
        file_url: "https://cdn.example/clip-storyboard.png",
      },
      start_frame_asset_ref: {
        file_url: "https://cdn.example/start-frame.png",
      },
      end_frame_asset_ref: {
        file_url: "https://cdn.example/end-frame.png",
      },
    },
  };
}

function openReferencePicker(utils: ReturnType<typeof render>, name: string) {
  fireEvent.click(utils.getByRole("button", { name }));
  return utils.getByRole("dialog");
}

function hasText(utils: ReturnType<typeof render>, text: string) {
  return utils.queryAllByText(text).length > 0;
}

function videoClipWithoutStartEndFrames() {
  const clip = videoClipWithStoryboardPanel();
  return {
    ...clip,
    meta: {
      ...clip.meta,
      start_frame_asset_ref: undefined,
      end_frame_asset_ref: undefined,
      start_frame_url: undefined,
      end_frame_url: undefined,
    },
  };
}

function videoClipWithoutStoryboardPanel() {
  const clip = videoClipWithStoryboardPanel();
  return {
    ...clip,
    meta: {
      ...clip.meta,
      source_refs: {},
      clip_storyboard_sheet_asset_ref: undefined,
    },
  };
}

function videoClipWithTimelineShotPlanOnly() {
  const clip = videoClipWithoutStoryboardPanel();
  return {
    ...clip,
    meta: {
      ...clip.meta,
      start_frame_asset_ref: undefined,
      end_frame_asset_ref: undefined,
      start_frame_url: undefined,
      end_frame_url: undefined,
      source_refs: {
        timeline_shot_plan: {
          video_prompt: "Timeline shot plan motion prompt",
          motion_timeline: [{ at_ms: 0, action: "open with a tense push-in" }],
        },
      },
    },
  };
}

function videoClipWithCharacterNames(names: string[]) {
  const clip = videoClipWithStoryboardPanel();
  return {
    ...clip,
    meta: {
      ...clip.meta,
      characters_involved: names,
    },
  };
}

function episodeCharacter(characterName: string, virtualIpId: number) {
  return {
    id: virtualIpId + 1000,
    business_id: `ep_char_${virtualIpId}`,
    episode_id: 1,
    episode_business_id: "episode_1",
    virtual_ip_id: virtualIpId,
    virtual_ip_business_id: `vip_${virtualIpId}`,
    character_name: characterName,
    role_type: "temporary",
    importance: 3,
    created_at: "2026-06-09T00:00:00Z",
    updated_at: "2026-06-09T00:00:00Z",
  };
}
