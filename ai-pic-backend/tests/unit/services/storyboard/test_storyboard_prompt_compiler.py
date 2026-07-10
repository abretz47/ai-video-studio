from app.services.storyboard.storyboard_prompt_compiler import StoryboardPromptCompiler


def test_storyboard_prompt_compiler_preserves_shot_plan_sections():
 frame = {
 "frame_number": 1,
 "timeline_clip_id": "video_scene_1_beat_1_001",
 "scene_id": 12,
 "beat_id": 34,
 "description": "Lin Wan Zhan Zai rainy night doorway",
 "shot_type": "medium shot",
 "camera_movement": "Huan Man Tui Jin",
 "composition": "Lin Wan Zai Zuo San Fen Xian, Men Kuang Qie Fen You Ce Fu Kong Jian",
 "reference_images": ["https://cdn.example/linwan.png"],
 "shot_plan_prompt_layers": {
 "direction_anchor": "a lonely search toward the rainy-night doorway",
 "aesthetic_reference": "IMAX film, Panavision C lens, cold neon rain",
 "composition_geometry": "left third subject, doorway as vertical split",
 "motion_timeline": [
 {"at_ms": 0, "action": "Lin Wan Ting Zai doorway"},
 {"at_ms": 1400, "action": "Yu Shui Luo Zai Jian Tou"},
 {"at_ms": 2800, "action": "Ta Tai Tou Kan Xiang Men Nei"},
 ],
 "emotional_landing": "restrained loneliness in the cold rain",
 },
 }

 compiled = StoryboardPromptCompiler().compile_frame(
 frame,
 reference_notes=[{"type": "character", "name": "Lin Wan"}],
 provider="openai",
 negative_prompt_supported=False,
)

 assert compiled["version"] == "storyboard_prompt_v2"
 assert compiled["clip_identity"]["timeline_clip_id"] == "video_scene_1_beat_1_001"
 assert "Direction anchor: a lonely search toward the rainy-night doorway" in compiled["image_prompt"]
 assert "Aesthetic reference: IMAX film" in compiled["image_prompt"]
 assert "Composition geometry: left third subject" in compiled["image_prompt"]
 assert "0ms: Lin Wan Ting Zai doorway" in compiled["image_prompt"]
 assert "Emotional landing: restrained loneliness in the cold rain" in compiled["image_prompt"]
 assert "No readable text" in compiled["image_prompt"]
 assert "negative_prompt not supported; constraints inlined" in compiled["warnings"]
 assert len(compiled["prompt_sha256"]) == 64


def test_storyboard_prompt_compiler_reads_timeline_shot_plan_from_source_refs():
 frame = {
 "description": "doorway Duan Zan pause",
 "source_refs": {
 "timeline_shot_plan": {
 "clip_id": "clip_from_timeline",
 "scene_id": "scene-1",
 "beat_id": "beat-2",
 "direction_anchor": "from Men Wai Xiang INT Kui Jian tense Qi Fen",
 "aesthetic_reference": "cool tungsten contrast",
 "composition_geometry": "door frame splits foreground and background",
 "motion_timeline": [
 {"at_ms": 0, "action": "hand reaches toward the handle"},
 {"at_ms": 900, "action": "the hand stops before touching it"},
 ],
 "emotional_landing": "suspended hesitation",
 }
 },
 }

 compiled = StoryboardPromptCompiler().compile_frame(frame)

 assert compiled["clip_identity"]["timeline_clip_id"] == "clip_from_timeline"
 assert "Direction anchor: from Men Wai Xiang INT Kui Jian tense Qi Fen" in compiled["image_prompt"]
 assert "door frame splits foreground" in compiled["image_prompt"]
 assert "the hand stops before touching it" in compiled["i2v_motion_prompt"]


def test_storyboard_prompt_compiler_builds_distinct_keyframe_prompts():
 frame = {
 "description": "Chen Zhe Zuo Zai Che INT, Ce Lian Bei phone Ping Zhao Liang",
 "shot_plan_prompt_layers": {
 "motion_timeline": [
 {"at_ms": 0, "action": "Ta Di Tou Ding Zhe screen"},
 {"at_ms": 2200, "action": "Ta Chi Yi Hou Tai Yan Kan Xiang Chuang Wai"},
 ]
 },
 }

 compiled = StoryboardPromptCompiler().compile_frame(frame)

 assert compiled["start_keyframe_prompt"]!= compiled["end_keyframe_prompt"]
 assert "Opening keyframe" in compiled["start_keyframe_prompt"]
 assert "Ta Di Tou Ding Zhe screen" in compiled["start_keyframe_prompt"]
 assert "Ending keyframe" in compiled["end_keyframe_prompt"]
 assert "Ta Chi Yi Hou Tai Yan Kan Xiang Chuang Wai" in compiled["end_keyframe_prompt"]


def test_storyboard_prompt_compiler_i2v_prompt_focuses_on_motion_not_reference_visuals():
 frame = {
 "description": "Chuan Shen Se Xi Zhuang De Nan Ren Zuo Zai Che INT, rainy night Ni Hong Fan She Zai Che Chuang Shang",
 "shot_plan_prompt_layers": {
 "camera_movement": "locked tripod shot",
 "motion_timeline": [
 {"at_ms": 0, "action": "the subject remains still"},
 {"at_ms": 1200, "action": "rain moves across the window"},
 {"at_ms": 2400, "action": "the subject slowly turns his eyes"},
 ],
 },
 }

 compiled = StoryboardPromptCompiler().compile_frame(frame)

 assert "Use the reference image for identity" in compiled["i2v_motion_prompt"]
 assert "Motion timeline:" in compiled["i2v_motion_prompt"]
 assert "the subject slowly turns his eyes" in compiled["i2v_motion_prompt"]
 assert "dark suit" not in compiled["i2v_motion_prompt"].lower()
 assert "neon" not in compiled["i2v_motion_prompt"].lower()
