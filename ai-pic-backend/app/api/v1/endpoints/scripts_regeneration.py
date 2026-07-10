"""Script regeneration endpoints."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.api.v1.endpoints.scripts_route_utils import get_script_by_identifier
from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.script import Episode, Script
from app.models.task import Task, TaskType
from app.models.user import User
from app.services.script.task_titles import friendly_task_title
from app.services.task_worker import script_regenerate_task
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter()


class ScriptRegenerateRequest(BaseModel):
    """Script regeneration request parameters"""

    model: Optional[str] = Field(None, description="Model ID, in provider:model_id format")


def build_script_regenerate_request(
    script: Script, episode: Episode, override_model: Optional[str] = None
) -> Dict[str, Any]:
    """Build the request-parameter dictionary for script regeneration."""
    original_params = script.generation_params or {}
    duration_minutes = getattr(episode, "duration_minutes", None)
    return {
        "script_id": script.id,
        "format_type": script.format_type,
        "language": script.language,
        "dialogue_style": original_params.get("dialogue_style", "natural"),
        "scene_detail_level": original_params.get("scene_detail_level", "medium"),
        "market_region": original_params.get("market_region"),
        "micro_genre": original_params.get("micro_genre"),
        "hook_plan": original_params.get("hook_plan"),
        "twist_density": original_params.get("twist_density"),
        "cliffhanger_plan": original_params.get("cliffhanger_plan"),
        "ad_snippets": original_params.get("ad_snippets"),
        "additional_requirements": f"Regenerate the script content for episode {episode.episode_number}",
        "style_preferences": original_params.get("style_preferences"),
        "model": override_model or original_params.get("model"),
        "temperature": original_params.get("temperature", 0.7),
        "duration_minutes": duration_minutes,
    }


@router.post("/{script_id}/regenerate")
async def regenerate_script_async(
    script_id: int,
    request: Optional[ScriptRegenerateRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Regenerate script content asynchronously"""
    script = get_script_by_identifier(db, script_id, None, current_user)
    return _enqueue_script_regeneration(script, request, current_user, db)


@router.post("/business/{script_business_id}/regenerate")
async def regenerate_script_by_business_id_async(
    script_business_id: str,
    request: Optional[ScriptRegenerateRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Regenerate script content asynchronously by business_id"""
    script = get_script_by_identifier(db, None, script_business_id, current_user)
    return _enqueue_script_regeneration(script, request, current_user, db)


def _enqueue_script_regeneration(
    script: Script,
    request: Optional[ScriptRegenerateRequest],
    current_user: User,
    db: Session,
) -> Dict[str, Any]:
    episode = script.episode
    if not episode or getattr(episode, "is_deleted", False):
        raise HTTPException(status_code=404, detail="Episode does not exist")

    story = episode.story
    if not story or getattr(story, "is_deleted", False):
        raise HTTPException(status_code=404, detail="Story does not exist")

    override_model = request.model if request else None
    request_dict = build_script_regenerate_request(script, episode, override_model)

    task = Task(
        title=friendly_task_title("Script regeneration", script, episode, story),
        description=f"Regenerate script {script.id} (episode {episode.episode_number})",
        task_type=TaskType.SCRIPT_GENERATION,
        prompt=f"Script regeneration for script {script.id}",
        parameters=json.dumps(request_dict, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    script_regenerate_task.delay(task.id, request_dict, current_user.id)
    return {
        "success": True,
        "data": {
            "task_id": task.id,
            "status": task.status,
            "message": "Script regeneration task submitted",
        },
    }
