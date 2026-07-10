from __future__ import annotations

from typing import Any, Mapping, Optional

from app.schemas.style import (
    BackgroundDetailLevel,
    CharacterFaceStyle,
    CharacterProportion,
    ColorMood,
    ColorRenderStyle,
    CompositionStyle,
    EmotionActionLevel,
    LightingStyle,
    LineArtStyle,
    OutputTarget,
    ShotStoryboardStyle,
    StyleLockLevel,
    StyleOption,
    StylePreset,
    StyleSpec,
    StyleUniverse,
)

STYLE_DIMENSIONS: dict[str, type] = {
    "style_universe": StyleUniverse,
    "character_proportion": CharacterProportion,
    "character_face_style": CharacterFaceStyle,
    "line_art_style": LineArtStyle,
    "color_render_style": ColorRenderStyle,
    "lighting_style": LightingStyle,
    "color_mood": ColorMood,
    "shot_storyboard_style": ShotStoryboardStyle,
    "composition_style": CompositionStyle,
    "background_detail_level": BackgroundDetailLevel,
    "emotion_action_level": EmotionActionLevel,
    "style_lock_level": StyleLockLevel,
    "output_target": OutputTarget,
}


def humanize_style_value(value: str) -> str:
    return value.replace("_", " ").strip()


STYLE_OPTION_LABELS_ZH: dict[str, dict[str, str]] = {
    "style_universe": {
        "japanese_anime": "Ri Xi Dong Man",
        "chinese_comic": "Guo Man",
        "chinese_ink": "Shui Mo Guo Feng",
        "chinese_national_trend": "Guo Chao",
        "western_comic": "Ou Mei Man Hua",
        "western_cartoon": "Ou Mei Ka Tong",
        "dark_fantasy": "An Hei Qi Huan",
        "sci_fi": "Ke Huan",
        "cyberpunk": "Sai Bo Peng Ke",
        "steampunk": "Zheng Qi Peng Ke",
        "fantasy_magic": "Qi Huan Mo Fa",
        "experimental_art": "Shi Yan Yi Shu",
    },
    "character_proportion": {
        "chibi_2_head": "QBan(2Tou Shen)",
        "super_deformed_3_head": "ChaoQ(3Tou Shen)",
        "anime_5_head": "Dong Man(5Tou Shen)",
        "standard_6_head": "Biao Zhun(6Tou Shen)",
        "realistic_7_head": "Xie Shi(7Tou Shen)",
        "cinematic_realistic": "film Xie Shi",
    },
    "character_face_style": {
        "anime_big_eye": "Da Yan Dong Man",
        "anime_light_real": "Qing Xie Shi Dong Man",
        "chinese_realistic": "Guo Feng Xie Shi",
        "western_realistic": "Ou Mei Xie Shi",
        "cartoon_exaggerated": "Kua Zhang Ka Tong",
        "minimalist_flat": "Ji Jian Bian Ping",
        "cute_round": "Ke Ai Yuan Run",
    },
    "line_art_style": {
        "no_line_art": "Wu Xian Gao",
        "thin_clean_line": "Xi Xian Gan Jing",
        "bold_outline": "Cu Xian Gou Bian",
        "sketchy_line": "Cao Tu Xian",
        "broken_line": "Duan Xian",
        "ink_brush_line": "Mo Shua Xian",
    },
    "color_render_style": {
        "flat_color": "Ping Tu",
        "cell_shading": "Sai Lu Lu",
        "soft_shading": "Rou He on Se",
        "semi_painterly": "Ban Hou Tu",
        "full_painterly": "Hou Tu",
        "watercolor": "Shui Cai",
        "ink_wash": "Shui Mo Yun Ran",
    },
    "lighting_style": {
        "no_shadow": "none Yin Ying",
        "single_shadow": "Dan Ceng Yin Ying",
        "soft_light": "Rou Guang",
        "hard_light": "Ying Guang",
        "cinematic_light": "film Guang",
        "dramatic_contrast": "Xi Ju Dui Bi",
        "backlight_rim": "Ni Guang Lun Kuo Guang",
    },
    "color_mood": {
        "bright_vivid": "Ming Liang Xian Yan",
        "soft_pastel": "Rou He Fen Cai",
        "warm_tone": "Nuan Se Diao",
        "cool_tone": "Leng Se Diao",
        "low_saturation": "Di Bao He",
        "monochrome": "Hei Bai/Dan Se",
        "high_contrast": "Gao Dui Bi",
        "cinematic_lut": "filmLUT",
    },
    "shot_storyboard_style": {
        "anime_dynamic": "Dong Man Dong Tai",
        "cinematic_film": "film shot",
        "static_comic_panel": "Jing Tai Man Hua storyboard",
        "vertical_webtoon": "Shu Ping Tiao Man",
        "ppt_storyboard": "PPTstoryboard",
        "motion_comic": "Dong Tai Man Hua",
    },
    "composition_style": {
        "close_up": "close-up",
        "medium_shot": "medium shot",
        "wide_shot": "Quan Jing",
        "extreme_wide": "wide shot",
        "portrait_focus": "Ren Wu Xiao Xiang",
        "environment_focus": "environment Wei Zhu",
        "negative_space": "Liu Bai Gou Tu",
    },
    "background_detail_level": {
        "no_background": "none background",
        "simple_gradient": "Jian Dan Jian Bian",
        "stylized_background": "Feng Ge Hua background",
        "detailed_background": "Xi Jie background",
        "cinematic_environment": "film Ji environment",
    },
    "emotion_action_level": {
        "calm_static": "calm Jing Tai",
        "light_expression": "Qing Biao Qing",
        "clear_emotion": "Emotionclear",
        "dramatic_action": "Qiang action",
        "extreme_emotion": "Ji ZhiEmotion",
    },
    "style_lock_level": {
        "free": "Zi You",
        "scene_consistent": "scene Yi Zhi",
        "character_consistent": "character Yi Zhi",
        "episode_consistent": "Dan Ji Yi Zhi",
        "full_project_lock": "Quan Xiang Mu lock",
    },
    "output_target": {
        "short_video": "Duan video",
        "long_serial": "Zhang Lian Zai",
        "social_media": "She Jiao Mei Ti",
        "ip_design": "IPShe Ji",
        "commercial_ad": "Shang Ye Guang Gao",
        "concept_art": "Gai Nian setting",
    },
}


