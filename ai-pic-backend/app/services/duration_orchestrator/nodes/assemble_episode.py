"""
episode assemble node

He Bing all scene dialogue, when Zhang Xin Xi, Zhun Bei Zui Zhong output.
"""

import logging
from typing import Any, Dict, List

from app.services.duration_orchestrator.state import SceneBudget, SceneStatus

logger = logging.getLogger(__name__)


def assemble_episode_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 episode assemble node.

 He Bing all submit scene data, Ji Suan total duration, Zhun Bei Zui Zhong output.

 input status:
 - scene_budgets: scene Yu Suan list
 - committed_scenes: submit scene data
 - generated_dialogues: all Sheng Cheng dialogue

 output status update:
 - assembled_episode: assemble after episode data
 - statistics: Tong Ji Xin Xi
 - reasoning: Tian Jia assemble log
    """
    budgets: List[SceneBudget] = state.get("scene_budgets", [])
    committed_scenes = state.get("committed_scenes", {})
    episode_id = state.get("episode_id")
    script_id = state.get("script_id")
    total_duration_minutes = state.get("total_duration_minutes", 0)

    reasoning = state.get("reasoning", [])
    errors = state.get("errors", [])

    # Ji Suan total duration
    total_actual_duration = 0.0
    total_target_duration = total_duration_minutes * 60

    # Tong Ji Ge scene status
    committed_count = 0
    failed_count = 0
    total_retries = 0

    for budget in budgets:
        if budget.status == SceneStatus.COMMITTED:
            committed_count += 1
            if budget.actual_duration_seconds:
                total_actual_duration += budget.actual_duration_seconds
        elif budget.status == SceneStatus.FAILED:
            failed_count += 1

        total_retries += max(0, budget.attempt_count - 1)

    # assemble dialogue list
    all_dialogues = []
    scene_order = sorted(committed_scenes.keys())

    for scene_number in scene_order:
        scene_data = committed_scenes.get(scene_number, {})
        scene_dialogues = scene_data.get("dialogues", [])

        # Que Bao dialogue has scene ID
        for dialogue in scene_dialogues:
            if "scene_number" not in dialogue:
                dialogue["scene_number"] = scene_number
            all_dialogues.append(dialogue)

    # Ji Suan when Zhang ratio
    duration_ratio = (
        total_actual_duration / total_target_duration
        if total_target_duration > 0
        else 0
    )

    # Ji Suan Ping Jun retry Ci Shu
    avg_retries = total_retries / len(budgets) if budgets else 0

    logger.info(
        "assemble_episode_node: episode assemble complete",
        extra={
            "episode_id": episode_id,
            "script_id": script_id,
            "scene_count": len(budgets),
            "committed_count": committed_count,
            "failed_count": failed_count,
            "total_actual_duration": total_actual_duration,
            "total_target_duration": total_target_duration,
            "duration_ratio": duration_ratio,
            "total_retries": total_retries,
            "dialogue_count": len(all_dialogues),
        },
    )

    # build assemble Jie Guo
    assembled_episode = {
        "episode_id": episode_id,
        "script_id": script_id,
        "dialogues": all_dialogues,
        "scene_results": [
            {
                "scene_number": b.scene_number,
                "target_duration_seconds": b.target_duration_seconds,
                "actual_duration_seconds": b.actual_duration_seconds,
                "status": b.status.value,
                "attempt_count": b.attempt_count,
                "deviation_seconds": (
                    b.actual_duration_seconds - b.target_duration_seconds
                    if b.actual_duration_seconds
                    else None
                ),
            }
            for b in budgets
        ],
        "committed_scenes": committed_scenes,
    }

    # build Tong Ji Xin Xi
    statistics = {
        "total_target_duration_seconds": total_target_duration,
        "total_actual_duration_seconds": round(total_actual_duration, 2),
        "duration_ratio": round(duration_ratio, 4),
        "scene_count": len(budgets),
        "committed_count": committed_count,
        "failed_count": failed_count,
        "total_retries": total_retries,
        "avg_retries_per_scene": round(avg_retries, 2),
        "dialogue_count": len(all_dialogues),
    }

    reasoning.append(
        f"剧集组装完成: {committed_count}/{len(budgets)} 场景已提交, "
        f"总时长 {total_actual_duration:.1f}s / {total_target_duration}s "
        f"({duration_ratio:.1%})"
    )

    return {
        "assembled_episode": assembled_episode,
        "statistics": statistics,
        "reasoning": reasoning,
        "errors": errors,
        "phase": "assembled",
    }
