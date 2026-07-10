from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.schemas.script_scoring import ScriptScoreDimensions as ScriptScoreDimensions
from app.schemas.script_scoring import ScriptScoreResult as ScriptScoreResult
from app.schemas.script_scoring import TrafficSheet as TrafficSheet
from app.schemas.script_scoring import TrafficSheetAsset as TrafficSheetAsset
from pydantic import BaseModel, Field


class CharacterInfo(BaseModel):
    name: str = Field(..., description="character name")
    description: Optional[str] = Field(None, description="character description or Ding Wei")
    role: Optional[str] = Field(None, description="character type/Zhi Ze")


class PlotStructure(BaseModel):
    act1: Optional[str] = None
    act2: Optional[str] = None
    act3: Optional[str] = None


class HookBeat(BaseModel):
    beat_type: Optional[str] = Field(
        None, description="Gou Zi type: hook/reversal/payoff Deng"
    )
    description: str = Field(..., description="Gou Zi/twist description")
    timing: Optional[str] = Field(None, description="Chu Xian Shi Ji: Kai Chang/Zhong Duan/Jie Wei Deng")
    intensity: Optional[str] = Field(None, description="Qiang Du: low/medium/high")


class HookPlan(BaseModel):
    opening_hook: Optional[str] = Field(None, description="Kai Chang Gou Zi She Ji")
    escalation_plan: Optional[str] = Field(None, description="EmotionJi Ya/escalate Jie Zou")
    payoff_plan: Optional[str] = Field(None, description="Shi Fang/Hui Shou node Gui Hua")
    key_reversals: Optional[List[HookBeat]] = Field(None, description="key twist list")


class AdSnippet(BaseModel):
    duration_seconds: Optional[int] = Field(None, description="Su Cai when Zhang(seconds)")
    hook: str = Field(..., description="Su Cai core Gou Zi")
    visual_summary: Optional[str] = Field(None, description="Su Cai frame summary")
    call_to_action: Optional[str] = Field(None, description="Yin Dao Wen An/CTA")


class StoryOutlineModel(BaseModel):
    premise: str = Field(..., description="story Qian Ti/core Gai Nian")
    synopsis: str = Field(..., description="detailed story outline")
    main_conflict: Optional[str] = Field(None, description="Main conflict")
    resolution: Optional[str] = Field(None, description="Jie Jue Fang An/Jie Ju")
    character_relationships: Optional[Dict[str, Any]] = Field(
        None, description="character Guan Xi Wang"
    )
    main_characters: Optional[List[CharacterInfo]] = Field(None, description="Main character")
    plot_structure: Optional[PlotStructure] = Field(None, description="San Mu Shi structure")
    core_values: Optional[str] = Field(None, description="core Jia Zhi")
    visual_style: Optional[str] = Field(None, description="Shi Jue style suggestion")
    selling_points: Optional[List[str]] = Field(None, description="Ying Xiao Mai Dian")
    market_region: Optional[str] = Field(None, description="Target market/region")
    micro_genre: Optional[str] = Field(None, description="Micro-genre/subgenre")
    hook_plan: Optional[HookPlan] = Field(None, description="Payoff/hook rhythm plan")
    twist_density: Optional[str] = Field(None, description="Twist density target")
    cliffhanger_plan: Optional[List[str]] = Field(None, description="Suspense/cliffhanger plan")
    ad_snippets: Optional[List[AdSnippet]] = Field(None, description="Ad creative suggestions")
    structured_story_contract: Optional[Dict[str, Any]] = Field(
        None, description="production Ji short drama story contract(only production Sheng Cheng requirement)"
    )


class SceneItem(BaseModel):
    scene_number: Optional[int] = None
    location: Optional[str] = None
    time: Optional[str] = None
    description: Optional[str] = None
    characters: Optional[List[str]] = None
    props: Optional[List[str]] = None
    notes: Optional[str] = None


class DialogueItem(BaseModel):
    scene_number: Optional[int] = None
    character: Optional[str] = None
    content: str
    emotion: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[str] = None


class StageDirectionItem(BaseModel):
    scene_number: Optional[int] = None
    timing: Optional[str] = None
    content: str
    type: Optional[str] = None


class ScriptMetadata(BaseModel):
    total_scenes: Optional[int] = None
    total_dialogues: Optional[int] = None
    estimated_duration: Optional[str] = None
    shooting_locations: Optional[List[str]] = None
    main_characters: Optional[List[str]] = None
    special_effects: Optional[List[str]] = None
    market_region: Optional[str] = Field(None, description="Target market/region")
    micro_genre: Optional[str] = Field(None, description="Micro-genre/subgenre")
    hook_plan: Optional[HookPlan] = Field(None, description="Payoff/hook rhythm plan")
    twist_density: Optional[str] = Field(None, description="Twist density target")
    cliffhanger_plan: Optional[List[str]] = Field(None, description="Suspense/cliffhanger plan")
    ad_snippets: Optional[List[AdSnippet]] = Field(None, description="Ad creative suggestions")


