from app.services.timeline_clip_visual_prompt_builder import (
 PROMPT_CONTRACT_VERSION,
 build_timeline_clip_keyframe_frames,
 build_timeline_clip_video_motion_prompt,
)


def clip_with_motion_plan() -> dict:
 return {
 "clip_id": "video_scene_001_beat_002_001",
 "track_type": "video",
 "text": "Chen Zhe Zuo Zai Che INT, Ce Lian Bei phone Ping Zhao Liang.",
 "source_refs": {
 "timeline_shot_plan": {
 "visual_prompt": "Chen Zhe Zuo Zai rainy night Che INT, phone screen Leng Guang Zhao Liang Ce Lian",
 "video_prompt": "camera Huan Man Tui Jin, Yu Shui Yan Che Chuang Hua Luo",
 "direction_anchor": "rainy night Che Nei De Chi Yi Yu Jing Jue",
 "aesthetic_reference": "live action cinema, cool neon rain",
 "shot_type": "tight medium close-up",
 "camera_movement": "slow push-in",
 "composition_geometry": "face on right third, window reflections left",
 "motion_timeline": [
 {"at_ms": 0, "action": "Ta Di Tou Ding Zhe phone screen"},
 {"at_ms": 900, "action": "Ta De Shou Zhi Ting Zai Bo Hao Jian Shang"},
 {"at_ms": 1800, "action": "Ta Tai Yan Kan Xiang Yu Zhong De Che Chuang"},
 ],
 "emotional_landing": "Ke Zhi De Huai Yi Luo Dian",
 }
 },
 }


def test_keyframe_prompts_use_first_and_last_motion_points() -> None:
 frames, metadata = build_timeline_clip_keyframe_frames(clip_with_motion_plan())

 assert [frame["role"] for frame in frames] == ["start_frame", "end_frame"]
 assert "Ta Di Tou Ding Zhe phone screen" in frames[0]["prompt"]
 assert "Ta Tai Yan Kan Xiang Yu Zhong De Che Chuang" in frames[1]["prompt"]
 assert frames[0]["prompt"]!= frames[1]["prompt"]
 assert metadata["prompt_contract_version"] == PROMPT_CONTRACT_VERSION
 assert metadata["visual_prompt_source"] == "timeline_shot_plan.visual_prompt"
 assert metadata["motion_prompt_source"] == "timeline_shot_plan.video_prompt"


def test_video_motion_prompt_prefers_operator_override() -> None:
 prompt, metadata = build_timeline_clip_video_motion_prompt(
 clip_with_motion_plan(),
 override="only Bao Liu Qing Wei Hu Xi He Chuang Wai Yu Di, Jing Tou Gu Ding",
)

 assert "only Bao Liu Qing Wei Hu Xi He Chuang Wai Yu Di" in prompt
 assert "slow push-in" not in prompt
 assert metadata["motion_prompt_source"] == "operator_override"


def test_video_motion_prompt_without_override_keeps_motion_and_constraints() -> None:
 prompt, metadata = build_timeline_clip_video_motion_prompt(clip_with_motion_plan())

 assert "Generate only the selected Timeline clip" in prompt
 assert "slow push-in" in prompt
 assert "0ms: Ta Di Tou Ding Zhe phone screen" in prompt
 assert "1800ms: Ta Tai Yan Kan Xiang Yu Zhong De Che Chuang" in prompt
 assert "No subtitles" in prompt
 assert metadata["prompt_contract_version"] == PROMPT_CONTRACT_VERSION


def test_video_motion_prompt_expands_short_timeline_slot_for_provider() -> None:
 clip = clip_with_motion_plan()
 clip["duration_ms"] = 1240
 clip["source_refs"]["timeline_shot_plan"]["video_prompt"] = (
 "Plot: Jie Tu Tou Dao Zhu Ping. Duration: 1240ms. "
 "Motion timeline: [{\"at_ms\": 0, \"action\": \"Jie Tu Chu Xian\"}]"
)

 prompt, _metadata = build_timeline_clip_video_motion_prompt(clip)

 assert "Duration: 1240ms" not in prompt
 assert "source timeline slot: 1240ms; provider render duration: 4s" in prompt
 assert "render as one continuous 4-second shot" in prompt
 assert "Avoid a flicker-fast micro clip" in prompt
