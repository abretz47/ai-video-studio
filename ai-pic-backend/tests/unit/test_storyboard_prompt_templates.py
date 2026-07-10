from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


def test_storyboard_image_prompt_template_forbids_collage():
 base_prompt = "Old Guai, Zhi Xing final Ya Li test, Fu Zai Ti Sheng Zhi Feng Zhi. Jing Bie: medium shot Yun Jing: fixed Gou Tu: rule of thirds Jing Tou Qie Huan: opening"

 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORYBOARD_IMAGE_PROMPT.value,
 {"base_prompt": base_prompt, "reference_notes": []},
)

 assert base_prompt in prompt
 assert "only generate Dan Fu frame" in prompt
 assert "Bu Yao Pin Jie" in prompt
 assert "no collage" in prompt.lower()


def test_storyboard_image_fallback_template_forbids_collage():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORYBOARD_IMAGE_FALLBACK.value,
 {"frame_index": 1, "scene_number": 2},
)

 assert "only generate Dan Fu frame" in prompt
 assert "Bu Yao Pin Jie" in prompt


def test_storyboard_grid_sheet_template_allows_sheet_but_limits_text():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORYBOARD_GRID_SHEET.value,
 {
 "layout_label": "3x3",
 "panel_count": 9,
 "style": "vertical short-drama, cinematic realism",
 "panel_briefs": [
 "Panel 1 / clip clip-1: Lin Wan Zhan Zai rainy night doorway, Ni Hong Fan Guang, medium shot",
 "Panel 2 / clip clip-2: Chen Zhe Zuo Zai Che INT, Ce Lian Bei phone Ping Zhao Liang",
 ],
 },
)

 assert "3x3" in prompt
 assert "9-panel" in prompt
 assert "storyboard sheet" in prompt.lower()
 assert "panel numbers" in prompt
 assert "shot labels" in prompt
 assert "outside the cinematic panels" in prompt
 assert "No subtitles" in prompt
 assert "Lin Wan Zhan Zai rainy night doorway" in prompt


def test_storyboard_grid_video_template_scopes_to_one_panel():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORYBOARD_GRID_VIDEO.value,
 {
 "panel_index": 2,
 "clip_id": "clip-2",
 "video_prompt": "The camera remains still, capturing only his hesitant expression",
 },
)

 assert "Use panel 2 only" in prompt
 assert "clip-2" in prompt
 assert "Generate only this shot" in prompt
 assert "other panels" in prompt
 assert "camera keep Jing Zhi" in prompt


def test_storyboard_keyframe_template_forbids_collage():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORYBOARD_KEYFRAME.value,
 {"base_prompt": "Ye Se Zhong De office, Jing Bie: medium shot", "role": "start"},
)

 assert "only generate Dan Fu frame" in prompt
 assert "Jian Ji Bei Zhu" in prompt
 assert "Shou Zhen" in prompt


def test_storyboard_scene_template_forbids_on_screen_text():
 prompt = prompt_manager.render_prompt(
 "storyboard_scene",
 {
 "scene_plan_json": '{"scene_number": 1, "target_frames": 3, "frames": []}',
 "script_brief_json": '{"story": {"title": "test"}, "scenes": []}',
 "max_frames": None,
 },
)

 assert "Bu Yao Bao Han Ren He"frame Zhong Chu Xian De Wen Zi content"" in prompt
 assert "Wu Ke Du Wen Zi" in prompt


def test_storyboard_audio_visual_prompt_templates_exist():
 prompt = prompt_manager.render_prompt(
 "storyboard_audio_visual_dialogue_spoken",
 {"speaker": "Lin Wan", "intent": "Zhi Wen/Zhi Kong"},
)
 assert "Lin Wan" in prompt
 assert "no subtitles" in prompt

 prompt = prompt_manager.render_prompt(
 "storyboard_audio_visual_dialogue_voiceover",
 {"speaker": "Lin Wan", "intent": None},
)
 assert "Lin Wan" in prompt
 assert "voiceover" in prompt or "Nei Xin Du Bai" in prompt

 prompt = prompt_manager.render_prompt(
 "storyboard_audio_visual_dialogue_read_text",
 {"speaker": "Lin Wan"},
)
 assert "screen Wen Zi Mo Hu Bu Ke Du" in prompt
 assert "no subtitles" in prompt

 prompt = prompt_manager.render_prompt(
 "storyboard_audio_visual_action",
 {"action": "Ta Meng Di Ba file Pai Zai Zhuo Shang, Nu Shi Dui Fang"},
)
 assert "Pai Zai Zhuo Shang" in prompt
 assert "no subtitles" in prompt

 prompt = prompt_manager.render_prompt("storyboard_audio_visual_pause", {})
 assert "pause" in prompt
 assert "no subtitles" in prompt

 prompt = prompt_manager.render_prompt(
 "storyboard_audio_visual_context",
 {
 "base": "Lin Wan Kai Kou Shuo Hua, Zui Xing Qing Xi.",
 "character_cards": ["Lin Wan: Hei Chang Fa, Mi Se Mao Yi", "Chen Zhe: Duan Fa, Shen Se Jia Ke"],
 "environment": "Gong Yu Ke Ting, night",
 },
)
 assert "Jue Se Ka" in prompt
 assert "Huan Jing Mao Dian" in prompt