class ScriptModel(BaseModel):
    content: str
    scenes: Optional[List[SceneItem]] = None
    dialogues: Optional[List[DialogueItem]] = None
    stage_directions: Optional[List[StageDirectionItem]] = None
    metadata: Optional[ScriptMetadata] = None


class StoryboardFrame(BaseModel):
    # Accept any string id; default to a UUID string when absent.
    frame_id: str = Field(
        default_factory=lambda: str(uuid4()), description="storyboard Zhen Wei Yi Biao Shi(Zi Fu Chuan)"
    )
    frame_number: Optional[int] = None
    scene_number: Optional[int] = None
    scene_index: Optional[int] = Field(
        None, description="in script scene list in index(Cong1Kai Shi)"
    )
    shot_type: Optional[str] = Field(None, description="Jing Bie: wide shot/medium shot/Jin Jing/close-up Deng")
    camera_movement: Optional[str] = Field(
        None, description="Yun Jing: Tui/La/Yao/Yi/Gen/Bian Jiao Deng"
    )
    composition: Optional[str] = Field(None, description="Gou Tu: San Fen Fa/Dui Chen/Qian Hou Jing Deng")
    description: str = Field(..., description="frame description and action")
    duration_seconds: Optional[float] = Field(None, description="suggestion when Zhang(seconds)")
    start_ms: Optional[int] = Field(None, description="timeline Qi Dian(Hao Miao)")
    end_ms: Optional[int] = Field(None, description="timeline Zhong Dian(Hao Miao)")
    ai_prompt: Optional[str] = Field(None, description="Yong Yu Sheng Cheng image/video prompt Ci")
    hook_tag: Optional[str] = Field(None, description="Dui Ying Shuang Dian/Gou Zi tag(can Xuan)")
    ad_snippet: Optional[AdSnippet] = Field(None, description="Guan Lian Tou Liu Su Cai(can Xuan)")
    reference_images: Optional[List[str]] = Field(None, description="reference Tu URL list")
    image_url: Optional[str] = Field(
        None, description="Sheng Cheng storyboard imageURL(Sheng Cheng after Hui Tian)"
    )
    start_image_url: Optional[str] = Field(
        None, description="Fen Jing Shou Zhen Guan Jian ZhenURL(Sheng Cheng after Hui Tian)"
    )
    start_image_urls: Optional[List[str]] = Field(
        None, description="Fen Jing Shou Zhen Guan Jian ZhenURLlist(Sheng Cheng after Hui Tian)"
    )
    end_image_url: Optional[str] = Field(
        None, description="storyboard Wei Zhen Guan Jian ZhenURL(Sheng Cheng after Hui Tian)"
    )
    end_image_urls: Optional[List[str]] = Field(
        None, description="storyboard Wei Zhen Guan Jian ZhenURLlist(Sheng Cheng after Hui Tian)"
    )
    start_keyframe_prompt: Optional[str] = Field(
        None, description="Fen Jing Shou Zhen Guan Jian Zhen prompt Ci(Sheng Cheng when Tian Chong)"
    )
    end_keyframe_prompt: Optional[str] = Field(
        None, description="storyboard Wei Zhen Guan Jian Zhen prompt Ci(Sheng Cheng when Tian Chong)"
    )
    video_url: Optional[str] = Field(None, description="Sheng Cheng videoURL(Sheng Cheng after Hui Tian)")
    video_url_original: Optional[str] = Field(
        None, description="Sheng Cheng video originalURL(not Shang ChuanOSSwhen path)"
    )
    video_urls: Optional[List[str]] = Field(
        None, description="Sheng Cheng videoURLlist(Hui Tian Li Shi Ji Lu, Qu Zhong)"
    )
    video_thumbnail_url: Optional[str] = Field(
        None, description="video Feng Mian/Suo Lve TuURL(Sheng Cheng after Hui Tian)"
    )
    video_thumbnail_url_original: Optional[str] = Field(
        None, description="video Feng Mian originalURL(not Shang ChuanOSSwhen path)"
    )
    video_thumbnail_urls: Optional[List[str]] = Field(
        None, description="video Feng Mian/Suo Lve TuURLlist(Hui Tian Li Shi Ji Lu, Qu Zhong)"
    )
    video_last_frame_url: Optional[str] = Field(
        None, description="video Wei ZhenURL(return_last_frame=true when Hui Tian)"
    )
    video_last_frame_url_original: Optional[str] = Field(
        None, description="video Wei Zhen originalURL(not Shang ChuanOSSwhen path)"
    )
    video_last_frame_urls: Optional[List[str]] = Field(
        None, description="video Wei ZhenURLlist(Hui Tian Li Shi Ji Lu, Qu Zhong)"
    )
    video_generation: Optional[Dict[str, Any]] = Field(
        None, description="video Sheng Cheng Yuan data(model/parameters/Mao Dian Deng)"
    )
    generation_source: Optional[str] = Field(
        None, description="Sheng Cheng Lai Yuan: ai/manual/import/legacy"
    )
    generation_model: Optional[str] = Field(None, description="Sheng Cheng Suo Yong model Biao Shi")
    generation_method: Optional[str] = Field(
        None, description="Sheng Cheng Fang Shi: direct/plan/fallback Deng"
    )
    status: Optional[str] = Field(None, description="status: draft/confirmed/locked Deng")
    generated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Sheng Cheng time"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Zui Hou update time"
    )


