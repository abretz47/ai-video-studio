"""
Zui Zhong validation node

validation episode total duration Shi Fou in target range interior(±10%).
"""

import logging
from typing import Any, Dict

from app.services.duration_orchestrator.constants import (
    DURATION_TOLERANCE_EPISODE_HIGH,
    DURATION_TOLERANCE_EPISODE_LOW,
)

logger = logging.getLogger(__name__)

# Rong Cha Bai Fen Bi (10%)
TOLERANCE_PERCENT = (1 - DURATION_TOLERANCE_EPISODE_LOW) * 100


def final_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 Zui Zhong validation node.

 validation episode total duration Shi Fou in target Rong Cha range interior(default ±10%).

 input status:
 - statistics: Tong Ji Xin Xi(Bao Han total_actual_duration_seconds)
 - total_duration_minutes: target total duration(minutes)

 output status update:
 - final_validation_result: validation Jie Guo
 - success: Shi Fou validation through
 - reasoning: Tian Jia validation log
    """
    statistics = state.get("statistics", {})
    total_duration_minutes = state.get("total_duration_minutes", 0)
    episode_id = state.get("episode_id")

    reasoning = state.get("reasoning", [])
    errors = state.get("errors", [])

    # get Shi Ji and target when Zhang
    total_actual = statistics.get("total_actual_duration_seconds", 0)
    total_target = total_duration_minutes * 60

    # Ji Suan when Zhang ratio
    ratio = total_actual / total_target if total_target > 0 else 0

    # Ji Suan Rong Cha range (Shi Yong Chang Liang Ding Yi LOW/HIGH)
    min_ratio = DURATION_TOLERANCE_EPISODE_LOW
    max_ratio = DURATION_TOLERANCE_EPISODE_HIGH

    # determine Shi Fou in Rong Cha interior
    is_within_tolerance = min_ratio <= ratio <= max_ratio

    # Ji Suan Pian Cha
    deviation_seconds = total_actual - total_target
    deviation_percent = (ratio - 1) * 100

    logger.info(
        "final_validation_node: Zui Zhong validation",
        extra={
            "episode_id": episode_id,
            "total_actual": total_actual,
            "total_target": total_target,
            "ratio": ratio,
            "min_ratio": min_ratio,
            "max_ratio": max_ratio,
            "is_within_tolerance": is_within_tolerance,
            "deviation_seconds": deviation_seconds,
            "deviation_percent": deviation_percent,
        },
    )

    # build validation Jie Guo
    validation_result = {
        "passed": is_within_tolerance,
        "total_actual_duration_seconds": round(total_actual, 2),
        "total_target_duration_seconds": total_target,
        "duration_ratio": round(ratio, 4),
        "deviation_seconds": round(deviation_seconds, 2),
        "deviation_percent": round(deviation_percent, 2),
        "tolerance_percent": TOLERANCE_PERCENT,
        "tolerance_range": {
            "min_seconds": round(total_target * min_ratio, 2),
            "max_seconds": round(total_target * max_ratio, 2),
        },
    }

    # Sheng Cheng validation log
    if is_within_tolerance:
        reasoning.append(
            f"Zui Zhong Yan Zheng Tong Guo: Zong Shi Zhang {total_actual:.1f}s / {total_target}s "
            f"({ratio:.1%}), Zai ±{TOLERANCE_PERCENT:.0f}% Rong Cha Nei"
        )
    else:
        direction = "Guo Chang" if ratio > 1 else "Guo Duan"
        reasoning.append(
            f"Zui Zhong Yan Zheng failed: Zong Shi Zhang {total_actual:.1f}s / {total_target}s "
            f"({ratio:.1%}), {direction} {abs(deviation_percent):.1f}%, "
            f"Chao Chu ±{TOLERANCE_PERCENT:.0f}% Rong Cha"
        )
        errors.append(
            f"Episode {episode_id} Zong Shi Zhang Yan Zheng failed: "
            f"{direction} {abs(deviation_percent):.1f}%"
        )

    return {
        "final_validation_result": validation_result,
        "success": is_within_tolerance,
        "reasoning": reasoning,
        "errors": errors,
        "phase": "validated",
    }


def should_pass_or_fail(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Zui Zhong validation Shi Fou through.

    Returns:
 "pass" - validation through
 "fail" - validation failed
    """
    validation_result = state.get("final_validation_result", {})
    return "pass" if validation_result.get("passed", False) else "fail"
