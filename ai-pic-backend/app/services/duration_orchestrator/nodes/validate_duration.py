"""
when Zhang validation node

validation scene Shi Ji TTS when Zhang Shi Fou in target range interior.
"""

import logging
from typing import Any, Dict

from app.services.duration_orchestrator.constants import MAX_RETRY_ATTEMPTS
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus
from app.services.duration_orchestrator.utils import compute_adjustment_hint

logger = logging.getLogger(__name__)


def validate_duration_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 when Zhang validation node.

 validation current scene Shi Ji TTS when Zhang Shi Fou in target range interior.

 input status:
 - scene_budgets: scene Yu Suan list
 - current_scene_index: current scene index

 output status update:
 - scene_budgets: update validation Jie Guo
 - reasoning: Tian Jia validation log
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        logger.warning("validate_duration_node: current index Yue Jie")
        return {}

    budget: SceneBudget = budgets[current_index]

    # check Shi Fou has Shi Ji when Zhang data
    if budget.actual_duration_seconds is None:
        logger.warning(
            f"validate_duration_node: 场景 {budget.scene_number} 无实际时长数据"
        )
        return {}

    # validation when Zhang
    is_valid = budget.is_within_tolerance()
    ratio = budget.duration_ratio()

    logger.info(
        f"validate_duration_node: 场景 {budget.scene_number} 验证结果",
        extra={
            "scene_number": budget.scene_number,
            "target_duration": budget.target_duration_seconds,
            "actual_duration": budget.actual_duration_seconds,
            "ratio": ratio,
            "is_valid": is_valid,
            "attempt_count": budget.attempt_count,
        },
    )

    reasoning = state.get("reasoning", [])

    if is_valid:
        # validation through
        budget.status = SceneStatus.COMMITTED
        budget.last_rejection_reason = None
        budget.adjustment_hint = None

        reasoning.append(
            f"场景 {budget.scene_number} 验证通过: "
            f"{budget.actual_duration_seconds:.1f}s / "
            f"{budget.target_duration_seconds}s ({ratio:.0%})"
        )
    else:
        # validation failed
        if budget.attempt_count >= MAX_RETRY_ATTEMPTS:
            # reach maximum retry Ci Shu, Qiang Zhi Jie Shou
            budget.status = SceneStatus.COMMITTED
            reasoning.append(
                f"场景 {budget.scene_number} 达到最大重试次数 ({MAX_RETRY_ATTEMPTS})，"
                f"强制接受: {budget.actual_duration_seconds:.1f}s / "
                f"{budget.target_duration_seconds}s ({ratio:.0%})"
            )
            logger.warning(f"场景 {budget.scene_number} 达到最大重试次数，强制接受")
        else:
            # Sheng Cheng adjust suggestion
            actual_ms = int(budget.actual_duration_seconds * 1000)
            actual_words = budget.actual_word_count or 0

            reason, hint = compute_adjustment_hint(
                actual_word_count=actual_words,
                actual_duration_ms=actual_ms,
                target_duration_seconds=budget.target_duration_seconds,
            )

            budget.status = SceneStatus.PENDING
            budget.last_rejection_reason = reason
            budget.adjustment_hint = hint

            reasoning.append(
                f"场景 {budget.scene_number} 验证失败 ({reason}): "
                f"{budget.actual_duration_seconds:.1f}s / "
                f"{budget.target_duration_seconds}s ({ratio:.0%})，"
                f"将进行第 {budget.attempt_count + 1} 次重试"
            )

    return {
        "scene_budgets": budgets,
        "reasoning": reasoning,
    }


def should_commit_or_retry(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Shi Fou Ying Gai submit or retry current scene.

    Returns:
 "commit" - validation through, submit scene
 "retry" - validation failed, need retry
 "next" - Jin Ru below a scene
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        return "next"

    budget: SceneBudget = budgets[current_index]

    if budget.status == SceneStatus.COMMITTED:
        return "commit"
    elif budget.status == SceneStatus.PENDING and budget.last_rejection_reason:
        return "retry"
    else:
        return "next"


def check_all_scenes_done(state: Dict[str, Any]) -> str:
    """
 Lu You function: check Shi Fou all scene all process complete.

    Returns:
 "done" - all scene process, Jin Ru assemble Jie Duan
 "continue" - Hai You Dai Chu Li scene
    """
    budgets = state.get("scene_budgets", [])

    if not budgets:
        return "done"

    all_done = all(
        b.status in (SceneStatus.COMMITTED, SceneStatus.FAILED) for b in budgets
    )

    return "done" if all_done else "continue"