STYLE_PROMPT_LABELS: dict[str, str] = {
    "style_universe": "style universe",
    "character_proportion": "character proportion",
    "character_face_style": "face style",
    "line_art_style": "line art",
    "color_render_style": "color render",
    "lighting_style": "lighting",
    "color_mood": "color mood",
    "shot_storyboard_style": "shot/storyboard",
    "composition_style": "composition",
    "background_detail_level": "background detail",
    "emotion_action_level": "emotion/action",
    "style_lock_level": "style lock",
    "output_target": "output target",
}


def build_style_prompt(spec: StyleSpec) -> str:
    """Convert a resolved StyleSpec into a prompt suffix (stable, engineering-oriented)."""

    # Use JSON mode to get enum values (strings) instead of Enum reprs.
    data = spec.model_dump(mode="json", exclude_none=True)
    if not data:
        return ""

    # Prefer explicit labels to reduce ambiguity across providers.
    parts: list[str] = []
    for key, value in data.items():
        label = STYLE_PROMPT_LABELS.get(key, key)
        parts.append(f"{label}: {humanize_style_value(str(value))}")
    return "STYLE_SPEC => " + "; ".join(parts)


def derive_legacy_image_style(spec: StyleSpec) -> str:
    """Map StyleSpec to the platform legacy `style` string (realistic/anime/cartoon/portrait)."""

    if spec.composition_style == CompositionStyle.PORTRAIT_FOCUS:
        return "portrait"

    if spec.style_universe in {
        StyleUniverse.JAPANESE_ANIME,
        StyleUniverse.CHINESE_COMIC,
        StyleUniverse.WESTERN_COMIC,
        StyleUniverse.FANTASY_MAGIC,
        StyleUniverse.SCI_FI,
        StyleUniverse.CYBERPUNK,
        StyleUniverse.STEAMPUNK,
        StyleUniverse.DARK_FANTASY,
        StyleUniverse.CHINESE_NATIONAL_TREND,
    }:
        return "anime"

    if spec.style_universe in {StyleUniverse.WESTERN_CARTOON}:
        return "cartoon"

    if (
        spec.line_art_style == LineArtStyle.NO_LINE_ART
        and spec.character_face_style
        in {CharacterFaceStyle.CHINESE_REALISTIC, CharacterFaceStyle.WESTERN_REALISTIC}
    ):
        return "realistic"

    return "realistic"


def derive_openai_image_style(spec: StyleSpec, *, fallback: str = "realistic") -> str:
    """Map StyleSpec to OpenAI image `style` ('vivid'|'natural')."""

    if spec.color_mood in {ColorMood.LOW_SATURATION, ColorMood.MONOCHROME}:
        return "natural"
    if spec.color_mood in {
        ColorMood.BRIGHT_VIVID,
        ColorMood.HIGH_CONTRAST,
        ColorMood.CINEMATIC_LUT,
    }:
        return "vivid"
    return "natural" if fallback == "realistic" else "vivid"


