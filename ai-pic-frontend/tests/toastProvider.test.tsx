import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import React from "react";
import { cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import { JSDOM } from "jsdom";

import {
  ToastProvider,
  useToast,
} from "../src/components/shared/notifications";
import type { NotifyVariant } from "../src/components/shared/notifications";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost",
});
(globalThis as any).window = dom.window;
(globalThis as any).self = dom.window;
(globalThis as any).document = dom.window.document;
(globalThis as any).HTMLElement = dom.window.HTMLElement;
(globalThis as any).localStorage = dom.window.localStorage;

function Harness({
  onReady,
}: {
  onReady: (
    notify: (
      message: string,
      variant?: NotifyVariant,
      options?: { durationMs?: number; title?: string },
    ) => void,
  ) => void;
}) {
  const { notify } = useToast();
  onReady(notify);
  return null;
}

function renderToastHarness() {
  let notifyFn:
    | ((
        message: string,
        variant?: NotifyVariant,
        options?: { durationMs?: number; title?: string },
      ) => void)
    | null = null;
  const utils = render(
    React.createElement(
      ToastProvider,
      null,
      React.createElement(Harness, {
        onReady: (notify) => {
          notifyFn = notify;
        },
      }),
    ),
    { container: dom.window.document.body },
  );
  assert.ok(notifyFn);
  return { utils, notify: notifyFn! };
}

describe("toast provider", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders success toasts as status and errors as alert", async () => {
    const { utils, notify } = renderToastHarness();
    notify("Script generation task submitted", "success");
    notify("Generation failed: insufficient balance", "error");

    await waitFor(() => {
      assert.ok(utils.getByText("Script generation task submitted"));
      assert.ok(utils.getByText("Generation failed: insufficient balance"));
    });
    const statuses = utils.getAllByRole("status");
    const alerts = utils.getAllByRole("alert");
    assert.equal(statuses.length, 1);
    assert.equal(alerts.length, 1);
  });

  it("auto-dismisses after the configured duration", async () => {
    const { utils, notify } = renderToastHarness();
    notify("Short-lived notice", "info", { durationMs: 30 });
    await waitFor(() => assert.ok(utils.getByText("Short-lived notice")));
    await waitFor(() => assert.equal(utils.queryByText("Short-lived notice"), null), {
      timeout: 2000,
    });
  });

  it("dismisses on manual close", async () => {
    const { utils, notify } = renderToastHarness();
    notify("Close me manually", "warning", { durationMs: 60000 });
    await waitFor(() => assert.ok(utils.getByText("Close me manually")));
    fireEvent.click(utils.getByLabelText("Close notification"));
    await waitFor(() => assert.equal(utils.queryByText("Close me manually"), null));
  });

  it("caps the visible stack at five toasts", async () => {
    const { utils, notify } = renderToastHarness();
    for (let index = 1; index <= 7; index++) {
      notify(`Notice ${index}`, "info", { durationMs: 60000 });
    }
    await waitFor(() => assert.ok(utils.getByText("Notice 7")));
    assert.equal(utils.getAllByRole("status").length, 5);
    assert.equal(utils.queryByText("Notice 1"), null);
    assert.equal(utils.queryByText("Notice 2"), null);
  });

  it("renders an optional title", async () => {
    const { utils, notify } = renderToastHarness();
    notify("Final cut is ready", "success", { title: "Render complete", durationMs: 60000 });
    await waitFor(() => {
      assert.ok(utils.getByText("Render complete"));
      assert.ok(utils.getByText("Final cut is ready"));
    });
  });
});
