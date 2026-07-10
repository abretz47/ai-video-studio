from typing import List, Literal, Optional

from app.schemas.generation import AdSnippet, HookPlan
from pydantic import BaseModel, Field


class StoryGenerationRequest(BaseModel):
    generation_mode: Literal["standard", "production"] = Field(
        "standard",
        description="Sheng Cheng Lian Lu: standard(sync/Tiao Shi)/production(async production Zhi Liang Men)",
    )
    # Ji Ben Xin Xi
    title: str = Field(..., max_length=255)
    story_format: Literal["short_drama", "tv_series", "film"] = Field(
        "short_drama",
        description="story Xing Tai: short_drama(short drama)/tv_series(TV series/web series)/film(film)",
    )
    default_aspect_ratio: Literal["9:16", "16:9"] = Field(
        "9:16", description="default Hua Fu: 9:16/16:9"
    )
    genre: str = Field(..., max_length=50)
    market_region: Optional[str] = Field(
        None, max_length=50, description="Target market/region"
    )
    micro_genre: Optional[str] = Field(
        None, max_length=80, description="Micro-genre/subgenre"
    )
    pacing_template: Optional[str] = Field(
        None,
        max_length=80,
        description="Jie Zou template(Qian Duan can Yong Yu automatic Tian Chong hook_plan Deng character Duan)",
    )
    hook_plan: Optional[HookPlan] = Field(
        None, description="Payoff/hook rhythm plan(can Xuan Yu She)"
    )
    twist_density: Optional[str] = Field(None, description="Twist density target(can Xuan Yu She)")
    cliffhanger_plan: Optional[List[str]] = Field(
        None, description="Suspense/cliffhanger plan(can Xuan Yu She)"
    )
    ad_snippets: Optional[List[AdSnippet]] = Field(
        None, description="Ad creative suggestions(can Xuan Yu She)"
    )
    theme: Optional[str] = Field(None, max_length=255)
    target_audience: Optional[str] = Field(None, max_length=100)
    duration_minutes: Optional[int] = Field(None, ge=1)

    # Character information
    character_ids: List[int] = Field(
        ..., min_items=1, description="Can Yu Xu NiIP IDlist"
    )

    # setting Xin Xi
    setting_time: Optional[str] = Field(None, max_length=100)
    setting_location: Optional[str] = Field(None, max_length=255)
    world_building: Optional[str] = None

    # Generation parameters
    additional_requirements: Optional[str] = None
    style_preferences: Optional[List[str]] = None
    content_restrictions: Optional[List[str]] = None

    # AIparameters
    model: Optional[str] = Field(
        None, description="Zhi Ding text Sheng Cheng model, for example openai:gpt-4o-mini"
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.5, description="Creative temperature")

    # Yuan data
    tags: Optional[List[str]] = None


class EpisodeGenerationRequest(BaseModel):
    generation_mode: Literal["standard", "production"] = Field(
        "standard",
        description="Sheng Cheng Lian Lu: standard(sync/Tiao Shi)/production(async production Zhi Liang Men)",
    )
    story_id: int
    episode_count: int = Field(..., ge=1, le=100, description="Yao Sheng Cheng episode Shu Liang")
    episode_duration: Optional[int] = Field(None, ge=1, description="Mei Ji when Zhang(minutes)")

    # market and Wei type
    market_region: Optional[str] = Field(
        None, max_length=50, description="Target market/region"
    )
    micro_genre: Optional[str] = Field(
        None, max_length=80, description="Micro-genre/subgenre"
    )
    pacing_template: Optional[str] = Field(
        None,
        max_length=80,
        description="Jie Zou template(Qian Duan can Yong Yu automatic Tian Chong hook_plan Deng character Duan)",
    )
    hook_plan: Optional[HookPlan] = Field(None, description="Payoff/hook rhythm plan")
    twist_density: Optional[str] = Field(None, description="Twist density target")
    cliffhanger_plan: Optional[List[str]] = Field(None, description="Suspense/cliffhanger plan")
    ad_snippets: Optional[List[AdSnippet]] = Field(None, description="Ad creative suggestions")

    # Generation parameters
    focus_characters: Optional[List[int]] = None
    plot_complexity: str = Field(
        "medium", description="Qing Jie Fu Za Du: simple, medium, complex"
    )
    pacing: str = Field("medium", description="Jie Zou: slow, medium, fast")

    # extra requirement
    additional_requirements: Optional[str] = None
    style_preferences: Optional[List[str]] = None

    # AIparameters
    model: Optional[str] = Field(
        None, description="Zhi Ding text Sheng Cheng model, for example openai:gpt-4o-mini"
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.5, description="Creative temperature")


