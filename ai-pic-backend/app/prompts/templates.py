"""
Prompt template definitions

Ding Yi Le Ge ZhongAIRen Wu De prompt text template Chang Liang He Mei Ju
"""

from enum import Enum
from typing import Dict, List


class PromptCategory(Enum):
 """Prompt category enum"""

 CHARACTER = "character" # Jue Se Xiang Guan
 STORY = "story" # Gu Shi Xiang Guan
 EPISODE = "episode" # Ju Ji Xiang Guan
 SCRIPT = "script" # Ju Ben Xiang Guan
 IMAGE = "image" # Tu Xiang Xiang Guan
 GENERAL = "general" # Tong Yong


class PromptTemplate(Enum):
 """Prompt template enum"""

 # Jue Se Xiang Guan
 VIRTUAL_IP_CREATION = "virtual_ip_creation"
 VIRTUAL_IP_STYLE_PROMPT = "virtual_ip_style_prompt"
 CHARACTER_PROFILE = "character_profile"

 # Gu Shi Xiang Guan
 STORY_OUTLINE = "story_outline"
 STORY_SUMMARY = "story_summary"

 # Ju Ji Xiang Guan
 EPISODE_GENERATION = "episode_generation"
 EPISODE_OUTLINE = "episode_outline"
 EPISODE_STEP_OUTLINE = "episode_step_outline"
 EPISODE_STEP_OUTLINE_REPAIR = "episode_step_outline_repair"
 EPISODE_FROM_OUTLINE = "episode_from_outline"
 EPISODE_ENRICH = "episode_enrich" # Ju Ji Feng Fu(Dang Shi length Bu Zu Shi)
 EPISODE_DURATION_REJECT = "episode_duration_reject" # duration Bu Fu He Yao Qiu Shi Bo Hui Zhong generate
 EPISODE_LIST = "episode_list" # episode list generate

 # Ju Ben Xiang Guan
 SCRIPT_GENERATION = "script_generation"
 SCENE_WRITING = "scene_writing"
 DIALOGUE_WRITING = "dialogue_writing"
 SCRIPT_SCENES = "script_scenes"
 SCRIPT_DIALOGUES = "script_dialogues"
 SCRIPT_BEATS = "script_beats"
 SCRIPT_REVIEW = "script_review" # Ju Ben Shen He(dialogue/Wu Tai Zhi Shi Fen Lei Jiao Zheng)
 SCENE_DESCRIPTION = "scene_description" # Chang Jing Miao Shu
 SCRIPT_WORD_COUNT_CONSTRAINT = "script_word_count_constraint" # script word count Yue Shu
 DIALOGUE_DURATION_ADJUST = "dialogue_duration_adjust" # dialogue Shi length Tiao Zheng Jian Yi
 SCRIPT_SCORE = "script_score" # Ju Ben Ping Fen
 TRAFFIC_SHEET_GENERATION = "traffic_sheet_generation" # Tou Liu Biao generate

 # Fen Jing Xiang Guan
 STORYBOARD_GENERATION = "storyboard_generation" # Fen Jing Sheng Cheng
 STORYBOARD_SHOT = "storyboard_shot" # Dan Ge storyboard frame
 STORYBOARD_PLAN = "storyboard_plan" # Fen Jing Gui Hua
 STORYBOARD_SCENE = "storyboard_scene" # storyboard planning scene Zhan Kai
 STORYBOARD_KEYFRAME = "storyboard_keyframe" # storyboard Guan Jian Zhen prompt
 STORYBOARD_IMAGE_PROMPT = "storyboard_image_prompt" # storyboard image prompt Zu Zhuang
 STORYBOARD_IMAGE_FALLBACK = "storyboard_image_fallback" # storyboard image Que Sheng prompt
 STORYBOARD_DYNAMIC_IMAGE_PROMPT = (
 "storyboard_dynamic_image_prompt" # storyboard image Dong Tai prompt text Pi Liang generate
)
 STORYBOARD_GRID_SHEET = "storyboard_grid_sheet" # Gong Ge story Ban image prompt
 STORYBOARD_GRID_VIDEO = "storyboard_grid_video" # Gong Ge Mian Ban Sheng video prompt
 STORYBOARD_SCENE_GRID_PROMPT = (
 "storyboard_scene_grid_prompt" # scene Gong Ge storyboard image LLM prompt text generate
)
 STORYBOARD_SCENE_GRID_VIDEO_PROMPT = (
 "storyboard_scene_grid_video_prompt" # Gong Ge Tu Zhuan Lian Xu Cheng Pian prompt text generate
)
 STORYBOARD_AUDIO_VISUAL_DIALOGUE_SPOKEN = "storyboard_audio_visual_dialogue_spoken"
 STORYBOARD_AUDIO_VISUAL_DIALOGUE_VOICEOVER = (
 "storyboard_audio_visual_dialogue_voiceover"
)
 STORYBOARD_AUDIO_VISUAL_DIALOGUE_READ_TEXT = (
 "storyboard_audio_visual_dialogue_read_text"
)
 STORYBOARD_AUDIO_VISUAL_ACTION = "storyboard_audio_visual_action"
 STORYBOARD_AUDIO_VISUAL_PAUSE = "storyboard_audio_visual_pause"
 STORYBOARD_AUDIO_VISUAL_CONTEXT = "storyboard_audio_visual_context"

 # Tu Xiang Xiang Guan
 IMAGE_GENERATION = "image_generation"
 PORTRAIT_GENERATION = "portrait_generation"
 SCENE_IMAGE = "scene_image"
 ENVIRONMENT_IMAGE = "environment_image" # Huan Jing Tu Xiang
 ENVIRONMENT_IMAGE_VARIANT = "environment_image_variant" # environment image Tu Sheng image Bian Ti
 VIRTUAL_IP_IMAGE = "virtual_ip_image" # virtualIPWen Sheng Tu
 VIRTUAL_IP_IMAGE_VARIANT = "virtual_ip_image_variant" # virtualIPTu Sheng Tu

 # Shi Jian Zhou related
 TIMELINE_GAP_REASONING = "timeline_gap_reasoning" # dialogue Jian Ge Tui Li
 TIMELINE_GAP_REPAIR = "timeline_gap_repair" # dialogue Jian Ge repair

 # system prompt text (System Prompts)
 SYSTEM_PROMPT_STORY = "system_prompt_story" # story Chuang Zuo system prompt
 SYSTEM_PROMPT_SCRIPT = "system_prompt_script" # Ju Ben Chuang Zuo system prompt
 SYSTEM_PROMPT_JSON_STRICT = "system_prompt_json_strict" # Yan GeJSONXi Tong Ti Shi
 STORY_OUTLINE_REPAIR = "story_outline_repair"
 EPISODE_PLAN_REPAIR = "episode_plan_repair"


