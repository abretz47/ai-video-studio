from __future__ import annotations

from app.prompts.templates import (
    DialogueStyle,
    ImageCategory,
    ImageStyle,
    Pacing,
    PlotComplexity,
    PromptTemplate,
    ScriptFormat,
)

DEFAULT_GENERATION_PARAMS = {
    "story_outline": {
        "target_audience": "general audience",
        "duration_minutes": 90,
        "style_preferences": ["positive", "entertaining"],
        "content_restrictions": ["violence", "sexual content"],
    },
    "episode_generation": {
        "episode_duration": 30,
        "plot_complexity": PlotComplexity.MEDIUM.value,
        "pacing": Pacing.MEDIUM.value,
    },
    "script_generation": {
        "format_type": ScriptFormat.TELEPLAY.value,
        "language": "zh-CN",
        "dialogue_style": DialogueStyle.NATURAL.value,
        "scene_detail_level": "medium",
    },
    "image_generation": {
        "style": ImageStyle.REALISTIC.value,
        "category": ImageCategory.PORTRAIT.value,
        "resolution": "512x768",
        "quality": "high",
    },
}

QUALITY_ENHANCERS = {
    "image": {
        "general": ["high quality", "detailed", "masterpiece", "best quality"],
        "realistic": [
            "photorealistic",
            "8k",
            "ultra-detailed",
            "professional photography",
        ],
        "anime": ["anime masterpiece", "detailed anime", "high resolution anime"],
        "artistic": [
            "trending on artstation",
            "award-winning art",
            "professional illustration",
        ],
    },
    "text": {
        "creativity": ["creative", "original", "entertaining"],
        "quality": ["professional", "compelling", "engaging"],
        "structure": ["well-structured", "logically clear", "well-organized"],
    },
}

NEGATIVE_PROMPTS = {
    "image": {
        "common": ["low quality", "blurry", "distorted", "bad anatomy"],
        "faces": ["bad face", "ugly face", "asymmetrical eyes"],
        "hands": ["bad hands", "missing fingers", "extra fingers"],
        "general": ["worst quality", "low resolution", "jpeg artifacts"],
    },
    "text": {
        "content": ["violence", "sexual content", "politically sensitive"],
        "quality": ["low quality", "logically incoherent", "poorly expressed"],
    },
}

TEMPLATE_EXAMPLES = {
    PromptTemplate.VIRTUAL_IP_CREATION: {
        "name": "Xiao Ya",
        "description": "a lively and cute young girl",
        "age": "22 years old",
        "gender": "female",
        "personality_traits": ["lively", "curious", "optimistic"],
        "style_preference": "modern fashion",
        "target_audience": "young people",
    },
    PromptTemplate.VIRTUAL_IP_STYLE_PROMPT: {
        "name": "Xiao Ya",
        "description": "22-year-old lively girl, short hair, sweet smile",
        "biography": "cheerful and optimistic, loves photography and travel, casual everyday style",
        "image_category": "portrait",
    },
    PromptTemplate.STORY_OUTLINE: {
        "title": "The Power of Friendship",
        "genre": "drama",
        "theme": "friendship and growth",
        "characters": [
            {"name": "Xiao Ya", "description": "a lively college student"},
            {"name": "Li Ming", "description": "an introverted programmer"},
        ],
    },
    PromptTemplate.IMAGE_GENERATION: {
        "character_name": "Xiao Ya",
        "character_description": "22-year-old lively girl",
        "style": "realistic",
        "category": "portrait",
    },
}
