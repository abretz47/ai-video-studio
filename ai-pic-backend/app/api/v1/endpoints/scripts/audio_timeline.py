"""Episode-level audio timeline generation endpoints and task processor."""

from __future__ import annotations

import json

from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.task import Task, TaskStatus, TaskType
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.audio.episode_audio_builder import generate_episode_audio_timeline
from app.services.script.task_titles import friendly_task_title
from app.services.task_worker import script_audio_timeline_generate_task
from app.services.timeline_import_service import import_audio_timeline_to_timeline_spec
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .audio_pipeline_utils import (
    episode_has_audio_timeline,
    load_script_with_access,
    mark_pipeline_endpoint_deprecated,
    run_async_task_sync,
    update_task_progress,
)

router = APIRouter()


class ScriptAudioTimelineGenerateRequest(BaseModel):
    overwrite: bool = Field(False, description="Overwrite existing episode timeline")


@router.post("/{script_id}/audio-timeline/generate-async", deprecated=True)
async def generate_script_audio_timeline_async(
    script_id: int,
    body: ScriptAudioTimelineGenerateRequest,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Queue async episode audio timeline generation for a script."""
    script = load_script_with_access(db, script_id, current_user)
    if not script:
        raise HTTPException(status_code=404, detail="Script does not exist")

    story = script.episode.story if script.episode else None
    episode = script.episode if script.episode else None
    params = body.model_dump()
    params["script_id"] = script_id

    task = Task(
        title=friendly_task_title("Timeline generation", script, episode, story),
        description="Concatenate scene audio tracks and generate the timeline (episode)",
        task_type=TaskType.TIMELINE_GENERATION,
        prompt=f"Episode audio timeline generation for script {script_id}",
        parameters=json.dumps(params, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    mark_pipeline_endpoint_deprecated(
        response,
        successor_path=f"/api/v1/scripts/{script_id}/timeline-pipeline/generate-async",
    )
    script_audio_timeline_generate_task.delay(task.id, params, current_user.id)
    return {"success": True, "data": {"task_id": task.id, "status": task.status}}


def _process_script_audio_timeline_task(
    task_id: int,
    payload: dict,
    user_id: int,
) -> None:
    """Celery worker handler for episode audio timeline generation."""
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        task_repo = TaskRepository(db)
        user_repo = UserRepository(db)
        task = task_repo.get_by_id(task_id)
        if task:
            task.status = TaskStatus.PROCESSING
            db.commit()

        script_id = int(payload.get("script_id"))
        overwrite = bool(payload.get("overwrite"))

        async def _run() -> None:
            user = user_repo.get_by_id(user_id)
            if not user:
                raise RuntimeError("user_not_found")

            script = load_script_with_access(db, script_id, user)
            if not script:
                raise RuntimeError("script_not_found")

            episode = script.episode
            if not episode:
                raise RuntimeError("episode_not_found")

            story = episode.story
            if not story:
                raise RuntimeError("story_not_found")

            audio_timeline_payload = None
            if not overwrite and episode_has_audio_timeline(episode, script_id):
                update_task_progress(
                    db,
                    task,
                    "An episode timeline already exists; import the Timeline Spec instead (enable overwrite to recompute)",
                )
            else:
                update_task_progress(db, task, "Concatenating scene audio tracks and generating timeline...")
                audio_timeline_payload = await generate_episode_audio_timeline(
                    db,
                    story=story,
                    episode=episode,
                    script=script,
                )

            import_result = import_audio_timeline_to_timeline_spec(
                db,
                episode=episode,
                script=script,
                audio_timeline=audio_timeline_payload,
                overwrite=overwrite,
                user_id=user.id,
            )
            update_task_progress(
                db,
                task,
                f"Timeline Spec v1 {import_result.action}",
            )

        run_async_task_sync(_run)

        if task:
            task.status = TaskStatus.COMPLETED
            task.result_file_path = f"script:{script_id}:audio_timeline"
            update_task_progress(db, task, "Timeline generation completed")
    except Exception as exc:
        task = TaskRepository(db).get_by_id(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(exc)
            update_task_progress(db, task, f"Timeline generation failed: {exc}")
    finally:
        db.close()


__all__ = [
    "router",
    "ScriptAudioTimelineGenerateRequest",
    "generate_script_audio_timeline_async",
    "_process_script_audio_timeline_task",
]