class ImageStyle(Enum):
 """Image style enum"""

 REALISTIC = "realistic"
 ANIME = "anime"
 CARTOON = "cartoon"
 PORTRAIT = "portrait"
 ARTISTIC = "artistic"
 SKETCH = "sketch"
 RENDER_3D = "3d"


class ImageCategory(Enum):
 """Image category enum"""

 PORTRAIT = "portrait"
 FULL_BODY = "full_body"
 ACTION = "action"
 EMOTION = "emotion"
 SCENE = "scene"
 CONCEPT = "concept"


class ScriptFormat(Enum):
 """Script format enum"""

 SCREENPLAY = "screenplay" # Dian Ying Ju Ben
 TELEPLAY = "teleplay" # Dian Shi Ju Ben
 STAGE = "stage" # Wu Tai Ju Ben
 AUDIO = "audio" # Yin Pin Ju Ben
 ANIMATION = "animation" # Dong Hua Ju Ben


class DialogueStyle(Enum):
 """Dialogue style enum"""

 NATURAL = "natural" # Zi Ran Dui Hua
 FORMAL = "formal" # Zheng Shi Dui Hua
 CASUAL = "casual" # Sui Yi Dui Hua
 DRAMATIC = "dramatic" # Xi Ju Dui Hua
 COMEDIC = "comedic" # Xi Ju Dui Hua


class PlotComplexity(Enum):
 """Plot complexity enum"""

 SIMPLE = "simple" # Jian Dan
 MEDIUM = "medium" # Zhong Deng
 COMPLEX = "complex" # Fu Za


class Pacing(Enum):
 """Jie Zou Mei Ju"""

 SLOW = "slow" # Man Jie Zou
 MEDIUM = "medium" # Zhong Deng Jie Zou
 FAST = "fast" # Kuai Jie Zou


