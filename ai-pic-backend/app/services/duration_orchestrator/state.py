"""
Duration Orchestrator status Ding Yi

Ding Yi LangGraph StateGraph Suo need status Shu Ju Jie Gou.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SceneStatus(str, Enum):
    """scene Sheng Cheng status"""

    PENDING = "pending"  # Dai Chu Li
    IN_PROGRESS = "in_progress"  # process in
    COMMITTED = "committed"  # submit(validation through)
    FAILED = "failed"  # failed(reach maximum retry Ci Shu)


@dataclass
class SceneBudget:
    """Dan Ge scene duration Yu Suan"""

    # basic Biao Shi
    scene_number: int
    scene_index: int  # in scene list in index (0-based)

    # when Zhang target
    target_duration_seconds: int
    target_word_count: int  # target dialogue word count

    # Rong Cha range
    min_duration_seconds: int  # Zui Xiao can Jie Shou when Zhang (target * 0.85)
    max_duration_seconds: int  # maximum can Jie Shou when Zhang (target * 1.15)

    # run when status
    status: SceneStatus = SceneStatus.PENDING
    attempt_count: int = 0

    # Shi Ji Jie Guo
    actual_duration_seconds: Optional[float] = None
    actual_word_count: Optional[int] = None
    actual_dialogue_count: Optional[int] = None

    # failed/retry Xin Xi
    last_rejection_reason: Optional[str] = None
    adjustment_hint: Optional[str] = None

    # Sheng Cheng Jie Guo Yin Yong
    script_scene_data: Optional[Dict[str, Any]] = None
    tts_results: Optional[List[Dict[str, Any]]] = None
    scene_beats: Optional[List[Dict[str, Any]]] = None

    def is_within_tolerance(self) -> bool:
        """check Shi Ji when Zhang Shi Fou in Rong Cha range interior"""
        if self.actual_duration_seconds is None:
            return False
        return (
            self.min_duration_seconds
            <= self.actual_duration_seconds
            <= self.max_duration_seconds
        )

    def duration_ratio(self) -> Optional[float]:
        """Ji Suan Shi Ji duration and target duration ratio"""
        if self.actual_duration_seconds is None or self.target_duration_seconds == 0:
            return None
        return self.actual_duration_seconds / self.target_duration_seconds

    def duration_diff_seconds(self) -> Optional[float]:
        """Ji Suan when Zhang Cha Yi (seconds), Zheng Shu Biao Shi Chao Shi, Fu Shu Biao Shi insufficient"""
        if self.actual_duration_seconds is None:
            return None
        return self.actual_duration_seconds - self.target_duration_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Zhuan Huan as Zi Dian"""
        return {
            "scene_number": self.scene_number,
            "scene_index": self.scene_index,
            "target_duration_seconds": self.target_duration_seconds,
            "target_word_count": self.target_word_count,
            "min_duration_seconds": self.min_duration_seconds,
            "max_duration_seconds": self.max_duration_seconds,
            "status": self.status.value,
            "attempt_count": self.attempt_count,
            "actual_duration_seconds": self.actual_duration_seconds,
            "actual_word_count": self.actual_word_count,
            "actual_dialogue_count": self.actual_dialogue_count,
            "last_rejection_reason": self.last_rejection_reason,
            "adjustment_hint": self.adjustment_hint,
            "is_within_tolerance": self.is_within_tolerance(),
            "duration_ratio": self.duration_ratio(),
        }