DEFAULT_STYLE_SPEC = StyleSpec(
    style_universe=StyleUniverse.JAPANESE_ANIME,
    character_proportion=CharacterProportion.ANIME_5_HEAD,
    character_face_style=CharacterFaceStyle.ANIME_BIG_EYE,
    line_art_style=LineArtStyle.THIN_CLEAN_LINE,
    color_render_style=ColorRenderStyle.CELL_SHADING,
    lighting_style=LightingStyle.SOFT_LIGHT,
    color_mood=ColorMood.BRIGHT_VIVID,
    shot_storyboard_style=ShotStoryboardStyle.ANIME_DYNAMIC,
    composition_style=CompositionStyle.MEDIUM_SHOT,
    background_detail_level=BackgroundDetailLevel.STYLIZED_BACKGROUND,
    emotion_action_level=EmotionActionLevel.CLEAR_EMOTION,
    style_lock_level=StyleLockLevel.CHARACTER_CONSISTENT,
    output_target=OutputTarget.LONG_SERIAL,
)


STYLE_PRESETS: dict[str, StylePreset] = {
    "default_manga": StylePreset(
        preset_id="default_manga",
        label="default Man Hua",
        description="basic Man Hua Yu She(Tong Yong, Jun Heng).",
        spec=DEFAULT_STYLE_SPEC,
    ),
    "romance_anime_soft": StylePreset(
        preset_id="romance_anime_soft",
        label="Lian Ai Dong Man·Rou He",
        description="Lian Ai Xiang Ri Xi Dong Man(Fen Cai, Rou Guang, Wen Rou atmosphere).",
        spec=StyleSpec(
            style_universe=StyleUniverse.JAPANESE_ANIME,
            character_proportion=CharacterProportion.ANIME_5_HEAD,
            character_face_style=CharacterFaceStyle.ANIME_BIG_EYE,
            line_art_style=LineArtStyle.THIN_CLEAN_LINE,
            color_render_style=ColorRenderStyle.CELL_SHADING,
            lighting_style=LightingStyle.SOFT_LIGHT,
            color_mood=ColorMood.SOFT_PASTEL,
            shot_storyboard_style=ShotStoryboardStyle.ANIME_DYNAMIC,
            composition_style=CompositionStyle.PORTRAIT_FOCUS,
            background_detail_level=BackgroundDetailLevel.STYLIZED_BACKGROUND,
            emotion_action_level=EmotionActionLevel.CLEAR_EMOTION,
            style_lock_level=StyleLockLevel.CHARACTER_CONSISTENT,
            output_target=OutputTarget.LONG_SERIAL,
        ),
    ),
    "dark_fantasy_dramatic": StylePreset(
        preset_id="dark_fantasy_dramatic",
        label="An Hei Qi Huan·Xi Ju Guang Ying",
        description="An Hei Qi Huan(film Guang, Qiang Dui Bi, Xi Ju Zhang Li).",
        spec=StyleSpec(
            style_universe=StyleUniverse.DARK_FANTASY,
            character_proportion=CharacterProportion.STANDARD_6_HEAD,
            character_face_style=CharacterFaceStyle.ANIME_LIGHT_REAL,
            line_art_style=LineArtStyle.BOLD_OUTLINE,
            color_render_style=ColorRenderStyle.SEMI_PAINTERLY,
            lighting_style=LightingStyle.DRAMATIC_CONTRAST,
            color_mood=ColorMood.HIGH_CONTRAST,
            shot_storyboard_style=ShotStoryboardStyle.CINEMATIC_FILM,
            composition_style=CompositionStyle.WIDE_SHOT,
            background_detail_level=BackgroundDetailLevel.CINEMATIC_ENVIRONMENT,
            emotion_action_level=EmotionActionLevel.DRAMATIC_ACTION,
            style_lock_level=StyleLockLevel.EPISODE_CONSISTENT,
            output_target=OutputTarget.LONG_SERIAL,
        ),
    ),
    "chinese_ink_minimal": StylePreset(
        preset_id="chinese_ink_minimal",
        label="Guo Feng Shui Mo·Ji Jian",
        description="Shui Mo Yun Ran(Ji Jian Xian Tiao, Hei Bai/Dan SeEmotion).",
        spec=StyleSpec(
            style_universe=StyleUniverse.CHINESE_INK,
            character_proportion=CharacterProportion.STANDARD_6_HEAD,
            character_face_style=CharacterFaceStyle.MINIMALIST_FLAT,
            line_art_style=LineArtStyle.INK_BRUSH_LINE,
            color_render_style=ColorRenderStyle.INK_WASH,
            lighting_style=LightingStyle.SOFT_LIGHT,
            color_mood=ColorMood.MONOCHROME,
            shot_storyboard_style=ShotStoryboardStyle.STATIC_COMIC_PANEL,
            composition_style=CompositionStyle.NEGATIVE_SPACE,
            background_detail_level=BackgroundDetailLevel.STYLIZED_BACKGROUND,
            emotion_action_level=EmotionActionLevel.CALM_STATIC,
            style_lock_level=StyleLockLevel.SCENE_CONSISTENT,
            output_target=OutputTarget.CONCEPT_ART,
        ),
    ),
    "cyberpunk_neon": StylePreset(
        preset_id="cyberpunk_neon",
        label="Sai Bo Peng Ke·Ni Hong",
        description="Sai Bo Ni Hong(Ni Guang Lun Kuo Guang, filmLUT, environment atmosphere Qiang).",
        spec=StyleSpec(
            style_universe=StyleUniverse.CYBERPUNK,
            character_proportion=CharacterProportion.REALISTIC_7_HEAD,
            character_face_style=CharacterFaceStyle.WESTERN_REALISTIC,
            line_art_style=LineArtStyle.NO_LINE_ART,
            color_render_style=ColorRenderStyle.SEMI_PAINTERLY,
            lighting_style=LightingStyle.BACKLIGHT_RIM,
            color_mood=ColorMood.CINEMATIC_LUT,
            shot_storyboard_style=ShotStoryboardStyle.MOTION_COMIC,
            composition_style=CompositionStyle.ENVIRONMENT_FOCUS,
            background_detail_level=BackgroundDetailLevel.CINEMATIC_ENVIRONMENT,
            emotion_action_level=EmotionActionLevel.CLEAR_EMOTION,
            style_lock_level=StyleLockLevel.EPISODE_CONSISTENT,
            output_target=OutputTarget.SHORT_VIDEO,
        ),
    ),
    "western_cartoon_bright": StylePreset(
        preset_id="western_cartoon_bright",
        label="Ou Mei Ka Tong·Ming Liang",
        description="Ou Mei Ka Tong(Cu Xian Gou Bian, Ping Tu, Ming Liang Se Cai).",
        spec=StyleSpec(
            style_universe=StyleUniverse.WESTERN_CARTOON,
            character_proportion=CharacterProportion.STANDARD_6_HEAD,
            character_face_style=CharacterFaceStyle.CARTOON_EXAGGERATED,
            line_art_style=LineArtStyle.BOLD_OUTLINE,
            color_render_style=ColorRenderStyle.FLAT_COLOR,
            lighting_style=LightingStyle.SINGLE_SHADOW,
            color_mood=ColorMood.BRIGHT_VIVID,
            shot_storyboard_style=ShotStoryboardStyle.STATIC_COMIC_PANEL,
            composition_style=CompositionStyle.MEDIUM_SHOT,
            background_detail_level=BackgroundDetailLevel.SIMPLE_GRADIENT,
            emotion_action_level=EmotionActionLevel.DRAMATIC_ACTION,
            style_lock_level=StyleLockLevel.CHARACTER_CONSISTENT,
            output_target=OutputTarget.SOCIAL_MEDIA,
        ),
    ),
    "realistic_cinematic": StylePreset(
        preset_id="realistic_cinematic",
        label="Xie Shi·film Gan",
        description="film Xie Shi(Wu Xian Gao, Rou He on Se, film Deng Guang).",
        spec=StyleSpec(
            style_universe=StyleUniverse.EXPERIMENTAL_ART,
            character_proportion=CharacterProportion.CINEMATIC_REALISTIC,
            character_face_style=CharacterFaceStyle.WESTERN_REALISTIC,
            line_art_style=LineArtStyle.NO_LINE_ART,
            color_render_style=ColorRenderStyle.SOFT_SHADING,
            lighting_style=LightingStyle.CINEMATIC_LIGHT,
            color_mood=ColorMood.CINEMATIC_LUT,
            shot_storyboard_style=ShotStoryboardStyle.CINEMATIC_FILM,
            composition_style=CompositionStyle.MEDIUM_SHOT,
            background_detail_level=BackgroundDetailLevel.CINEMATIC_ENVIRONMENT,
            emotion_action_level=EmotionActionLevel.CLEAR_EMOTION,
            style_lock_level=StyleLockLevel.CHARACTER_CONSISTENT,
            output_target=OutputTarget.COMMERCIAL_AD,
        ),
    ),
    "portrait_realistic": StylePreset(
        preset_id="portrait_realistic",
        label="Xie Shi·Xiao Xiang",
        description="Xie Shi Xiao Xiang(Gan Jing background, Rou Guang, character Ju Jiao).",
        spec=StyleSpec(
            style_universe=StyleUniverse.EXPERIMENTAL_ART,
            character_proportion=CharacterProportion.CINEMATIC_REALISTIC,
            character_face_style=CharacterFaceStyle.WESTERN_REALISTIC,
            line_art_style=LineArtStyle.NO_LINE_ART,
            color_render_style=ColorRenderStyle.SOFT_SHADING,
            lighting_style=LightingStyle.SOFT_LIGHT,
            color_mood=ColorMood.WARM_TONE,
            shot_storyboard_style=ShotStoryboardStyle.CINEMATIC_FILM,
            composition_style=CompositionStyle.PORTRAIT_FOCUS,
            background_detail_level=BackgroundDetailLevel.SIMPLE_GRADIENT,
            emotion_action_level=EmotionActionLevel.LIGHT_EXPRESSION,
            style_lock_level=StyleLockLevel.CHARACTER_CONSISTENT,
            output_target=OutputTarget.IP_DESIGN,
        ),
    ),
}


