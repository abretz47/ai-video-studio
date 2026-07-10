from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


def test_story_outline_template_resolves_tv_series_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORY_OUTLINE.value,
 {
 "title": "Ce Shi Gu Shi",
 "story_format": "tv_series",
 "genre": "drama",
 "characters": [{"name": "Protagonist", "description": "test"}],
 "market_region": None,
 "micro_genre": None,
 "theme": None,
 "target_audience": None,
 "duration_minutes": 60,
 "setting_time": None,
 "setting_location": None,
 "world_building": None,
 "additional_requirements": None,
 "style_preferences": [],
 "content_restrictions": [],
 },
)

 assert "Dian Shi Ju/Wang Ju" in prompt


def test_story_outline_template_resolves_film_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORY_OUTLINE.value,
 {
 "title": "Ce Shi Dian Ying",
 "story_format": "film",
 "genre": "drama",
 "characters": [{"name": "Protagonist", "description": "test"}],
 "market_region": None,
 "micro_genre": None,
 "theme": None,
 "target_audience": None,
 "duration_minutes": 120,
 "setting_time": None,
 "setting_location": None,
 "world_building": None,
 "additional_requirements": None,
 "style_preferences": [],
 "content_restrictions": [],
 },
)

 assert "Dian Ying Bian Ju" in prompt


def test_story_outline_template_resolves_short_drama_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.STORY_OUTLINE.value,
 {
 "title": "Ce Shi Duan Ju",
 "story_format": "short_drama",
 "genre": "drama",
 "characters": [{"name": "Protagonist", "description": "test"}],
 "market_region": "Southeast Asia",
 "micro_genre": "Ba Zong Fu Chou",
 "theme": None,
 "target_audience": None,
 "duration_minutes": 60,
 "setting_time": None,
 "setting_location": None,
 "world_building": None,
 "additional_requirements": None,
 "style_preferences": [],
 "content_restrictions": [],
 },
)

 assert "【short drama Ying Xing Yao Qiu】Mei Ji Bi You Shuang Dian" in prompt


def test_system_prompt_story_resolves_film_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.SYSTEM_PROMPT_STORY.value, {"story_format": "film"}
)

 assert "Dian Ying Bian Ju" in prompt


def test_episode_generation_template_resolves_tv_series_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_GENERATION.value,
 {
 "story": {
 "title": "Ce Shi Gu Shi",
 "genre": "drama",
 "story_format": "tv_series",
 },
 "episode_count": 3,
 "episode_duration": 45,
 "focus_characters": [],
 "plot_complexity": "medium",
 "pacing": "medium",
 "additional_requirements": None,
 "style_preferences": [],
 },
)

 assert "Dian Shi Ju/Wang Ju" in prompt


def test_episode_generation_template_resolves_short_drama_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_GENERATION.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode_count": 5,
 "episode_duration": 3,
 "focus_characters": [],
 "plot_complexity": "medium",
 "pacing": "fast",
 "additional_requirements": None,
 "style_preferences": [],
 },
)

 assert "【short drama Ying Xing Gui Ze】Mei Ji Bi You Shuang Dian" in prompt


def test_script_generation_template_resolves_short_drama_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.SCRIPT_GENERATION.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode": {"episode_number": 1, "title": "Di Yi Ji", "duration_minutes": 3},
 "format_type": "teleplay",
 "language": "zh-CN",
 "dialogue_style": "dramatic",
 "scene_detail_level": "medium",
 "additional_requirements": None,
 "style_preferences": [],
 },
)

 assert "PAYOFF" in prompt
 assert "CLIFFHANGER" in prompt


def test_episode_from_outline_template_resolves_short_drama_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_FROM_OUTLINE.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "outline": {
 "episode_number": 1,
 "title": "Di Yi Ji",
 "logline": "testlogline",
 },
 "previous_episodes": [],
 "episode_duration": 3,
 "plot_complexity": "medium",
 "pacing": "fast",
 "additional_requirements": None,
 "style_preferences": [],
 },
)

 assert "【short drama Ying Xing Gui Ze】Mei Ji Bi You Shuang Dian" in prompt


def test_episode_duration_reject_template_resolves_short_drama_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_DURATION_REJECT.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "outline": {
 "episode_number": 1,
 "title": "Di Yi Ji",
 "logline": "testlogline",
 },
 "previous_episodes": [],
 "rejected_episode": {
 "episode_number": 1,
 "title": "Di Yi Ji",
 "summary": "Ce Shi Gai Yao",
 "scenes": [
 {
 "scene_number": 1,
 "summary": "Ce Shi Chang Jing",
 "estimated_duration_seconds": 30,
 }
 ],
 },
 "target_duration_seconds": 180,
 "current_duration_seconds": 150,
 "rejection_reason": "duration_too_short",
 "attempt_number": 2,
 "focus_characters": [],
 "episode_duration": 3,
 "plot_complexity": "medium",
 "pacing": "fast",
 },
)

 assert "【short drama Ying Xing Gui Ze】Mei Ji Bi You Shuang Dian" in prompt


def test_script_scenes_template_resolves_film_variant():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.SCRIPT_SCENES.value,
 {
 "story": {"title": "Ce Shi Dian Ying", "genre": "drama", "story_format": "film"},
 "episode": {"episode_number": 1, "title": "Di Yi Mu"},
 "scene_detail_level": "medium",
 "format_type": "screenplay",
 "language": "zh-CN",
 "style_preferences": [],
 "additional_requirements": "",
 "duration_minutes": 120,
 "min_scene_seconds": 10,
 "max_scene_seconds": 120,
 },
)

 assert "Dian Ying Mo Shi" in prompt


def test_script_scenes_short_drama_production_prompt_has_quality_brief():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.SCRIPT_SCENES.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode": {"episode_number": 1, "title": "Di Yi Ji"},
 "scene_detail_level": "medium",
 "format_type": "screenplay",
 "language": "zh-CN",
 "style_preferences": [],
 "additional_requirements": "",
 "duration_minutes": 3,
 "min_scene_seconds": 10,
 "max_scene_seconds": 120,
 "generation_mode": "production",
 "production_mode": True,
 "script_score_thresholds": {"overall": 4.5, "dimension": 4.2},
 },
)

 assert "Sheng Chan Ji scene planning Ying Men Kan" in prompt
 assert "timestamp skeleton" in prompt
 assert "0-3 seconds ignition" in prompt
 assert "close-up reaction" in prompt
 assert "customer Zhang total Gei Chu60Miao Che Dan" in prompt
 assert "Shu Zi Bu Hui Sa Huang, Kan Shi Jian Chuo" in prompt
 assert "Gai Wan Gei Ni20Wan, Bu Zuo Jiu Cai you" in prompt


def test_script_scenes_short_drama_standard_prompt_omits_production_brief():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.SCRIPT_SCENES.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode": {"episode_number": 1, "title": "Di Yi Ji"},
 "scene_detail_level": "medium",
 "format_type": "screenplay",
 "language": "zh-CN",
 "style_preferences": [],
 "additional_requirements": "",
 "duration_minutes": 3,
 "min_scene_seconds": 10,
 "max_scene_seconds": 120,
 "generation_mode": "standard",
 "production_mode": False,
 "script_score_thresholds": {"overall": 4.5, "dimension": 4.2},
 },
)

 assert "Sheng Chan Ji scene planning Ying Men Kan" not in prompt
 assert "timestamp skeleton" not in prompt
