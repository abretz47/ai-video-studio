from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


def test_story_outline_short_drama_production_prompt_has_researched_brief():
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
 "generation_mode": "production",
 "production_mode": True,
 "story_contract_version": "story_contract_v1",
 },
)

 assert "structured_story_contract" in prompt
 assert "Da Qi Dai" in prompt
 assert "Xiao Qi Dai Jie Ti" in prompt
 assert "information Cha She Ji" in prompt
 assert "Qian San Ji Li Zhu Xian" in prompt
 assert "Shao Xie Xin Li, Duo Xie Xing Wei" in prompt
 assert "Jin Zhi Zhi Xie"Qing Xu Sheng Ji, Tui Jin Ju Qing, Ju Da Fan Zhuan"" in prompt


def test_story_outline_short_drama_standard_prompt_omits_production_contract():
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
 "generation_mode": "standard",
 "production_mode": False,
 "story_contract_version": "story_contract_v1",
 },
)

 assert "structured_story_contract" not in prompt
 assert "Qian San Ji Li Zhu Xian" not in prompt


def test_episode_step_outline_production_prompt_requires_contract_and_beats():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_STEP_OUTLINE.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode_count": 3,
 "episode_duration": 3,
 "focus_characters": [],
 "plot_complexity": "medium",
 "pacing": "fast",
 "additional_requirements": None,
 "style_preferences": [],
 "generation_mode": "production",
 "production_mode": True,
 "episode_contract_version": "episode_contract_v1",
 },
)

 assert "structured_episode_contract" in prompt
 assert "production Bu Jie Shou logline-only" in prompt
 assert "0-3 seconds ignition" in prompt
 assert "Qian 30 seconds Ting Liu Li You" in prompt
 assert "episode_goal" in prompt
 assert "next_tap_reason" in prompt


def test_episode_generation_production_prompt_has_dialogue_and_closeup_contract():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.EPISODE_GENERATION.value,
 {
 "story": {
 "title": "Ce Shi Duan Ju",
 "genre": "drama",
 "story_format": "short_drama",
 },
 "episode_count": 3,
 "episode_duration": 3,
 "focus_characters": [],
 "plot_complexity": "medium",
 "pacing": "fast",
 "additional_requirements": None,
 "style_preferences": [],
 "generation_mode": "production",
 "production_mode": True,
 "episode_contract_version": "episode_contract_v1",
 },
)

 assert "structured_episode_contract" in prompt
 assert "0-3 seconds ignition" in prompt
 assert "dialogue_function" in prompt
 assert "reveal/threat/decision/counterattack/payoff" in prompt
 assert "9:16 close-up" in prompt
 assert "Bu Neng Mo Wei Ying Sai Xin crisis" in prompt


def test_episode_from_outline_production_prompt_has_visual_action_contract():
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
 "generation_mode": "production",
 "production_mode": True,
 "episode_contract_version": "episode_contract_v1",
 },
)

 assert "structured_episode_contract" in prompt
 assert "visual_anchor" in prompt
 assert "Xin Xi Bian Hua" in prompt
 assert "dialogue_function" in prompt
 assert "final button/cliffhanger" in prompt
