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

describe("ProductionCanvasPersistence", () => {
  afterEach(() => cleanup());

  it("saves and restores a server-backed canvas run", async () => {
    const originalFetch = globalThis.fetch;
    const savedBodies: Record<string, unknown>[] = [];
    globalThis.fetch = async (input, init) => {
      const url = String(input);
      if (url.includes("/production-canvas/plan")) {
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              run_id: "canvas-run-123",
              task_id: 44,
              nodes: [
                {
                  id: "skill-brief",
                  label: "Brief Skill",
                  title: "Server-generated brief node",
                  status: "review",
                  x: 180,
                  y: 320,
                  width: 220,
                  kind: "skill_result",
                  skill: "brief.compose",
                  detail: "Used to test server-side state persistence.",
                  outputs: { prompt: "Create a short drama production canvas" },
                },
              ],
              selected_assets: { virtual_ips: [], environments: [] },
              skill_manifest: { version: "production_canvas.v1" },
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      if (url.includes("/production-canvas/runs/canvas-run-123/state")) {
        savedBodies.push(JSON.parse(String(init?.body)));
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              run_id: "canvas-run-123",
              task_id: 44,
              nodes: [],
              selected_assets: { virtual_ips: [], environments: [] },
              skill_manifest: { version: "production_canvas.v1" },
              saved_state: savedBodies[savedBodies.length - 1],
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      if (url.includes("/production-canvas/runs/canvas-run-123")) {
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              run_id: "canvas-run-123",
              task_id: 55,
              nodes: [],
              selected_assets: { virtual_ips: [], environments: [] },
              skill_manifest: { version: "production_canvas.v1" },
              saved_state: {
                nodes: [
                  {
                    id: "skill-brief",
                    label: "Brief Skill",
                    title: "Server brief",
                    status: "review",
                    x: 120,
                    y: 160,
                    width: 220,
                    kind: "skill_result",
                    skill: "brief.compose",
                  },
                  {
                    id: "note-1",
                    label: "Note",
                    title: "Server note",
                    status: "review",
                    x: 320,
                    y: 260,
                    width: 190,
                    kind: "note",
                    detail: "Restored from server",
                  },
                ],
                viewport: { x: 12, y: 34, zoom: 0.8 },
                selected_node_id: "note-1",
                edges: [{ from: "note-1", to: "skill-brief" }],
              },
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      throw new Error(`Unexpected request ${url}`);
    };

    try {
      const utils = render(<ProductionCanvasContent storageKey={null} />, {
        container: dom.window.document.body,
      });
      fireEvent.input(utils.getByLabelText("Production goal"), {
        target: { value: "Create a short drama production canvas" },
      });
      fireEvent.click(utils.getByRole("button", { name: "Create all" }));

      await waitFor(() => {
        const input = utils.getByLabelText("Run ID") as HTMLInputElement;
        assert.equal(input.value, "canvas-run-123");
      });

      fireEvent.click(utils.getByRole("button", { name: "Save canvas" }));
      await waitFor(() => assert.equal(savedBodies.length, 1));
      assert.equal(savedBodies[0]?.selected_node_id, "skill-brief");
      assert.ok(Array.isArray(savedBodies[0]?.nodes));
      assert.ok(Array.isArray(savedBodies[0]?.edges));
      await waitFor(() => assert.ok(utils.getByText("Saved")));

      fireEvent.click(utils.getByRole("button", { name: "Restore canvas" }));

      await waitFor(() => assert.ok(utils.getAllByText("Server note").length));
      assert.ok(
        utils.container.querySelector("[data-canvas-edge='note-1-skill-brief']"),
      );
      const world = utils.container.querySelector(
        "[data-production-canvas-world='true']",
      ) as HTMLElement;
      assert.match(world.style.transform, /translate\(12px, 34px\) scale\(0.8\)/);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  it("debounces autosave after a run exists and saves the latest canvas state", async () => {
    const originalFetch = globalThis.fetch;
    const savedBodies: Record<string, any>[] = [];
    globalThis.fetch = async (input, init) => {
      const url = String(input);
      if (url.includes("/production-canvas/plan")) {
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              run_id: "canvas-run-autosave",
              task_id: 66,
              nodes: [
                {
                  id: "skill-brief",
                  label: "Brief Skill",
                  title: "Autosave brief",
                  status: "review",
                  x: 180,
                  y: 320,
                  width: 220,
                  kind: "skill_result",
                  skill: "brief.compose",
                  outputs: { prompt: "Autosave canvas" },
                },
              ],
              selected_assets: { virtual_ips: [], environments: [] },
              skill_manifest: { version: "production_canvas.v1" },
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      if (url.includes("/production-canvas/runs/canvas-run-autosave/state")) {
        savedBodies.push(JSON.parse(String(init?.body)));
        return new Response(
          JSON.stringify({
            success: true,
            data: {
              run_id: "canvas-run-autosave",
              task_id: 66,
              nodes: [],
              selected_assets: { virtual_ips: [], environments: [] },
              skill_manifest: { version: "production_canvas.v1" },
              saved_state: savedBodies[savedBodies.length - 1],
            },
          }),
          { headers: { "content-type": "application/json" } },
        ) as Promise<Response>;
      }
      throw new Error(`Unexpected request ${url}`);
    };

    try {
      const utils = render(
        <ProductionCanvasContent storageKey={null} autosaveDelayMs={5} />,
        { container: dom.window.document.body },
      );
      fireEvent.input(utils.getByLabelText("Production goal"), {
        target: { value: "Autosave canvas" },
      });
      fireEvent.click(utils.getByRole("button", { name: "Create all" }));

      await waitFor(() => assert.equal(savedBodies.length, 1));
      fireEvent.click(utils.getByRole("button", { name: "Add note" }));
      fireEvent.click(utils.getByRole("button", { name: "Add note" }));

      await waitFor(() => {
        assert.equal(savedBodies.length, 2);
        const latestNodes = savedBodies[1].nodes as Array<{ id: string }>;
        assert.ok(latestNodes.some((node) => node.id === "note-2"));
      });
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});
