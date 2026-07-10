from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ContinuityTimelineItem(BaseModel):
    episode_number: int = Field(..., description="Ji Shu(Cong 1 Kai Shi)")
    time_anchor: Optional[str] = Field(
        None, description="time Mao Dian(Tong Yi Tian/Di Er Tian/Yi Zhou after/specific Ri Qi Deng)"
    )
    location_anchor: Optional[str] = Field(
        None, description="Di Dian Mao Dian(Cheng Shi/Qu Yu/key Zhu Yao Di Dian)"
    )
    events: List[str] = Field(default_factory=list, description="key Shi Jian(short sentence)")
    end_state: Optional[str] = Field(None, description="Ben Ji Jie Wei key status(short sentence)")
    reveals: List[str] = Field(
        default_factory=list, description="Ben Ji reveal Xin Xi(short sentence)"
    )


class ContinuityInfoAcquisitionEvent(BaseModel):
    episode_number: Optional[int] = Field(None, description="Ji Shu(if Shi Yong)")
    scene_number: Optional[int] = Field(None, description="scene Hao(if Shi Yong)")
    who: str = Field(..., description="Shui Huo De Xin Xi(character Ming/narration/Guan Zhong)")
    what: str = Field(..., description="Huo De Xin Xi(Xing Ming/Shen Fen/Shi Shi/Dong Ji Deng)")
    how: str = Field(
        ..., description="Huo De Fang Shi(Zi Bao/Ta Ren Jie Shao/Gong Pai/phone Bei Zhu/Mu Ji/Tui Duan Deng)"
    )
    evidence: Optional[str] = Field(None, description="evidence Pian Duan/Yin Yong(can Xuan)")


class RevealedInfoItem(BaseModel):
    """Xin Xi reveal Ji Lu, Yong Yu Xin Xi Men Kong Jiao Yan."""

    info_key: str = Field(..., description="Xin Xi Wei Yi Biao Shi(for example: character_identity_Zhang San)")
    info_content: str = Field(..., description="Xin Xi Nei Rong description")
    revealed_to: List[str] = Field(
        default_factory=list,
        description="Xin Xi reveal Gei Shui(character Ming list, 'Guan Zhong' Biao Shi Guan Zhong Yi Zhi Dan character unknown)",
    )
    revealed_at_episode: int = Field(..., description="reveal Ji Shu")
    revealed_at_scene: Optional[int] = Field(None, description="reveal scene Hao(can Xuan)")
    info_type: str = Field(
        "fact",
        description="Xin Xi type: identity/relationship/secret/event/location/motive",
    )
    is_public: bool = Field(
        False, description="Shi Fou as Gong Kai Xin Xi(all character+Guan Zhong all Zhi Dao)"
    )


class ContinuityCharacterState(BaseModel):
    status: Optional[str] = Field(None, description="current status/Chu Jing(short sentence)")
    goal: Optional[str] = Field(None, description="current target(short sentence)")
    relationships: Dict[str, str] = Field(
        default_factory=dict, description="and Ta Ren relationship"
    )
    known_info: List[str] = Field(
        default_factory=list, description="character Yi Zhi Xin Xi(short sentence)"
    )
    unknown_info: List[str] = Field(
        default_factory=list, description="character unknown Dan Zhong Yao Xin Xi(short sentence, Ke Wei Kong)"
    )


class ContinuityLedger(BaseModel):
    version: int = Field(1, description="Zhang Ben Ban Ben Hao")
    facts: List[str] = Field(default_factory=list, description="Que Ren Shi Shi(short sentence)")
    timeline: List[ContinuityTimelineItem] = Field(
        default_factory=list, description="time Xian"
    )
    characters: Dict[str, ContinuityCharacterState] = Field(
        default_factory=dict, description="character status/relationship/Zhi Shi"
    )
    info_acquisition_events: List[ContinuityInfoAcquisitionEvent] = Field(
        default_factory=list, description="Xin Xi Huo De Shi Jian(Yong Yu Zhi Shi Men Kong)"
    )
    revealed_info_timeline: List[RevealedInfoItem] = Field(
        default_factory=list,
        description="Xin Xi reveal time Xian(Yong Yu Xin Xi Men Kong Jiao Yan, Ji Lu Mei Tiao Xin Xi He Shi Xiang Shui reveal)",
    )
    open_threads: List[str] = Field(
        default_factory=list, description="not resolve clue/suspense(short sentence)"
    )
    resolved_threads: List[str] = Field(
        default_factory=list, description="Shou Shu clue/suspense(short sentence)"
    )


class EpisodeContinuitySnapshot(BaseModel):
    episode_number: int
    time_anchor: Optional[str] = None
    location_anchor: Optional[str] = None
    end_state: Optional[str] = None
    reveals: List[str] = Field(default_factory=list)
    info_acquisition_events: List[ContinuityInfoAcquisitionEvent] = Field(
        default_factory=list
    )


class EpisodeContinuityUpdatePayload(BaseModel):
    ledger: ContinuityLedger
    episode_snapshot: EpisodeContinuitySnapshot


class ContinuityAuditIssue(BaseModel):
    issue_type: str = Field(
        ...,
        description="Wen Ti type: causality/timeline/knowledge/relationship/location/plausibility Deng",
    )
    severity: str = Field(..., description="Yan Zhong Du: low/medium/high")
    description: str = Field(..., description="Wen Ti description(short sentence)")
    evidence: Optional[str] = Field(None, description="Chu Fa Wen Ti Pian Duan/Ding Wei(can Xuan)")
    fix_guidance: Optional[str] = Field(None, description="Xiu Fu Zhi Dao(can Xuan)")


class ContinuityAuditResult(BaseModel):
    verdict: str = Field(..., description="pass/fail")
    issues: List[ContinuityAuditIssue] = Field(default_factory=list)
    summary: Optional[str] = Field(None, description="Yi Ju Hua Zong Jie(can Xuan)")
