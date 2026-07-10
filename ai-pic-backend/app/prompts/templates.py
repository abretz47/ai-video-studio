"""
Prompt template definitions

Defines prompt template constants and enums for various AI tasks.
"""

from enum import Enum
from typing import Dict, List


class PromptCategory(Enum):
 """Prompt category enum"""

 CHARACTER = "character" # character-related
 STORY = "story" # story-related
 EPISODE = "episode" # episode-related
 SCRIPT = "script" # script-related
 IMAGE = "image" # image-related
 GENERAL = "general" # general-purpose


class PromptTemplate(Enum):
 """Prompt template enum"""

 # character-related
 VIRTUAL_IP_CREATION = "virtual_ip_creation"
 VIRTUAL_IP_STYLE_PROMPT = "virtual_ip_style_prompt"
 CHARACTER_PROFILE = "character_profile"

 # story-related
 STORY_OUTLINE = "story_outline"
 STORY_SUMMARY = "story_summary"

 # episode-related
 EPISODE_GENERATION = "episode_generation"
 EPISODE_OUTLINE = "episode_outline"
 EPISODE_STEP_OUTLINE = "episode_step_outline"
 EPISODE_STEP_OUTLINE_REPAIR = "episode_step_outline_repair"
 EPISODE_FROM_OUTLINE = "episode_from_outline"
 EPISODE_ENRICH = "episode_enrich" # episode enrichment (when duration is insufficient)
 EPISODE_DURATION_REJECT = "episode_duration_reject" # regenerate when duration requirements are not met
 EPISODE_LIST = "episode_list" # Episode list generation

 # script-related
 SCRIPT_GENERATION = "script_generation"
 SCENE_WRITING = "scene_writing"
 DIALOGUE_WRITING = "dialogue_writing"
 SCRIPT_SCENES = "script_scenes"
 SCRIPT_DIALOGUES = "script_dialogues"
 SCRIPT_BEATS = "script_beats"
 SCRIPT_REVIEW = "script_review" # Script review (dialogue/stage direction classification correction)
 SCENE_DESCRIPTION = "scene_description" # scene description
 SCRIPT_WORD_COUNT_CONSTRAINT = "script_word_count_constraint" # script word-count constraint
 DIALOGUE_DURATION_ADJUST = "dialogue_duration_adjust" # dialogue duration adjustment suggestions
 SCRIPT_SCORE = "script_score" # script scoring
 TRAFFIC_SHEET_GENERATION = "traffic_sheet_generation" # traffic sheet generation

 # storyboard-related
 STORYBOARD_GENERATION = "storyboard_generation" # storyboard generation
 STORYBOARD_SHOT = "storyboard_shot" # single storyboard frame
 STORYBOARD_PLAN = "storyboard_plan" # storyboard planning
 STORYBOARD_SCENE = "storyboard_scene" # storyboard planning scene expansion
 STORYBOARD_KEYFRAME = "storyboard_keyframe" # storyboard keyframe prompt
 STORYBOARD_IMAGE_PROMPT = "storyboard_image_prompt" # storyboard image prompt assembly
 STORYBOARD_IMAGE_FALLBACK = "storyboard_image_fallback" # storyboard fallback image prompt
 STORYBOARD_DYNAMIC_IMAGE_PROMPT = (
 "storyboard_dynamic_image_prompt" # batch generation of dynamic storyboard image prompts
)
 STORYBOARD_GRID_SHEET = "storyboard_grid_sheet" # grid storyboard image prompt
 STORYBOARD_GRID_VIDEO = "storyboard_grid_video" # grid panel video prompt
 STORYBOARD_SCENE_GRID_PROMPT = (
 "storyboard_scene_grid_prompt" # scene grid storyboard image LLM prompt generation
)
 STORYBOARD_SCENE_GRID_VIDEO_PROMPT = (
 "storyboard_scene_grid_video_prompt" # grid-to-sequence prompt generation
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

 # image-related
 IMAGE_GENERATION = "image_generation"
 PORTRAIT_GENERATION = "portrait_generation"
 SCENE_IMAGE = "scene_image"
 ENVIRONMENT_IMAGE = "environment_image" # Environment image
 ENVIRONMENT_IMAGE_VARIANT = "environment_image_variant" # Environment image variation (image-to-image)
 VIRTUAL_IP_IMAGE = "virtual_ip_image" # Virtual IP text-to-image
 VIRTUAL_IP_IMAGE_VARIANT = "virtual_ip_image_variant" # Virtual IP image-to-image

 # timeline-related
 TIMELINE_GAP_REASONING = "timeline_gap_reasoning" # dialogue gap reasoning
 TIMELINE_GAP_REPAIR = "timeline_gap_repair" # dialogue gap repair

 # system prompt text (System Prompts)
 SYSTEM_PROMPT_STORY = "system_prompt_story" # story creation system prompt
 SYSTEM_PROMPT_SCRIPT = "system_prompt_script" # script creation system prompt
 SYSTEM_PROMPT_JSON_STRICT = "system_prompt_json_strict" # strict JSON system prompt
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

 SCREENPLAY = "screenplay" # Film script
 TELEPLAY = "teleplay" # TV script
 STAGE = "stage" # Stage script
 AUDIO = "audio" # Audio script
 ANIMATION = "animation" # Animation script


class DialogueStyle(Enum):
 """Dialogue style enum"""

 NATURAL = "natural" # Natural dialogue
 FORMAL = "formal" # Formal dialogue
 CASUAL = "casual" # Casual dialogue
 DRAMATIC = "dramatic" # Dramatic dialogue
 COMEDIC = "comedic" # Dramatic dialogue


class PlotComplexity(Enum):
 """Plot complexity enum"""

 SIMPLE = "simple" # Simple
 MEDIUM = "medium" # Medium
 COMPLEX = "complex" # Complex


class Pacing(Enum):
 """Pacing enum"""

 SLOW = "slow" # Slow pacing
 MEDIUM = "medium" # Medium Pacing
 FAST = "fast" # Fast pacing


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
 # timeline-related
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
