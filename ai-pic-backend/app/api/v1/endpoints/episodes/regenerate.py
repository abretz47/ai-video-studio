"""
Episode regeneration endpoints.

Regenerate AI-generated episode content by reusing the generation flow.
"""

import json
from typing import Any, Dict, List

from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.script import Episode
from app.models.task import Task, TaskType
from app.models.user import User
from app.services.ai_service import ai_service  # noqa: F401
from app.services.task_worker import episode_generate_task
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .helpers import get_episode_by_identifier, get_story_by_identifier

router = APIRouter()
_ai_service_for_monkeypatch = ai_service


def _collect_previous_episodes(
    db: Session, story_id: int, current_episode_number: int, limit: int = 5
) -> List[Dict[str, Any]]:
    """Collect previous episodes for context."""
    if current_episode_number <= 1:
        return []

    previous = (
        db.query(Episode)
        .filter(
            Episode.story_id == story_id,
            Episode.episode_number < current_episode_number,
            Episode.is_deleted.is_(False),
        )
        .order_by(Episode.episode_number.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "episode_number": ep.episode_number,
            "title": ep.title,
            "logline": ep.summary[:200] if ep.summary else None,
        }
        for ep in reversed(previous)
    ]


def _build_regenerate_request(
    episode: Episode,
    previous_episodes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build request dict that mimics EpisodeGenerationRequest for regeneration."""
    original_params = episode.generation_params or {}

    # Build detailed additional requirements with full context
    additional_req_parts = [
        f"[IMPORTANT] This is a regeneration of episode {episode.episode_number}, not episode 1.",
        f"The episode number must be {episode.episode_number}.",
    ]

    if episode.summary:
        additional_req_parts.append(
            f"\nOriginal episode summary (must be followed):\n{episode.summary}"
        )

    if previous_episodes:
        additional_req_parts.append(
            "\n[Previous episode summaries] (maintain continuity and do not repeat existing content):"
        )
        for prev in previous_episodes:
            ep_desc = f"- Episode {prev['episode_number']} '{prev['title']}': {prev['logline'] or 'No summary'}"
            additional_req_parts.append(ep_desc)

    additional_requirements = "\n".join(additional_req_parts)

    return {
        "story_id": episode.story_id,
        "episode_count": 1,
        "episode_duration": episode.duration_minutes,
        "focus_characters": original_params.get("focus_characters"),
        "plot_complexity": original_params.get("plot_complexity", "medium"),
        "pacing": original_params.get("pacing", "medium"),
        "market_region": original_params.get("market_region"),
        "micro_genre": original_params.get("micro_genre"),
        "hook_plan": original_params.get("hook_plan"),
        "twist_density": original_params.get("twist_density"),
        "cliffhanger_plan": original_params.get("cliffhanger_plan"),
        "ad_snippets": original_params.get("ad_snippets"),
        "additional_requirements": additional_requirements,
        "style_preferences": original_params.get("style_preferences"),
        "model": original_params.get("model"),
        "temperature": original_params.get("temperature", 0.7),
    }


@router.post("/{episode_id}/regenerate")
async def regenerate_episode_async(
    episode_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate episode content asynchronously.

    This endpoint:
    1. Soft-deletes the existing episode
    2. Triggers the same generation flow used by generate-async
    3. Returns a task_id to track progress
    """
    episode = get_episode_by_identifier(db, episode_id, None, current_user)
    story = get_story_by_identifier(db, episode.story_id, None, current_user)

    # Collect previous episodes for context
    previous_episodes = _collect_previous_episodes(db, story.id, episode.episode_number)

    # Soft-delete the old episode FIRST so the generation flow can create a new one
    episode.soft_delete(user_id=current_user.id, reason="regenerate requested")
    db.commit()

    # Build request dict with context
    request_dict = _build_regenerate_request(episode, previous_episodes)

    # Create task
    task = Task(
        title=f"Regenerate episode - episode {episode.episode_number}",
        description=f"Regenerate episode {episode.episode_number} for story {story.id}",
        task_type=TaskType.EPISODE_GENERATION,
        prompt=f"Regenerate episode {episode.episode_number} for story {story.id}",
        parameters=json.dumps(request_dict, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Delegate to the same Celery task used by generate-async
    episode_generate_task.delay(task.id, request_dict, current_user.id)

    return {
        "success": True,
        "data": {
            "task_id": task.id,
            "status": task.status,
            "message": f"Episode {episode.episode_number} regeneration task submitted",
        },
    }


@router.post("/business/{episode_business_id}/regenerate")
async def regenerate_episode_by_business_id_async(
    episode_business_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate episode content by business ID asynchronously.

    This endpoint:
    1. Soft-deletes the existing episode
    2. Triggers the same generation flow used by generate-async
    3. Returns a task_id to track progress
    """
    episode = get_episode_by_identifier(db, None, episode_business_id, current_user)
    story = get_story_by_identifier(db, episode.story_id, None, current_user)

    # Collect previous episodes for context
    previous_episodes = _collect_previous_episodes(db, story.id, episode.episode_number)

    # Soft-delete the old episode FIRST so the generation flow can create a new one
    episode.soft_delete(user_id=current_user.id, reason="regenerate requested")
    db.commit()

    # Build request dict with context
    request_dict = _build_regenerate_request(episode, previous_episodes)

    # Create task
    task = Task(
        title=f"Regenerate episode - episode {episode.episode_number}",
        description=f"Regenerate episode {episode.episode_number} for story {story.id}",
        task_type=TaskType.EPISODE_GENERATION,
        prompt=f"Regenerate episode {episode.episode_number} for story {story.id}",
        parameters=json.dumps(request_dict, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Delegate to the same Celery task used by generate-async
    episode_generate_task.delay(task.id, request_dict, current_user.id)

    return {
        "success": True,
        "data": {
            "task_id": task.id,
            "status": task.status,
            "message": f"Episode {episode.episode_number} regeneration task submitted",
        },
    }