class StoryboardModel(BaseModel):
    frames: List[StoryboardFrame]


class PlotPoint(BaseModel):
    description: str
    timing: Optional[str] = Field(None, description="Chu Xian Shi Duan: Kai Chang/Zhong Duan/Jie Wei Deng")
    purpose: Optional[str] = Field(None, description="Gai Qing Jie Dian Xu Shi Mu Di")
    escalation: Optional[str] = Field(None, description="conflict/Zhang Li Ru He escalate")


class ConflictItem(BaseModel):
    description: str
    intensity: Optional[str] = Field(None, description="Qiang Du: low/medium/high")
    parties: Optional[List[str]] = Field(None, description="conflict Shuang Fang/Duo Fang")


class EpisodeBeat(BaseModel):
    sequence_number: int = Field(..., ge=1, description="Shun Xu ID, Cong1Kai Shi")
    beat_title: str = Field(..., description="Qing Jie Dian title")
    beat_summary: str = Field(..., description="Qing Jie Dian summary")
    act_label: Optional[str] = Field(None, description="Suo Zai Mu: ACT I/II/III Deng")
    dramatic_question: Optional[str] = Field(None, description="suspense/Xi Ju Wen Ti")
    characters_involved: Optional[List[str]] = Field(
        None, description="Can Yu character name list"
    )
    location_hint: Optional[str] = Field(None, description="scene/Di Dian prompt")
    duration_estimate_minutes: Optional[float] = Field(
        None, ge=0, description="Yu Gu when Zhang(minutes)"
    )


class EpisodeStepOutlineItem(BaseModel):
    episode_number: int
    title: Optional[str] = None
    logline: Optional[str] = None
    beats: Optional[List[EpisodeBeat]] = None
    structured_episode_contract: Optional[Dict[str, Any]] = Field(
        None, description="production Ji episode contract summary(only production Sheng Cheng requirement)"
    )


class EpisodeStepOutlineModel(BaseModel):
    episodes: List[EpisodeStepOutlineItem]


class EpisodePlanItem(BaseModel):
    episode_number: int
    title: str
    summary: str
    market_region: Optional[str] = Field(None, description="Target market/region")
    micro_genre: Optional[str] = Field(None, description="Micro-genre/subgenre")
    hook_plan: Optional[HookPlan] = Field(None, description="Payoff/hook rhythm plan")
    twist_density: Optional[str] = Field(None, description="Twist density target")
    cliffhanger_plan: Optional[List[str]] = Field(None, description="Suspense/cliffhanger plan")
    ad_snippets: Optional[List[AdSnippet]] = Field(None, description="Ad creative suggestions")
    plot_points: Optional[List[PlotPoint]] = None
    character_arcs: Optional[Dict[str, Any]] = None
    conflicts: Optional[List[ConflictItem]] = None
    scene_count: Optional[int] = None
    scenes: Optional[List[Dict[str, Any]]] = None
    payoff: Optional[str] = Field(None, description="Ben Ji specific Shuang Dian/Shou Huo Dian")
    cliffhanger: Optional[str] = Field(None, description="Ben Ji Jie Wei Ka Dian")
    structured_episode_contract: Optional[Dict[str, Any]] = Field(
        None, description="production Ji Dan Ji He Tong(only production Sheng Cheng requirement)"
    )


class EpisodePlanModel(BaseModel):
    episodes: List[EpisodePlanItem]


class StoryboardPlanFrameOutline(BaseModel):
    shot_type: Optional[str] = Field(None, description="Jing Bie: wide shot/medium shot/Jin Jing/close-up")
    camera_movement: Optional[str] = Field(
        None, description="Yun Jing: Gu Ding/Tui/La/Yao/Yi/Gen/Bian Jiao"
    )
    composition: Optional[str] = Field(None, description="Gou Tu: San Fen Fa/Dui Chen/Qian Hou Jing")
    intent: Optional[str] = Field(None, description="frame Yi Tu/Xu Shi Zuo Yong(Jian Duan)")


class StoryboardPlanScene(BaseModel):
    scene_number: int
    target_frames: int = Field(..., ge=1, le=20)
    frames: List[StoryboardPlanFrameOutline]
    environment_id: Optional[int] = None
    character_ids: Optional[List[int]] = None


class StoryboardPlanModel(BaseModel):
    scenes: List[StoryboardPlanScene]
