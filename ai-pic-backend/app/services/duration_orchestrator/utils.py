"""
Duration Orchestrator Gong Ju function

Ti Gong Yu Suan Fen Pei, word count Ji Suan, adjust suggestion Sheng Cheng Deng Gong Ju function.
"""

import logging
from typing import Any, Dict, List, Tuple

from app.services.duration_orchestrator.constants import (
    ADJUSTMENT_WORDS_PER_DIALOGUE,
    BUFFER_RATIO,
    DEFAULT_SCENE_DURATION_SECONDS,
    DIALOGUE_DENSITY_FACTOR,
    DURATION_TOLERANCE_SCENE_HIGH,
    DURATION_TOLERANCE_SCENE_LOW,
    MAX_SCENE_DURATION_SECONDS,
    MIN_SCENE_DURATION_SECONDS,
    MIN_WORD_ADJUSTMENT,
    MIN_WORD_REDUCTION,
    WORDS_PER_SECOND,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus

logger = logging.getLogger(__name__)


def calculate_target_word_count(duration_seconds: int) -> int:
    """
 Gen Ju target when Zhang Ji Suan target dialogue word count.

 consider Yin Su:
 - DIALOGUE_DENSITY_FACTOR (0.90): Bu Shi all time all in Shuo Hua, need consider
 Ting Dun, Yu Qi Ci, EmotionBiao Da, character Fan Ying Shi Jian, environment Yin Deng
 - WORDS_PER_SECOND (4.7): Jiao Zhun after Zhong Wen TTS Yu Su

 for example: 60seconds scene
 - Shi Ji dialogue time: 60 * 0.90 = 54seconds
 - target word count: 54 * 4.7 ≈ 254character

    Args:
 duration_seconds: target when Zhang (seconds)

    Returns:
 target dialogue word count
    """
    effective_seconds = duration_seconds * DIALOGUE_DENSITY_FACTOR
    return int(effective_seconds * WORDS_PER_SECOND)


def allocate_scene_budgets(
    total_duration_minutes: int,
    scenes: List[Dict[str, Any]],
    buffer_ratio: float = BUFFER_RATIO,
) -> Tuple[List[SceneBudget], int]:
    """
 Fen Pei Mei Ge scene duration Yu Suan.

 Ce Lve:
 1. Bao Liu buffer_ratio (default 5%) Yong Yu scene Jian Guo Du
 2. Ru Guo scene has estimated_duration_seconds, An ratio Suo Fang
 3. Fou Ze Ping Jun Fen Pei

    Args:
 total_duration_minutes: total duration (minutes)
 scenes: scene list (Lai Zi Episode Agent)
 buffer_ratio: Yu Liu buffer ratio

    Returns:
 (scene Yu Suan list, buffer Miao Shu)
    """
    if not scenes:
        logger.warning("allocate_scene_budgets: none scene can Fen Pei")
        return [], 0

    total_seconds = total_duration_minutes * 60
    buffer_seconds = int(total_seconds * buffer_ratio)
    available_seconds = total_seconds - buffer_seconds

    # check Shi Fou has Gu Suan when Zhang
    has_estimates = any(s.get("estimated_duration_seconds") for s in scenes)

    budgets: List[SceneBudget] = []

    if has_estimates:
        # An Gu Suan when Zhang ratio Fen Pei
        total_estimated = sum(
            s.get("estimated_duration_seconds", DEFAULT_SCENE_DURATION_SECONDS)
            for s in scenes
        )

        for idx, scene in enumerate(scenes):
            estimated = scene.get(
                "estimated_duration_seconds", DEFAULT_SCENE_DURATION_SECONDS
            )
            ratio = (
                estimated / total_estimated if total_estimated > 0 else 1 / len(scenes)
            )
            target = int(available_seconds * ratio)

            # Que Bao in He Li range interior
            target = max(
                MIN_SCENE_DURATION_SECONDS, min(target, MAX_SCENE_DURATION_SECONDS)
            )

            budgets.append(
                SceneBudget(
                    scene_number=scene.get("scene_number", idx + 1),
                    scene_index=idx,
                    target_duration_seconds=target,
                    target_word_count=calculate_target_word_count(target),
                    min_duration_seconds=int(target * DURATION_TOLERANCE_SCENE_LOW),
                    max_duration_seconds=int(target * DURATION_TOLERANCE_SCENE_HIGH),
                )
            )
    else:
        # Ping Jun Fen Pei
        per_scene = available_seconds // len(scenes)
        per_scene = max(
            MIN_SCENE_DURATION_SECONDS, min(per_scene, MAX_SCENE_DURATION_SECONDS)
        )

        for idx, scene in enumerate(scenes):
            budgets.append(
                SceneBudget(
                    scene_number=scene.get("scene_number", idx + 1),
                    scene_index=idx,
                    target_duration_seconds=per_scene,
                    target_word_count=calculate_target_word_count(per_scene),
                    min_duration_seconds=int(per_scene * DURATION_TOLERANCE_SCENE_LOW),
                    max_duration_seconds=int(per_scene * DURATION_TOLERANCE_SCENE_HIGH),
                )
            )

    logger.info(
        "allocate_scene_budgets: Fen Pei complete",
        extra={
            "total_duration_minutes": total_duration_minutes,
            "scene_count": len(scenes),
            "buffer_seconds": buffer_seconds,
            "available_seconds": available_seconds,
            "has_estimates": has_estimates,
        },
    )

    return budgets, buffer_seconds


def compute_adjustment_hint(
    actual_word_count: int,
    actual_duration_ms: int,
    target_duration_seconds: int,
) -> Tuple[str, str]:
    """
 Ji Suan adjust suggestion.

 Gen Ju Shi Ji duration and target duration Cha Yi, Sheng Cheng specific adjust suggestion.

    Args:
 actual_word_count: Shi Ji dialogue word count
 actual_duration_ms: Shi Ji TTS when Zhang (Hao Miao)
 target_duration_seconds: target when Zhang (seconds)

    Returns:
        (rejection_reason, adjustment_hint)
    """
    target_ms = target_duration_seconds * 1000
    diff_ms = target_ms - actual_duration_ms
    diff_seconds = abs(diff_ms) / 1000

    # Gu Suan need Zeng Jian word count(An current Ji Zhun Yu Su)
    words_per_second = WORDS_PER_SECOND
    word_diff = max(int(abs(diff_seconds) * words_per_second), MIN_WORD_ADJUSTMENT)

    # Gu Suan need Zeng Jian dialogue Ju Shu
    dialogue_diff = max(1, word_diff // ADJUSTMENT_WORDS_PER_DIALOGUE)

    if diff_ms > 0:
        # when Zhang insufficient
        reason = "duration_too_short"
        hint = (
            f"Dang Qian dialogue Shi Zhang {actual_duration_ms / 1000:.1f} Miao，"
            f"Mu Biao {target_duration_seconds} Miao，"
            f"Cha Ju {diff_seconds:.1f} Miao。\n"
            f"Jian Yi Zeng Jia Yue {word_diff} Zi De dialogue（Yue {dialogue_diff} Ju）。\n"
            f"Ke Yi：\n"
            f"1. Kuo Zhan Xian You dialogue De Qing Gan Miao Xie He Fan Ying\n"
            f"2. Zeng Jia character Jian De Hu Dong He Zhui Wen\n"
            f"3. Tian Jia Nei Xin Du Bai Huo Pang Bai\n"
            f"4. Feng Fu scene Xi Jie Miao Shu"
        )
    else:
        # when Zhang Guo Chang
        word_diff = max(word_diff, MIN_WORD_REDUCTION)
        dialogue_diff = max(1, word_diff // ADJUSTMENT_WORDS_PER_DIALOGUE)
        reason = "duration_too_long"
        hint = (
            f"Dang Qian dialogue Shi Zhang {actual_duration_ms / 1000:.1f} Miao，"
            f"Mu Biao {target_duration_seconds} Miao，"
            f"Chao Chu {diff_seconds:.1f} Miao。\n"
            f"Jian Yi Shan Jian Yue {word_diff} Zi De dialogue（Yue {dialogue_diff} Ju）。\n"
            f"Ke Yi：\n"
            f"1. Jing Jian Rong Yu dialogue，Bao Liu He Xin Xin Xi\n"
            f"2. He Bing Xiang Shi Nei Rong De Dui Hua\n"
            f"3. Shan Chu Dui Qing Jie Tui Jin Gong Xian Bu Da De Tai Ci\n"
            f"4. Jian Hua Guo Zhang De Miao Shu Xing Yu Ju"
        )

    return reason, hint


def count_dialogue_words(dialogues: List[Dict[str, Any]]) -> int:
    """
 Tong Ji dialogue Zong word count.

    Args:
 dialogues: dialogue list

    Returns:
 Zong word count
    """
    total = 0
    for dlg in dialogues:
        content = dlg.get("content", "")
        if isinstance(content, str):
            total += len(content)
    return total


def estimate_duration_from_words(word_count: int) -> int:
    """
 Gen Ju word count Gu Suan when Zhang (seconds).

    Args:
 word_count: word count

    Returns:
 Gu Suan when Zhang (seconds)
    """
    return int(word_count / WORDS_PER_SECOND)


def rebalance_remaining_budgets(
    budgets: List[SceneBudget],
    current_index: int,
    actual_duration: float,
) -> None:
    """
 Gen Ju Shi Ji when Zhang adjust subsequent scene Yu Suan.

 Ru Guo current scene Chao Shi/Qian Shi, Cong subsequent scene Yu Suan in adjust.

    Args:
 budgets: scene Yu Suan list (will Yuan Di Xiu Gai)
 current_index: current scene index
 actual_duration: current scene Shi Ji when Zhang (seconds)
    """
    if current_index >= len(budgets) - 1:
        # Shi Zui Hou a scene, Wu Xu adjust
        return

    current_budget = budgets[current_index]
    diff = actual_duration - current_budget.target_duration_seconds

    if abs(diff) < 5:
        # Cha Yi Tai Xiao, not adjust
        return

    # Ji Suan subsequent Dai Chu Li scene
    remaining_budgets = [
        b for b in budgets[current_index + 1 :] if b.status == SceneStatus.PENDING
    ]

    if not remaining_budgets:
        return

    # Cha Yi Ping Jun Fen Pei to subsequent scene
    adjustment_per_scene = -diff / len(remaining_budgets)

    for budget in remaining_budgets:
        new_target = int(budget.target_duration_seconds + adjustment_per_scene)
        # Que Bao in He Li range interior
        new_target = max(
            MIN_SCENE_DURATION_SECONDS, min(new_target, MAX_SCENE_DURATION_SECONDS)
        )
        budget.target_duration_seconds = new_target
        budget.target_word_count = calculate_target_word_count(new_target)
        budget.min_duration_seconds = int(new_target * DURATION_TOLERANCE_SCENE_LOW)
        budget.max_duration_seconds = int(new_target * DURATION_TOLERANCE_SCENE_HIGH)

    logger.info(
        "rebalance_remaining_budgets: Yu Suan then Ping Heng",
        extra={
            "current_scene": current_budget.scene_number,
            "diff_seconds": diff,
            "remaining_scenes": len(remaining_budgets),
            "adjustment_per_scene": adjustment_per_scene,
        },
    )


def format_budget_summary(budgets: List[SceneBudget]) -> str:
    """
 Ge Shi Hua Yu Suan summary, Yong Yu log and Tiao Shi.

    Args:
 budgets: scene Yu Suan list

    Returns:
 Ge Shi Hua summary Zi Fu Chuan
    """
    lines = ["scene Yu Suan summary:"]
    for b in budgets:
        status_icon = {
            SceneStatus.PENDING: "⏳",
            SceneStatus.IN_PROGRESS: "🔄",
            SceneStatus.COMMITTED: "✅",
            SceneStatus.FAILED: "❌",
        }.get(b.status, "?")

        actual_info = ""
        if b.actual_duration_seconds is not None:
            ratio = b.duration_ratio()
            actual_info = f" -> Shi Ji: {b.actual_duration_seconds:.1f}s ({ratio:.0%})"

        lines.append(
            f"  {status_icon} scene{b.scene_number}: "
            f"Mu Biao {b.target_duration_seconds}s, "
            f"Zi Shu {b.target_word_count}, "
            f"Chang Shi {b.attempt_count}Ci"
            f"{actual_info}"
        )

    return "\n".join(lines)
