"""Unit tests: dynamic prompt context builder and cache."""

from __future__ import annotations

from app.services.storyboard.dynamic_prompt.cache import (
 compute_input_fingerprint,
 read_cached_bundle,
)
from app.services.storyboard.dynamic_prompt.context_builder import (
 build_frame_input,
 build_scene_context,
 group_target_frames_by_scene,
)
from tests.unit.services.storyboard.dynamic_prompt_fixtures import (
 make_frames,
 make_ref_ctx,
 make_script,
)


def test_scene_context_filters_by_scene_number():
 context = build_scene_context(make_script(), 1, make_ref_ctx(), ["Zui Bu Ru Chang"])
 assert context["scene"]["location"] == "outside the tavern"
 assert context["dialogues"] == ["you He Duo Le Ba"]
 assert context["stage_notes"] == ["Di Ren from Liang Ce Bi Jin"]
 assert context["characters"] == [
 {"name": "A-Long", "appearance": "30Sui Wu Zhe, Jiu Bu Yi Duan Da"}
 ]
 assert "Zui Quan" in context["story_tone"]


def test_scene_context_character_fallback_by_name_match():
 ctx = make_ref_ctx()
 ctx.scene_by_number = {}
 context = build_scene_context(make_script(), 1, ctx, ["A Long Zui Bu Ru Chang"])
 assert context["characters"][0]["name"] == "A-Long"


def test_scene_context_handles_missing_scene():
 context = build_scene_context(make_script(scenes=[]), 9, make_ref_ctx(), [])
 assert context["scene"]["scene_number"] == 9
 assert context["dialogues"] == []


def test_frame_input_includes_neighbor_summaries():
 frames = make_frames()
 frame_input = build_frame_input(frames, 1)
 assert frame_input["prev_summary"] == "Zui Bu Ru Chang"
 assert frame_input["next_summary"] == ""
 assert frame_input["duration"] == 0.9


def test_group_target_frames_by_scene_skips_invalid_indexes():
 frames = make_frames() + [{"scene_number": 2, "description": "x"}]
 groups = group_target_frames_by_scene(frames, [0, 1, 2, 99])
 assert groups == {1: [0, 1], 2: [2]}


def test_cache_roundtrip_and_fingerprint_mismatch():
 scene_context = {"scene": {"scene_number": 1}}
 frame_input = {"frame_index": 0, "description": "a"}
 fingerprint = compute_input_fingerprint(scene_context, frame_input)
 frame = {
 "llm_prompt_bundle": {
 "input_sha": fingerprint,
 "image_prompt": "i",
 "start_keyframe_prompt": "s",
 "end_keyframe_prompt": "e",
 }
 }
 assert read_cached_bundle(frame, fingerprint) is not None
 changed = compute_input_fingerprint(
 scene_context, {**frame_input, "description": "b"}
)
 assert changed!= fingerprint
 assert read_cached_bundle(frame, changed) is None


def test_cache_rejects_bundle_with_empty_prompt():
 frame = {
 "llm_prompt_bundle": {
 "input_sha": "x",
 "image_prompt": "",
 "start_keyframe_prompt": "s",
 "end_keyframe_prompt": "e",
 }
 }
 assert read_cached_bundle(frame, "x") is None
