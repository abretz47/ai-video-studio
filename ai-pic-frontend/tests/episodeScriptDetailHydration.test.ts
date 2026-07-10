import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  mergeScriptDetail,
  scriptNeedsDetail,
} from "../src/hooks/episode/scriptDetailHydration";
import type { Script } from "../src/utils/api/types";

const baseScript = {
  id: 131,
  business_id: "script-business-id",
  episode_id: 142,
  title: "Rainy Night Evidence Chain - Script",
  format_type: "screenplay",
  language: "zh-CN",
  status: "draft",
  version: "1.0",
  created_at: "2026-05-08T08:56:14",
  updated_at: "2026-05-08T11:50:47",
} satisfies Script;

describe("episode script detail hydration", () => {
  it("detects lightweight episode script list items", () => {
    assert.equal(scriptNeedsDetail(baseScript), true);
    assert.equal(
      scriptNeedsDetail({
        ...baseScript,
        content: "Body text",
        scenes: [{ scene_number: 1 }],
        dialogues: [{ scene_number: 1, character: "Lin", content: "Alarm?" }],
        stage_directions: [{ scene_number: 1, content: "Phone vibrates" }],
      }),
      false,
    );
  });

  it("merges a fetched script detail into the existing list", () => {
    const detail = {
      ...baseScript,
      content: "Body text",
      scenes: [{ scene_number: 1, description: "Opening" }],
      dialogues: [{ scene_number: 1, character: "Lin", content: "Alarm?" }],
      stage_directions: [{ scene_number: 1, content: "Phone vibrates" }],
    } satisfies Script;

    const merged = mergeScriptDetail([baseScript], detail);

    assert.equal(merged.length, 1);
    assert.deepEqual(merged[0].dialogues, detail.dialogues);
    assert.deepEqual(merged[0].stage_directions, detail.stage_directions);
  });
});