class ScriptGenerationRequest(BaseModel):
    episode_id: int
    generation_mode: Literal["standard", "production"] = Field(
        "standard",
        description=(
            "Sheng Cheng Lian Lu: standard(Qing Liang/sync Tiao Shi)/production(Ping Fen Fan Xiu+timeline storyboard)"
        ),
    )
    auto_timeline_pipeline: Optional[bool] = Field(
        None,
        description=(
            "production mode below Shi Fou automatic Sheng Cheng dialogue Yin Gui, audio_timeline and storyboard Zhan Wei; "
            "Wei Zhi Ding when async production default as true"
        ),
    )
    format_type: str = Field("screenplay", description="script format")
    language: str = Field("zh-CN", description="Yu Yan")
    template_style: Literal["commercial_vertical_drama", "structured_json"] = Field(
        "commercial_vertical_drama",
        description="body text template: commercial_vertical_drama(Shang Yong Shu Ping short drama body text)/structured_json(Jiu Jie Gou Hua Cao Gao)",
    )
    target_chars_per_episode: int = Field(
        1300, ge=600, le=2500, description="Dan Ji target body text Zi Fu Shu"
    )
    quality_threshold: float = Field(
        9.0, ge=0.0, le=10.0, description="Shang Yong format Zhi Liang Men Yu Zhi(0-10)"
    )

    # market and Wei type
    market_region: Optional[str] = Field(
        None, max_length=50, description="Target market/region"
    )
    micro_genre: Optional[str] = Field(
        None, max_length=80, description="Micro-genre/subgenre"
    )
    pacing_template: Optional[str] = Field(
        None,
        max_length=80,
        description="Jie Zou template(Qian Duan can Yong Yu automatic Tian Chong hook_plan Deng character Duan)",
    )
    hook_plan: Optional[HookPlan] = Field(None, description="Payoff/hook rhythm plan")
    twist_density: Optional[str] = Field(None, description="Twist density target")
    cliffhanger_plan: Optional[List[str]] = Field(None, description="Suspense/cliffhanger plan")
    ad_snippets: Optional[List[AdSnippet]] = Field(None, description="Ad creative suggestions")

    # Generation parameters
    dialogue_style: str = Field(
        "natural", description="Dui Hua style: formal, natural, casual"
    )
    scene_detail_level: str = Field(
        "medium", description="scene description detailed Cheng Du: minimal, medium, detailed"
    )

    # extra requirement
    additional_requirements: Optional[str] = None
    style_preferences: Optional[List[str]] = None

    # AIparameters
    model: Optional[str] = Field(
        None, description="Zhi Ding text Sheng Cheng model, for example openai:gpt-4o-mini"
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.5, description="Creative temperature")


class StoryNovelExportRequest(BaseModel):
    """ Story Kuo Xie as Zhang text Xiao Shuo(default Zhi Hu Ti)."""

    style: Literal["zhihu"] = Field("zhihu", description="output style: zhihu(Zhi Hu Ti)")
    target_words: int = Field(
        20000, ge=10000, le=30000, description="target word count(1-3Wan Zi)"
    )
    chapter_count: Optional[int] = Field(
        None, ge=3, le=24, description="Zhang Jie Shu(can Xuan, default An target word count automatic Gu Suan)"
    )

    model: Optional[str] = Field(
        None, description="Zhi Ding text Sheng Cheng model, for example openai:gpt-4o-mini"
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.5, description="Creative temperature")
