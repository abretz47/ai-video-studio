"""
duration Jing Kong dialogue Sheng Cheng service

Hun He mode: Shi Yong Duration Orchestrator Jin Xing Yu Suan Fen Pei and validation, 
Shi Yong Mo Kuai Hua scene audio generator Jin Xing Shi Ji TTS Sheng Cheng.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from app.models.script import Episode, Script, Story
from app.models.story_structure import Scene
from app.services.duration_controlled_scene_runner import (
    generate_scene_audio_with_budgets,
)
from app.services.duration_orchestrator.nodes import (
    allocate_budget_node,
    final_validation_node,
)
from app.services.duration_orchestrator.state import SceneBudget
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# log Qian Zhui, Bian Yu log Guo Lv
LOG_PREFIX = "DurationControl"


def _scene_to_dict(scene: Scene) -> Dict[str, Any]:
    """ Scene ORM Dui Xiang Zhuan Huan as Zi Dian."""
    return {
        "scene_number": getattr(scene, "scene_number", None),
        "id": getattr(scene, "id", None),
        "title": getattr(scene, "title", None),
        "summary": getattr(scene, "summary", None),
        "location": getattr(scene, "location", None),
        "time_of_day": getattr(scene, "time_of_day", None),
        "characters": getattr(scene, "characters", None) or [],
        "estimated_duration_seconds": getattr(
            scene, "estimated_duration_seconds", None
        ),
    }


async def generate_dialogue_with_duration_control(
    db: Session,
    *,
    story: Story,
    episode: Episode,
    script: Script,
    scenes: List[Scene],
    tts_model: str = "speech-2.6-hd",
    overwrite_beats: bool = True,
    timing_model: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Shi Yong Duration Orchestrator Jin Xing duration Jing Kong dialogue Sheng Cheng."""
    start_time = time.time()
    total_duration_minutes = getattr(episode, "duration_minutes", None) or 3
    scenes_data = [_scene_to_dict(s) for s in scenes]

    logger.info(
        f"{LOG_PREFIX}: Kai Shi Shi Zhang Jing Kong Liu Cheng",
        extra={
            "phase": "start",
            "episode_id": episode.id,
            "script_id": script.id,
            "story_id": story.id,
            "scene_count": len(scenes),
            "total_duration_minutes": total_duration_minutes,
            "tts_model": tts_model,
        },
    )

    # ========== Phase 1: Yu Suan Fen Pei ==========
    phase1_start = time.time()
    if progress_callback:
        progress_callback("Phase 1/3: Fen Pei scene when Zhang Yu Suan...")

    budget_state = {
        "episode_id": episode.id,
        "script_id": script.id,
        "total_duration_minutes": total_duration_minutes,
        "scenes_from_episode": scenes_data,
        "scene_budgets": [],
        "reasoning": [],
        "errors": [],
    }

    budget_result = allocate_budget_node(budget_state)
    scene_budgets: List[SceneBudget] = budget_result.get("scene_budgets", [])
    phase1_duration = time.time() - phase1_start

    if not scene_budgets:
        logger.error(
            f"{LOG_PREFIX}: Yu Suan Fen Pei failed",
            extra={
                "phase": "budget_allocation",
                "episode_id": episode.id,
                "duration_ms": int(phase1_duration * 1000),
            },
        )
        return {
            "success": False,
            "error": "budget_allocation_failed",
            "reasoning": budget_result.get("reasoning", []),
            "timing": {"phase1_budget_ms": int(phase1_duration * 1000)},
        }

    # Ji Lu Yu Suan Fen Pei Jie Guo
    budget_summary = [
        {"scene": b.scene_number, "target_s": b.target_duration_seconds}
        for b in scene_budgets
    ]
    logger.info(
        f"{LOG_PREFIX}: Yu Suan Fen Pei Wan Cheng",
        extra={
            "phase": "budget_allocation",
            "episode_id": episode.id,
            "scene_count": len(scene_budgets),
            "budgets": budget_summary,
            "duration_ms": int(phase1_duration * 1000),
        },
    )

    # ========== Phase 2: Zhu scene Sheng Cheng ==========
    phase2 = await generate_scene_audio_with_budgets(
        db,
        story=story,
        episode=episode,
        script=script,
        scenes=scenes,
        scene_budgets=scene_budgets,
        total_duration_minutes=total_duration_minutes,
        tts_model=tts_model,
        overwrite_beats=overwrite_beats,
        timing_model=timing_model,
        progress_callback=progress_callback,
        logger=logger,
        log_prefix=LOG_PREFIX,
    )
    generation_results = phase2["generation_results"]
    total_actual_duration = phase2["total_actual_duration"]
    scene_timings = phase2["scene_timings"]
    phase2_duration = phase2["phase_duration"]

    # ========== Phase 3: Zui Zhong validation ==========
    phase3_start = time.time()
    if progress_callback:
        progress_callback("Phase 3/3: validation total duration...")

    validation_state = {
        "episode_id": episode.id,
        "total_duration_minutes": total_duration_minutes,
        "statistics": {
            "total_actual_duration_seconds": total_actual_duration,
        },
        "reasoning": budget_result.get("reasoning", []),
        "errors": [],
    }

    validation_result = final_validation_node(validation_state)
    final_validation = validation_result.get("final_validation_result", {})
    success = final_validation.get("passed", False)
    phase3_duration = time.time() - phase3_start

    # Tong Ji failed scene
    failed_scenes = [r for r in generation_results if not r.get("success")]
    if failed_scenes:
        success = False

    total_time = time.time() - start_time
    duration_ratio = final_validation.get("duration_ratio", 0)

    # Zui Zhong log
    logger.info(
        f"{LOG_PREFIX}: Liu Cheng Wan Cheng",
        extra={
            "phase": "complete",
            "episode_id": episode.id,
            "success": success,
            "total_target_duration": total_duration_minutes * 60,
            "total_actual_duration": round(total_actual_duration, 2),
            "duration_ratio": round(duration_ratio, 4),
            "validation_passed": final_validation.get("passed", False),
            "scene_count": len(scenes),
            "failed_count": len(failed_scenes),
            "timing": {
                "total_ms": int(total_time * 1000),
                "phase1_budget_ms": int(phase1_duration * 1000),
                "phase2_generation_ms": int(phase2_duration * 1000),
                "phase3_validation_ms": int(phase3_duration * 1000),
                "avg_scene_ms": (
                    int(sum(scene_timings) / len(scene_timings)) if scene_timings else 0
                ),
            },
        },
    )

    if progress_callback:
        status = "through" if success else "not through"
        progress_callback(
            f"Wan Cheng: {status} (Shi Zhang Bi {duration_ratio:.1%}, " f"Hao Shi {total_time:.1f}s)"
        )

    return {
        "success": success,
        "episode_id": episode.id,
        "script_id": script.id,
        # Yu Suan Xin Xi
        "scene_budgets": [b.to_dict() for b in scene_budgets],
        # Sheng Cheng Jie Guo
        "generation_results": generation_results,
        # Tong Ji Xin Xi
        "statistics": {
            "total_target_duration_seconds": total_duration_minutes * 60,
            "total_actual_duration_seconds": round(total_actual_duration, 2),
            "duration_ratio": round(duration_ratio, 4),
            "scene_count": len(scenes),
            "successful_count": len(scenes) - len(failed_scenes),
            "failed_count": len(failed_scenes),
        },
        # validation Jie Guo
        "final_validation": final_validation,
        # Shi Xu Xin Xi
        "timing": {
            "total_ms": int(total_time * 1000),
            "phase1_budget_ms": int(phase1_duration * 1000),
            "phase2_generation_ms": int(phase2_duration * 1000),
            "phase3_validation_ms": int(phase3_duration * 1000),
        },
        # Tui Li log
        "reasoning": validation_result.get("reasoning", []),
        "errors": validation_result.get("errors", []),
    }