def build_style_schema_options() -> dict[str, list[StyleOption]]:
    dimensions: dict[str, list[StyleOption]] = {}
    for key, enum_cls in STYLE_DIMENSIONS.items():
        options: list[StyleOption] = []
        zh_map = STYLE_OPTION_LABELS_ZH.get(key, {})
        for item in enum_cls:  # type: ignore[assignment]
            value = str(item.value)
            label = zh_map.get(value) or humanize_style_value(value)
            options.append(StyleOption(value=value, label=label))
        dimensions[key] = options
    return dimensions


def list_style_presets() -> list[StylePreset]:
    return list(STYLE_PRESETS.values())


def get_style_preset(preset_id: str) -> Optional[StylePreset]:
    return STYLE_PRESETS.get(preset_id)


LEGACY_STYLE_PRESET_MAP: dict[str, str] = {
    "anime": "default_manga",
    "cartoon": "western_cartoon_bright",
    "realistic": "realistic_cinematic",
    "portrait": "portrait_realistic",
}


def resolve_style_spec(
    *,
    style_spec: StyleSpec | Mapping[str, Any] | None = None,
    style_preset_id: str | None = None,
    legacy_style: str | None = None,
    fill_defaults: bool = True,
) -> tuple[StyleSpec, dict[str, Any]]:
    """Resolve a full StyleSpec from optional preset + partial overrides + legacy style.

    - Frontend may send partial `style_spec` depending on the feature area.
    - Backend remains the source of truth by filling missing fields from preset/defaults.
    - `legacy_style` is supported for backward compatibility.
    """

    meta: dict[str, Any] = {
        "preset_id": None,
        "legacy_style": None,
        "filled_defaults": fill_defaults,
    }

    preset_id = (style_preset_id or "").strip() or None
    if not preset_id and legacy_style:
        mapped = LEGACY_STYLE_PRESET_MAP.get(str(legacy_style).strip().lower())
        if mapped:
            preset_id = mapped
            meta["legacy_style"] = str(legacy_style).strip().lower()

    base = StyleSpec()
    if preset_id:
        preset = get_style_preset(preset_id)
        if preset:
            base = preset.spec
            meta["preset_id"] = preset_id
        else:
            meta["preset_id"] = preset_id
            meta["preset_missing"] = True

    overrides = StyleSpec()
    if isinstance(style_spec, StyleSpec):
        overrides = style_spec
    elif isinstance(style_spec, Mapping):
        overrides = StyleSpec.model_validate(dict(style_spec))

    if fill_defaults:
        resolved = DEFAULT_STYLE_SPEC.model_copy(deep=True)
        resolved = resolved.model_copy(update=base.model_dump(exclude_none=True))
    else:
        resolved = base.model_copy(deep=True)

    resolved = resolved.model_copy(update=overrides.model_dump(exclude_none=True))
    return resolved, meta


def summarize_style_spec(spec: StyleSpec) -> str:
    data = spec.model_dump(mode="json", exclude_none=True)
    if not data:
        return ""
    parts = [f"{k}={v}" for k, v in data.items()]
    return "; ".join(parts)
