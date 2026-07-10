"""
Duration Orchestrator Agent

Duan Dao Duan duration Bi Huan validation system, Que Bao Cong episode to timeline/dialogue to storyboard duration Jing Que Dui Qi.

core feature:
1. Yu Suan Fen Pei: Gen Ju total_duration_minutes Ji Suan Mei Ge scene duration Yu Suan and word count target
2. scene Ji Bi Huan: Mei Ge scene Sheng Cheng after Li Ji TTS Ce Liang, not Da Biao then retry Sheng Cheng
3. Yu Suan then Ping Heng: Mou scene Chao Shi/Qian Shi Shi Dong Tai adjust subsequent scene Yu Suan
4. Zui Zhong validation: Que Bao episode total duration in ±10% Rong Cha interior
"""

from app.services.duration_orchestrator.agent import (
    DurationOrchestratorAgent,
    orchestrate_episode_duration,
)
from app.services.duration_orchestrator.constants import (
    BUFFER_RATIO,
    DURATION_TOLERANCE_EPISODE,
    DURATION_TOLERANCE_SCENE,
    MAX_RETRY_ATTEMPTS,
    WORDS_PER_SECOND,
)
from app.services.duration_orchestrator.state import (
    OrchestratorState,
    SceneBudget,
    SceneStatus,
)

__all__ = [
    # Agent
    "DurationOrchestratorAgent",
    "orchestrate_episode_duration",
    # State
    "OrchestratorState",
    "SceneBudget",
    "SceneStatus",
    # Constants
    "DURATION_TOLERANCE_SCENE",
    "DURATION_TOLERANCE_EPISODE",
    "MAX_RETRY_ATTEMPTS",
    "WORDS_PER_SECOND",
    "BUFFER_RATIO",
]
