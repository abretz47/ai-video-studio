from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ScriptScoreDimensions(BaseModel):
    """Ping Fen Wei Du, Mei Xiang 0-5 Fen"""

    conflict_intensity: float = Field(
        ..., ge=0, le=5, description="conflict Qiang Du: conflict Shi Fou clear, Ji Lie, Chi Xu escalate"
    )
    character_recognizability: float = Field(
        ..., ge=0, le=5, description="character Bian Shi Du: character Shi Fou has Qing Xi tag, Dong Ji, Xing Wei Yi Zhi Xing"
    )
    cultural_fit: float = Field(
        ..., ge=0, le=5, description="Wen Hua Shi Pei: Shi Fou Fu He target market Shen Mei and Jin Ji"
    )
    clip_ability: float = Field(
        ..., ge=0, le=5, description="Su Cai can Jian Xing: Mei 60 seconds interior can Chai Chu Tou Liu Gou Zi Shu"
    )
    logic_coherence: float = Field(
        ..., ge=0, le=5, description="Luo Ji Yi Zhi Xing: Qing Jie Lian Guan, none Ming Xian Lou Dong"
    )


class ScriptScoreResult(BaseModel):
    """script Ping Fen Jie Guo"""

    overall_score: float = Field(..., ge=0, le=5, description="Zong Ti Ping Fen(Jia Quan Ping Jun)")
    dimension_scores: ScriptScoreDimensions = Field(..., description="Ge Wei Du Ping Fen")
    verdict: str = Field(..., description="Pan Ding Jie Guo: pass/review/rewrite")
    strengths: List[str] = Field(default_factory=list, description="script You Shi Dian")
    risks: List[str] = Field(default_factory=list, description="Feng Xian Dian/Wen Ti")
    rewrite_guidance: List[str] = Field(
        default_factory=list, description="Xiu Ding suggestion(Jin Dang verdict!= pass when)"
    )
    suggested_ad_hooks: List[str] = Field(
        default_factory=list, description="can Ti Lian Tou Liu Gou Zi suggestion"
    )


class TrafficSheetAsset(BaseModel):
    """Tou Liu Biao Dan Tiao Su Cai"""

    asset_id: str = Field(..., description="Su Cai Wei Yi Biao Shi")
    duration_seconds: int = Field(..., description="Su Cai when Zhang: 15/30/60")
    market_region: Optional[str] = Field(None, description="target market")
    micro_genre: Optional[str] = Field(None, description="Wei type")
    hook_type: str = Field(
        ...,
        description="Gou Zi type: betrayal/reveal/revenge/reunion/threat/taboo/power-shift",
    )
    source_episode: int = Field(..., description="Lai Yuan episode ID")
    source_timecode_start: Optional[str] = Field(None, description="Qi Shi Shi Jian Ma")
    source_timecode_end: Optional[str] = Field(None, description="Jie Shu Shi Jian Ma")
    key_line: str = Field(..., description="Zi Mu Mao Dian/core line")
    visual_hook: str = Field(..., description="first frame action/Shi Jue Gou Zi")
    shot_list: List[str] = Field(
        default_factory=list, description="key shot list(1-5 Ge)"
    )
    cliff_or_cta: str = Field(..., description="cliffhanger/CTA Wen An")
    music_reference: Optional[str] = Field(None, description="Yin Yue reference")
    compliance_flags: Optional[List[str]] = Field(None, description="He Gui Biao Ji")


class TrafficSheet(BaseModel):
    """Tou Liu Biao(Traffic Sheet)"""

    episode_id: Optional[int] = Field(None, description="Guan Lian episode ID")
    script_id: Optional[int] = Field(None, description="Guan Lian script ID")
    market_region: Optional[str] = Field(None, description="target market")
    micro_genre: Optional[str] = Field(None, description="Wei type")
    assets: List[TrafficSheetAsset] = Field(
        default_factory=list, description="Su Cai list"
    )
    generated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Sheng Cheng time"
    )
