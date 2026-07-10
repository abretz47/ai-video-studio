import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import { cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import { JSDOM } from "jsdom";

import { ProductionCanvasContent } from "../src/components/features/canvas/ProductionCanvasBoard";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost",
});
(globalThis as any).window = dom.window;
(globalThis as any).self = dom.window;
(globalThis as any).document = dom.window.document;
(globalThis as any).HTMLElement = dom.window.HTMLElement;
(globalThis as any).SVGElement = dom.window.SVGElement;
(globalThis as any).localStorage = dom.window.localStorage;
(globalThis as any).Event = dom.window.Event;
(globalThis as any).InputEvent = dom.window.InputEvent;
Object.defineProperty(globalThis, "navigator", {
  value: dom.window.navigator,
  configurable: true,
});

describe("ProductionCanvasMediaControls", () => {
  afterEach(() => cleanup());

  it("sends selected media controls when executing image and video skills", async () => {
    const originalFetch = globalThis.fetch;
    const executeRequests: Record<string, any>[] = [];
    globalThis.fetch = async (input, init) => {
      const url = String(input);
      if (url.includes("/production-canvas/execute")) {
        const body = JSON.parse(String(init?.body));
        executeRequests.push(body);
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              task_id: body.skill === "image.candidates" ? 91 : 92,
              task_status: "pending",
              skill_result: {
                skill: body.skill,
                label: body.skill === "image.candidates" ? "Image Skill" : "Video Skill",
                title: "Media task submitted",
                status: "running",
                detail: "Media task submitted in the backend.",
                outputs: {
                  script_id: body.script_id,
                  dispatched_task_id: body.skill === "image.candidates" ? 91 : 92,
                  canvas_run_id: body.run_id,
                },
              },
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            run_id: "canvas-run-media",
            task_id: 44,
            nodes: [
              {
                id: "skill-image",
                label: "Image Candidates",
                title: "Image candidate execution entry",
                status: "blocked",
                x: 120,
                y: 320,
                width: 220,
                kind: "skill_result",
                skill: "image.candidates",
                detail: "Reuses the existing storyboard image candidate task.",
                outputs: {
                  script_id: 321,
                  required_inputs: ["manual_media_controls"],
                },
              },
              {
                id: "skill-video",
                label: "Video Candidates",
                title: "Video candidate execution entry",
                status: "blocked",
                x: 380,
                y: 320,
                width: 220,
                kind: "skill_result",
                skill: "video.candidates",
                detail: "Reuses the existing storyboard video candidate task.",
                outputs: {
                  script_id: 321,
                  required_inputs: ["manual_media_controls"],
                },
              },
            ],
            selected_assets: { virtual_ips: [], environments: [] },
            skill_manifest: { version: "production_canvas.v1" },
          },
        }),
        { headers: { "content-type": "application/json" } },
      ) as Promise<Response>;
    };

    try {
      const utils = render(
        <ProductionCanvasContent storageKey={null} autosaveDelayMs={null} />,
        { container: dom.window.document.body },
      );
      fireEvent.input(utils.getByLabelText("Production goal"), {
        target: { value: "Generate media candidates" },
      });
      fireEvent.click(utils.getByRole("button", { name: "Create all" }));
      await waitFor(() =>
        assert.ok(utils.getAllByText("Image candidate execution entry").length),
      );

      fireEvent.click(utils.getByLabelText("Image Candidates Image candidate execution entry"));
      fireEvent.input(utils.getByLabelText("Media frame indexes"), {
        target: { value: "1" },
      });
      fireEvent.input(utils.getByLabelText("Media model"), {
        target: { value: "codex:gpt-image-2" },
      });
      fireEvent.input(utils.getByLabelText("Image aspect ratio"), {
        target: { value: "16:9" },
      });
      fireEvent.click(utils.getByLabelText("Require reference images"));
      await waitFor(() => assert.ok(utils.getByText("frame_indexes: 1")));
      fireEvent.click(utils.getByRole("button", { name: "Run in background" }));
      await waitFor(() => assert.equal(executeRequests[0]?.skill, "image.candidates"));
      assert.deepEqual(executeRequests[0]?.frame_indexes, [1]);
      assert.equal(executeRequests[0]?.model, "codex:gpt-image-2");
      assert.equal(executeRequests[0]?.aspect_ratio, "16:9");
      assert.equal(executeRequests[0]?.require_reference_images, false);

      fireEvent.click(utils.getByLabelText("Video Candidates Video candidate execution entry"));
      fireEvent.input(utils.getByLabelText("Media frame indexes"), {
        target: { value: "1" },
      });
      fireEvent.input(utils.getByLabelText("Media model"), {
        target: { value: "minimax:video-01" },
      });
      fireEvent.input(utils.getByLabelText("Video duration"), {
        target: { value: "6" },
      });
      fireEvent.input(utils.getByLabelText("Video FPS"), {
        target: { value: "30" },
      });
      fireEvent.input(utils.getByLabelText("Video resolution"), {
        target: { value: "1080p" },
      });
      fireEvent.input(utils.getByLabelText("Video aspect ratio"), {
        target: { value: "16:9" },
      });
      fireEvent.click(utils.getByLabelText("Fixed camera"));
      await waitFor(() => assert.ok(utils.getByText("duration: 6")));
      fireEvent.click(utils.getByRole("button", { name: "Run in background" }));
      await waitFor(() => assert.equal(executeRequests[1]?.skill, "video.candidates"));
      assert.deepEqual(executeRequests[1]?.frame_indexes, [1]);
      assert.equal(executeRequests[1]?.model, "minimax:video-01");
      assert.equal(executeRequests[1]?.duration, 6);
      assert.equal(executeRequests[1]?.fps, 30);
      assert.equal(executeRequests[1]?.resolution, "1080p");
      assert.equal(executeRequests[1]?.ratio, "16:9");
      assert.equal(executeRequests[1]?.camera_fixed, true);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});