@dataclass
class OrchestratorState:
    """Duration Orchestrator Quan Ju status"""

    # ==========================================================================
    # input parameters
    # ==========================================================================
    episode_id: int
    script_id: int
    story_id: int
    total_duration_minutes: int

    # Episode Agent Chan Chu scene list (Yuan Shi Shu Ju)
    scenes_from_episode: List[Dict[str, Any]] = field(default_factory=list)

    # ==========================================================================
    # Yu Suan Fen Pei Jie Guo
    # ==========================================================================
    scene_budgets: List[SceneBudget] = field(default_factory=list)
    buffer_seconds: int = 0  # Yu Liu buffer

    # ==========================================================================
    # scene Sheng Cheng Jie Guo
    # ==========================================================================
    committed_scenes: List[Dict[str, Any]] = field(default_factory=list)

    # ==========================================================================
    # when Zhang Gen Zong
    # ==========================================================================
    committed_duration_seconds: float = 0.0
    remaining_budget_seconds: float = 0.0

    # ==========================================================================
    # Liu Cheng Kong Zhi
    # ==========================================================================
    current_scene_index: int = 0
    phase: str = (
        "init"  # init | allocating | generating | assembling | validating | done | failed
    )

    # ==========================================================================
    # Zui Zhong Jie Guo
    # ==========================================================================
    final_duration_seconds: Optional[float] = None
    final_duration_ratio: Optional[float] = None
    audio_timeline_url: Optional[str] = None
    storyboard_frames_count: int = 0

    # ==========================================================================
    # Tui Li log
    # ==========================================================================
    reasoning: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # ==========================================================================
    # Fu Zhu Fang Fa
    # ==========================================================================

    def get_current_budget(self) -> Optional[SceneBudget]:
        """get current Zheng Zai process scene Yu Suan"""
        if 0 <= self.current_scene_index < len(self.scene_budgets):
            return self.scene_budgets[self.current_scene_index]
        return None

    def get_pending_budgets(self) -> List[SceneBudget]:
        """get all Dai Chu Li scene Yu Suan"""
        return [b for b in self.scene_budgets if b.status == SceneStatus.PENDING]

    def get_committed_budgets(self) -> List[SceneBudget]:
        """get all submit scene Yu Suan"""
        return [b for b in self.scene_budgets if b.status == SceneStatus.COMMITTED]

    def get_failed_budgets(self) -> List[SceneBudget]:
        """get all failed scene Yu Suan"""
        return [b for b in self.scene_budgets if b.status == SceneStatus.FAILED]

    def all_scenes_processed(self) -> bool:
        """check Shi Fou all scene all process complete"""
        return all(
            b.status in (SceneStatus.COMMITTED, SceneStatus.FAILED)
            for b in self.scene_budgets
        )

    def total_target_duration(self) -> int:
        """Ji Suan all scene target when Zhang Zong He"""
        return sum(b.target_duration_seconds for b in self.scene_budgets)

    def total_actual_duration(self) -> float:
        """Ji Suan all submit scene Shi Ji when Zhang Zong He"""
        return sum(
            b.actual_duration_seconds or 0
            for b in self.scene_budgets
            if b.status == SceneStatus.COMMITTED
        )

    def total_retry_count(self) -> int:
        """Ji Suan Zong retry Ci Shu"""
        return sum(max(0, b.attempt_count - 1) for b in self.scene_budgets)

    def add_reasoning(self, msg: str) -> None:
        """Tian Jia Tui Li log"""
        self.reasoning.append(msg)

    def add_error(self, msg: str) -> None:
        """Tian Jia error log"""
        self.errors.append(msg)

    def to_dict(self) -> Dict[str, Any]:
        """Zhuan Huan as Zi Dian (Yong Yu Chi Jiu Hua and log)"""
        return {
            "episode_id": self.episode_id,
            "script_id": self.script_id,
            "story_id": self.story_id,
            "total_duration_minutes": self.total_duration_minutes,
            "scene_count": len(self.scene_budgets),
            "buffer_seconds": self.buffer_seconds,
            "phase": self.phase,
            "current_scene_index": self.current_scene_index,
            "committed_duration_seconds": self.committed_duration_seconds,
            "remaining_budget_seconds": self.remaining_budget_seconds,
            "scene_budgets": [b.to_dict() for b in self.scene_budgets],
            "committed_scenes_count": len(self.committed_scenes),
            "final_duration_seconds": self.final_duration_seconds,
            "final_duration_ratio": self.final_duration_ratio,
            "total_retry_count": self.total_retry_count(),
            "errors": self.errors,
        }

    def summary(self) -> Dict[str, Any]:
        """Sheng Cheng status summary"""
        committed = self.get_committed_budgets()
        failed = self.get_failed_budgets()
        pending = self.get_pending_budgets()

        return {
            "phase": self.phase,
            "total_scenes": len(self.scene_budgets),
            "committed": len(committed),
            "failed": len(failed),
            "pending": len(pending),
            "current_scene": self.current_scene_index + 1 if self.scene_budgets else 0,
            "committed_duration_seconds": round(self.committed_duration_seconds, 1),
            "target_duration_seconds": self.total_duration_minutes * 60,
            "progress_ratio": (
                round(len(committed) / len(self.scene_budgets), 2)
                if self.scene_budgets
                else 0
            ),
        }
