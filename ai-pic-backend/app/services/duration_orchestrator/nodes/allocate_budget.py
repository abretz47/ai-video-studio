"""
Yu Suan Fen Pei node

Gen Ju episode total duration and scene Shu Liang, Fen Pei Mei Ge scene duration Yu Suan and word count target.
"""

import logging
from typing import Any, Dict

from app.services.duration_orchestrator.utils import (
    allocate_scene_budgets,
    format_budget_summary,
)

logger = logging.getLogger(__name__)


def allocate_budget_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 Yu Suan Fen Pei node.

 Gen Ju total_duration_minutes and scenes_from_episode Ji Suan Mei Ge scene duration Yu Suan.

 input status:
 - total_duration_minutes: episode total duration(minutes)
 - scenes_from_episode: Episode Agent Chan Chu scene list

 output status update:
 - scene_budgets: scene Yu Suan list
 - buffer_seconds: Yu Liu buffer Miao Shu
 - remaining_budget_seconds: Sheng Yu can Fen Pei Miao Shu
 - phase: update as "generating"
 - reasoning: Tian Jia Fen Pei log
    """
    total_duration_minutes = state.get("total_duration_minutes", 0)
    scenes = state.get("scenes_from_episode", [])

    logger.info(
        "allocate_budget_node: Kai Shi Fen Pei Yu Suan",
        extra={
            "episode_id": state.get("episode_id"),
            "total_duration_minutes": total_duration_minutes,
            "scene_count": len(scenes),
        },
    )

    if not scenes:
        error_msg = "none scene can Fen Pei, Qing Xian Sheng Cheng episode scene"
        logger.error(error_msg)
        return {
            "phase": "failed",
            "errors": state.get("errors", []) + [error_msg],
        }

    # Fen Pei Yu Suan
    budgets, buffer_seconds = allocate_scene_budgets(
        total_duration_minutes=total_duration_minutes,
        scenes=scenes,
    )

    # Ji Suan Sheng Yu can Fen Pei Miao Shu
    total_allocated = sum(b.target_duration_seconds for b in budgets)
    remaining = total_duration_minutes * 60 - buffer_seconds - total_allocated

    # Sheng Cheng Fen Pei summary
    summary = format_budget_summary(budgets)
    logger.info(f"allocate_budget_node: 分配完成\n{summary}")

    reasoning = state.get("reasoning", [])
    reasoning.append(
        f"预算分配完成: {len(budgets)} 个场景，"
        f"总目标 {total_allocated}s，"
        f"buffer {buffer_seconds}s"
    )

    return {
        "scene_budgets": budgets,
        "buffer_seconds": buffer_seconds,
        "remaining_budget_seconds": remaining,
        "phase": "generating",
        "current_scene_index": 0,
        "reasoning": reasoning,
    }


def should_proceed_to_generation(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Shi Fou Ying Gai Jin Ru Sheng Cheng Jie Duan.

    Returns:
 "generate" - You Dai process scene, Jin Ru Sheng Cheng Jie Duan
 "assemble" - all scene process, Jin Ru assemble Jie Duan
 "failed" - Fa Sheng error
    """
    phase = state.get("phase", "")

    if phase == "failed":
        return "failed"

    budgets = state.get("scene_budgets", [])
    if not budgets:
        return "failed"

    # check Shi Fou You Dai process scene
    from app.services.duration_orchestrator.state import SceneStatus

    pending = [b for b in budgets if b.status == SceneStatus.PENDING]

    if pending:
        return "generate"
    else:
        return "assemble"
