"""
Celery Ren Wu entry point

Mu Qian Zhu Yao Yong Yu Diao Du Story/Episode/Script related async Sheng Cheng Ren Wu.
"""

from __future__ import annotations

from typing import Any, Dict

from app.core.celery_app import celery_app

# Re-export asset/image tasks for compatibility imports.
from app.services.task_worker_assets import (  # noqa: F401
    environment_image_generate_task,
    environment_image_variant_task,
    virtual_ip_image_generate_task,
    virtual_ip_image_variant_task,
)
from app.services.task_worker_grid_storyboard import (  # noqa: F401
    grid_storyboard_sheet_generate_task,
)

# Re-export storyboard media tasks for compatibility imports.
from app.services.task_worker_storyboard_media import (  # noqa: F401
    storyboard_image_generate_task,
    storyboard_video_generate_task,
)

__all__ = [
    "environment_image_generate_task",
    "environment_image_variant_task",
    "grid_storyboard_sheet_generate_task",
    "storyboard_image_generate_task",
    "storyboard_video_generate_task",
    "virtual_ip_image_generate_task",
    "virtual_ip_image_variant_task",
]

EPISODE_GENERATE_SOFT_TIME_LIMIT = 7200
EPISODE_GENERATE_TIME_LIMIT = 7500


@celery_app.task(name="tasks.story_generate")
def story_generate_task(
    task_id: int, request_dict: Dict[str, Any], user_id: int
) -> None:
    """
 async story Sheng Cheng Ren Wu entry point.

 as avoid Dao Ru Huan Zao Cheng Fu Zuo Yong, here Yi Lai in function Nei Bu An need Dao Ru.
    """
    from app.api.v1.endpoints.stories import _process_story_generation_task

    _process_story_generation_task(task_id, request_dict, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="story",
        request_dict=request_dict,
    )


@celery_app.task(name="tasks.story_novel_generate")
def story_novel_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """async Dao Chu Zhi Hu Ti Xiao Shuo Ren Wu entry point."""
    from app.api.v1.endpoints.stories import process_story_novel_export_task

    process_story_novel_export_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="text_generation",
    )


@celery_app.task(
    name="tasks.episode_generate",
    soft_time_limit=EPISODE_GENERATE_SOFT_TIME_LIMIT,
    time_limit=EPISODE_GENERATE_TIME_LIMIT,
)
def episode_generate_task(
    task_id: int, request_dict: Dict[str, Any], user_id: int
) -> None:
    """async episode Sheng Cheng Ren Wu entry point."""
    from app.api.v1.endpoints.episodes import process_episode_generation_task

    process_episode_generation_task(task_id, request_dict, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="episode",
        request_dict=request_dict,
    )


@celery_app.task(name="tasks.script_generate")
def script_generate_task(
    task_id: int, request_dict: Dict[str, Any], user_id: int
) -> None:
    """async script Sheng Cheng Ren Wu entry point."""
    from app.services.script.generation_task_processor import (
        process_script_generation_task,
    )

    process_script_generation_task(task_id, request_dict, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="script",
        request_dict=request_dict,
    )


@celery_app.task(name="tasks.script_regenerate")
def script_regenerate_task(
    task_id: int, request_dict: Dict[str, Any], user_id: int
) -> None:
    """async script retry Sheng Cheng Ren Wu entry point."""
    from app.services.script.regeneration_task_processor import (
        process_script_regeneration_task,
    )

    process_script_regeneration_task(task_id, request_dict, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="script",
        request_dict=request_dict,
    )


@celery_app.task(name="tasks.script_dialogue_audio_generate")
def script_dialogue_audio_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """async Sheng Cheng script scene dialogue Yin Gui Ren Wu entry point."""
    from app.api.v1.endpoints.scripts import _process_script_dialogue_audio_task

    _process_script_dialogue_audio_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="dialogue_audio",
    )


@celery_app.task(name="tasks.script_audio_timeline_generate")
def script_audio_timeline_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """async Sheng Cheng episode dialogue Yin Gui Pin Jie and timeline Ren Wu entry point."""
    from app.api.v1.endpoints.scripts import _process_script_audio_timeline_task

    _process_script_audio_timeline_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="timeline_generation",
    )


@celery_app.task(name="tasks.script_audio_storyboard_generate")
def script_audio_storyboard_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """async Cong episode audio timeline Sheng Cheng Fen Jing Zhen Zhan Wei Ren Wu entry point."""
    from app.api.v1.endpoints.scripts import _process_script_audio_storyboard_task

    _process_script_audio_storyboard_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="storyboard_from_audio_timeline",
    )


@celery_app.task(name="tasks.storyboard_generate")
def storyboard_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """async storyboard structure Sheng Cheng Ren Wu entry point."""
    from app.api.v1.endpoints.scripts import _process_storyboard_generation_task

    _process_storyboard_generation_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="storyboard_generation",
    )


@celery_app.task(name="tasks.timeline_pipeline_generate")
def timeline_pipeline_generate_task(
    task_id: int, payload: Dict[str, Any], user_id: int
) -> None:
    """Yi Jian Sheng Cheng timeline Liu Shui Xian Ren Wu entry point(dialogue Yin Gui → timeline → storyboard Zhen Zhan Wei)."""
    from app.api.v1.endpoints.scripts import _process_timeline_pipeline_task

    _process_timeline_pipeline_task(task_id, payload, user_id)
    from app.services.task_agent_run import persist_task_agent_run

    persist_task_agent_run(
        task_id=task_id,
        user_id=user_id,
        kind="timeline_pipeline",
    )


@celery_app.task(
    name="tasks.video_generation_poll", soft_time_limit=120, time_limit=180
)
def video_generation_poll_task(limit: int = 50) -> int:
    """Ji Zhong Lun Xun video Sheng Cheng Ren Wu status."""
    from app.services.video.video_task_entrypoints import poll_pending_video_tasks

    return poll_pending_video_tasks(limit=limit)
