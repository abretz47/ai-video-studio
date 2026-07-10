"""
scene submit node

validation through after submit scene, and Chu Fa subsequent scene Yu Suan then Ping Heng.
"""

from typing import Any, Dict

from app.core.logging import get_logger
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus
from app.services.duration_orchestrator.utils import rebalance_remaining_budgets

logger = get_logger()


def commit_scene_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 scene submit node.

 current scene Biao Ji as submit, and Chu Fa subsequent scene Yu Suan then Ping Heng.

 input status:
 - scene_budgets: scene Yu Suan list
 - current_scene_index: current scene index
 - generated_dialogues: Sheng Cheng dialogue

 output status update:
 - scene_budgets: update status and subsequent scene Yu Suan
 - committed_scenes: Tian Jia submit scene data
 - current_scene_index: Yi Dong to below a scene
 - reasoning: Tian Jia submit log
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        logger.warning("commit_scene_node: current index Yue Jie")
        return {}

    budget: SceneBudget = budgets[current_index]
    generated_dialogues = state.get("generated_dialogues", {})
    scene_dialogues = generated_dialogues.get(budget.scene_number, [])

    # Biao Ji as submit
    budget.status = SceneStatus.COMMITTED

    # Ji Suan when Zhang Pian Cha
    actual_seconds = budget.actual_duration_seconds or 0
    target_seconds = budget.target_duration_seconds
    deviation_seconds = actual_seconds - target_seconds

    logger.info(
        "commit_scene_node: scene %d submit",
        budget.scene_number,
        extra={
            "event": "scene_committed",
            "episode_id": state.get("episode_id"),
            "scene_number": budget.scene_number,
            "actual_duration_seconds": actual_seconds,
            "target_duration_seconds": target_seconds,
            "deviation_seconds": deviation_seconds,
            "deviation_ratio": round(deviation_seconds / target_seconds, 3)
            if target_seconds > 0
            else 0,
            "attempt_count": budget.attempt_count,
        },
    )

    # Chu Fa Yu Suan then Ping Heng(Ru Guo has Pian Cha Qie Hai You subsequent scene)
    if deviation_seconds != 0 and current_index < len(budgets) - 1:
        rebalance_remaining_budgets(
            budgets=budgets,
            current_index=current_index,
            actual_duration=actual_seconds,
        )
        logger.info(
            "commit_scene_node: Chu Fa Yu Suan then Ping Heng",
            extra={
                "event": "budget_rebalanced",
                "episode_id": state.get("episode_id"),
                "scene_number": budget.scene_number,
                "deviation_seconds": deviation_seconds,
                "remaining_scenes": len(budgets) - current_index - 1,
            },
        )

    # save submit scene data
    committed_scenes = state.get("committed_scenes", {})
    committed_scenes[budget.scene_number] = {
        "scene_number": budget.scene_number,
        "dialogues": scene_dialogues,
        "target_duration_seconds": target_seconds,
        "actual_duration_seconds": actual_seconds,
        "deviation_seconds": deviation_seconds,
        "attempt_count": budget.attempt_count,
    }

    # Yi Dong to below a scene
    next_index = current_index + 1

    reasoning = state.get("reasoning", [])
    reasoning.append(
        f"scene {budget.scene_number} Yi Ti Jiao: "
        f"{actual_seconds:.1f}s (Mu Biao {target_seconds}s, "
        f"Pian Cha {deviation_seconds:+.1f}s, "
        f"Chang Shi {budget.attempt_count} Ci)"
    )

    return {
        "scene_budgets": budgets,
        "committed_scenes": committed_scenes,
        "current_scene_index": next_index,
        "reasoning": reasoning,
    }


def should_continue_or_assemble(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Shi Fou continue process below a scene or Jin Ru assemble Jie Duan.

    Returns:
 "continue" - Hai You Dai Chu Li scene
 "assemble" - all scene process, Jin Ru assemble Jie Duan
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        return "assemble"

    # check Shi Fou Hai You Dai Chu Li scene
    remaining_pending = [
        b for b in budgets[current_index:] if b.status == SceneStatus.PENDING
    ]

    if remaining_pending:
        return "continue"

    return "assemble"