# Template category mapping
TEMPLATE_CATEGORIES: Dict[PromptTemplate, PromptCategory] = {
 PromptTemplate.VIRTUAL_IP_CREATION: PromptCategory.CHARACTER,
 PromptTemplate.VIRTUAL_IP_STYLE_PROMPT: PromptCategory.CHARACTER,
 PromptTemplate.CHARACTER_PROFILE: PromptCategory.CHARACTER,
 PromptTemplate.STORY_OUTLINE: PromptCategory.STORY,
 PromptTemplate.STORY_SUMMARY: PromptCategory.STORY,
 PromptTemplate.EPISODE_GENERATION: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_OUTLINE: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_STEP_OUTLINE: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_STEP_OUTLINE_REPAIR: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_FROM_OUTLINE: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_ENRICH: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_DURATION_REJECT: PromptCategory.EPISODE,
 PromptTemplate.EPISODE_LIST: PromptCategory.EPISODE,
 PromptTemplate.SCRIPT_GENERATION: PromptCategory.SCRIPT,
 PromptTemplate.SCENE_WRITING: PromptCategory.SCRIPT,
 PromptTemplate.DIALOGUE_WRITING: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_SCENES: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_DIALOGUES: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_BEATS: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_REVIEW: PromptCategory.SCRIPT,
 PromptTemplate.SCENE_DESCRIPTION: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_WORD_COUNT_CONSTRAINT: PromptCategory.SCRIPT,
 PromptTemplate.DIALOGUE_DURATION_ADJUST: PromptCategory.SCRIPT,
 PromptTemplate.SCRIPT_SCORE: PromptCategory.SCRIPT,
 PromptTemplate.TRAFFIC_SHEET_GENERATION: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_GENERATION: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_SHOT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_PLAN: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_SCENE: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_KEYFRAME: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_IMAGE_PROMPT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_IMAGE_FALLBACK: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_DYNAMIC_IMAGE_PROMPT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_GRID_SHEET: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_GRID_VIDEO: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_SCENE_GRID_PROMPT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_SCENE_GRID_VIDEO_PROMPT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_SPOKEN: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_VOICEOVER: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_READ_TEXT: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_ACTION: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_PAUSE: PromptCategory.SCRIPT,
 PromptTemplate.STORYBOARD_AUDIO_VISUAL_CONTEXT: PromptCategory.SCRIPT,
 PromptTemplate.IMAGE_GENERATION: PromptCategory.IMAGE,
 PromptTemplate.PORTRAIT_GENERATION: PromptCategory.IMAGE,
 PromptTemplate.SCENE_IMAGE: PromptCategory.IMAGE,
 PromptTemplate.ENVIRONMENT_IMAGE: PromptCategory.IMAGE,
 PromptTemplate.ENVIRONMENT_IMAGE_VARIANT: PromptCategory.IMAGE,
 PromptTemplate.VIRTUAL_IP_IMAGE: PromptCategory.IMAGE,
 PromptTemplate.VIRTUAL_IP_IMAGE_VARIANT: PromptCategory.IMAGE,
 PromptTemplate.SYSTEM_PROMPT_STORY: PromptCategory.GENERAL,
 PromptTemplate.SYSTEM_PROMPT_SCRIPT: PromptCategory.GENERAL,
 PromptTemplate.SYSTEM_PROMPT_JSON_STRICT: PromptCategory.GENERAL,
 PromptTemplate.STORY_OUTLINE_REPAIR: PromptCategory.GENERAL,
 PromptTemplate.EPISODE_PLAN_REPAIR: PromptCategory.GENERAL,
 PromptTemplate.EPISODE_STEP_OUTLINE_REPAIR: PromptCategory.GENERAL,
 # Shi Jian Zhou related
 PromptTemplate.TIMELINE_GAP_REASONING: PromptCategory.SCRIPT,
 PromptTemplate.TIMELINE_GAP_REPAIR: PromptCategory.SCRIPT,
}

from app.prompts import template_defaults as _template_defaults # noqa: E402

DEFAULT_GENERATION_PARAMS = _template_defaults.DEFAULT_GENERATION_PARAMS
NEGATIVE_PROMPTS = _template_defaults.NEGATIVE_PROMPTS
QUALITY_ENHANCERS = _template_defaults.QUALITY_ENHANCERS
TEMPLATE_EXAMPLES = _template_defaults.TEMPLATE_EXAMPLES


def get_template_by_category(category: PromptCategory) -> List[PromptTemplate]:
 """Get template list by category"""
 return [
 template for template, cat in TEMPLATE_CATEGORIES.items() if cat == category
 ]


def get_category_by_template(template: PromptTemplate) -> PromptCategory:
 """Get category by template"""
 return TEMPLATE_CATEGORIES.get(template, PromptCategory.GENERAL)
