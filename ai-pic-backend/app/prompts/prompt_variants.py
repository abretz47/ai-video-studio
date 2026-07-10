"""Type-safe prompt variant system."""

from enum import Enum
from typing import Optional


class StoryFormat(str, Enum):
    """Story format types for template selection."""

    DEFAULT = "default"
    SHORT_DRAMA = "short_drama"
    FILM = "film"
    TV_SERIES = "tv_series"


class ScriptFormat(str, Enum):
    """Script format types for template selection."""

    DEFAULT = "default"
    SHORT_DRAMA = "short_drama"
    FILM = "film"
    DOCUMENTARY = "documentary"


class ImageStyle(str, Enum):
    """Image generation style types."""

    REALISTIC = "realistic"
    ANIME = "anime"
    CARTOON = "cartoon"
    CINEMATIC = "cinematic"


class PromptVariants:
    """Type-safe prompt variant resolver."""

    _TEMPLATES = {
        "story_outline": {
            StoryFormat.DEFAULT: "story_outline",
            StoryFormat.SHORT_DRAMA: "story_outline_short_drama",
            StoryFormat.FILM: "story_outline_film",
            StoryFormat.TV_SERIES: "story_outline_tv_series",
        },
        "episode_generation": {
            StoryFormat.DEFAULT: "episode_generation",
            StoryFormat.SHORT_DRAMA: "episode_generation_short_drama",
            StoryFormat.FILM: "episode_generation_film",
            StoryFormat.TV_SERIES: "episode_generation_tv_series",
        },
        "episode_from_outline": {
            StoryFormat.DEFAULT: "episode_from_outline",
            StoryFormat.SHORT_DRAMA: "episode_from_outline_short_drama",
        },
        "episode_duration_reject": {
            StoryFormat.DEFAULT: "episode_duration_reject",
            StoryFormat.SHORT_DRAMA: "episode_duration_reject_short_drama",
        },
        "script_generation": {
            ScriptFormat.DEFAULT: "script_generation",
            ScriptFormat.SHORT_DRAMA: "script_generation_short_drama",
        },
    }

    @classmethod
    def story_outline(cls, format_type: StoryFormat = StoryFormat.DEFAULT) -> str:
        return cls._TEMPLATES["story_outline"].get(format_type, "story_outline")

    @classmethod
    def episode_generation(cls, format_type: StoryFormat = StoryFormat.DEFAULT) -> str:
        return cls._TEMPLATES["episode_generation"].get(
            format_type, "episode_generation"
        )

    @classmethod
    def episode_from_outline(cls, format_type: StoryFormat = StoryFormat.DEFAULT) -> str:
        return cls._TEMPLATES["episode_from_outline"].get(
            format_type, "episode_from_outline"
        )

    @classmethod
    def episode_duration_reject(
        cls, format_type: StoryFormat = StoryFormat.DEFAULT
    ) -> str:
        return cls._TEMPLATES["episode_duration_reject"].get(
            format_type, "episode_duration_reject"
        )

    @classmethod
    def script_generation(cls, format_type: ScriptFormat = ScriptFormat.DEFAULT) -> str:
        return cls._TEMPLATES["script_generation"].get(
            format_type, "script_generation"
        )

    @classmethod
    def resolve(cls, base_name: str, variant: Optional[str] = None) -> str:
        if variant and variant != "default":
            return f"{base_name}_{variant}"
        return base_name

    @classmethod
    def from_story_format_string(cls, format_str: str) -> StoryFormat:
        format_map = {
            "short_drama": StoryFormat.SHORT_DRAMA,
            "film": StoryFormat.FILM,
            "tv_series": StoryFormat.TV_SERIES,
            "default": StoryFormat.DEFAULT,
        }
        return format_map.get(format_str.lower(), StoryFormat.DEFAULT)


def get_template_for_format(
    base_template: str,
    story_format: Optional[str] = None,
    micro_genre: Optional[str] = None,
) -> str:
    """Get a template name based on story format."""
    format_type = StoryFormat.DEFAULT

    if story_format:
        format_type = PromptVariants.from_story_format_string(story_format)
    elif micro_genre:
        micro_lower = micro_genre.lower()
        if any(kw in micro_lower for kw in ["short drama", "short", "vertical"]):
            format_type = StoryFormat.SHORT_DRAMA
        elif any(kw in micro_lower for kw in ["film", "movie"]):
            format_type = StoryFormat.FILM
        elif any(kw in micro_lower for kw in ["tv", "episode", "series"]):
            format_type = StoryFormat.TV_SERIES

    if base_template == "story_outline":
        return PromptVariants.story_outline(format_type)
    if base_template == "episode_generation":
        return PromptVariants.episode_generation(format_type)
    if base_template == "episode_from_outline":
        return PromptVariants.episode_from_outline(format_type)
    if base_template == "episode_duration_reject":
        return PromptVariants.episode_duration_reject(format_type)
    return PromptVariants.resolve(base_template, format_type.value)
