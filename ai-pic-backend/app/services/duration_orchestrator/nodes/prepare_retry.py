"""
retry Zhun Bei node

Dang scene when Zhang validation failed when, Sheng Cheng adjust suggestion Gong Xia Ci Sheng Cheng Shi Yong.
"""

import logging
from typing import Any, Dict

from app.services.duration_orchestrator.constants import MAX_RETRY_ATTEMPTS
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus
from app.services.duration_orchestrator.utils import compute_adjustment_hint

logger = logging.getLogger(__name__)


def prepare_retry_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 retry Zhun Bei node.

 Dang scene when Zhang validation failed when: 
 1. Sheng Cheng adjust suggestion(increase/Shan Jian Duo Shao character)
 2. update scene status as pending retry
 3. Qing Kong Sheng Cheng dialogue

 input status:
 - scene_budgets: scene Yu Suan list
 - current_scene_index: current scene index
 - generated_dialogues: Sheng Cheng dialogue

 output status update:
 - scene_budgets: update adjust suggestion
 - generated_dialogues: Qing Kong current scene dialogue
 - reasoning: Tian Jia retry Zhun Bei log
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        logger.warning("prepare_retry_node: current index Yue Jie")
        return {}

    budget: SceneBudget = budgets[current_index]

    # check Shi Fou reach maximum retry Ci Shu
    if budget.attempt_count >= MAX_RETRY_ATTEMPTS:
        logger.warning(
            "prepare_retry_node: scene %d reach maximum retry Ci Shu %d, Qiang Zhi submit",
            budget.scene_number,
            MAX_RETRY_ATTEMPTS,
        )
        budget.status = SceneStatus.COMMITTED
        budget.last_rejection_reason = "max_retries_exceeded"
        budget.adjustment_hint = None

        reasoning = state.get("reasoning", [])
        reasoning.append(
            f"scene {budget.scene_number} Da Dao Zui Da Zhong Shi Ci Shu ({MAX_RETRY_ATTEMPTS})，Qiang Zhi Ti Jiao"
        )

        return {
            "scene_budgets": budgets,
            "reasoning": reasoning,
        }

    # Ji Suan adjust suggestion
    actual_duration_ms = int((budget.actual_duration_seconds or 0) * 1000)
    actual_word_count = budget.actual_word_count or 0

    reason, hint = compute_adjustment_hint(
        actual_word_count=actual_word_count,
        actual_duration_ms=actual_duration_ms,
        target_duration_seconds=budget.target_duration_seconds,
    )

    # update Yu Suan status
    budget.status = SceneStatus.PENDING
    budget.last_rejection_reason = reason
    budget.adjustment_hint = hint

    logger.info(
        "prepare_retry_node: scene %d Zhun Bei Di %d Ci retry",
        budget.scene_number,
        budget.attempt_count + 1,
        extra={
            "scene_number": budget.scene_number,
            "attempt_count": budget.attempt_count,
            "reason": reason,
            "actual_duration_seconds": budget.actual_duration_seconds,
            "target_duration_seconds": budget.target_duration_seconds,
        },
    )

    # Qing Kong current scene Sheng Cheng dialogue
    generated_dialogues = state.get("generated_dialogues", {})
    if budget.scene_number in generated_dialogues:
        del generated_dialogues[budget.scene_number]

    reasoning = state.get("reasoning", [])
    reasoning.append(
        f"scene {budget.scene_number} Zhun Bei Zhong Shi (Di {budget.attempt_count + 1} Ci): {reason}"
    )

    return {
        "scene_budgets": budgets,
        "generated_dialogues": generated_dialogues,
        "reasoning": reasoning,
    }


def should_retry_or_fail(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Shi Fou Ying Gai retry or Biao Ji failed.

    Returns:
 "retry" - Canretry
 "commit" - reach maximum retry Ci Shu, Qiang Zhi submit
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        return "commit"

    budget: SceneBudget = budgets[current_index]

    if budget.status == SceneStatus.COMMITTED:
        return "commit"

    if budget.attempt_count >= MAX_RETRY_ATTEMPTS:
        return "commit"

    return "retry"
