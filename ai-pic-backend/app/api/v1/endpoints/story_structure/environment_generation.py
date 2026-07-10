"""
Story Structure environment image generation endpoints.

Text-to-image generation for environments (sync and async).
"""

from __future__ import annotations

import json

from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.task import Task, TaskType
from app.models.user import User
from app.services.ai_service import ai_service
from app.services.storage import oss_service
from app.services.story_structure.environment_image_generation import (
    generate_environment_images as generate_environment_images_service,
)
from app.services.story_structure.environment_image_prompts import (
    compose_environment_prompt,
)
from app.services.story_structure.environment_image_requests import (
    build_environment_text_to_image_task_payload,
    resolve_environment_text_to_image_request,
)
from app.services.task_worker import environment_image_generate_task
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from .environment_image_helpers import get_owned_environment_or_404, read_json_payload

router = APIRouter()


class EnvironmentImageGenerateParams:
    def __init__(
        self,
        prompt: str | None = Query(
            None, description="Generation prompt; uses the environment description/name when omitted"
        ),
        model: str | None = Query(None, description="Model, in the form provider:model_id"),
        generation_profile: str | None = Query(
            None,
            description="Generation parameter tier (backend resolves default steps/cfg/negative_prompt by provider+model)",
        ),
        count: int = Query(1, ge=1, le=4, description="Generation count"),
        size: str | None = Query(None, description="Resolution/size, such as 1024x1024 or 2K"),
        aspect_ratio: str | None = Query(None, description="Aspect ratio, such as 16:9 or 1:1"),
        seed: int | None = Query(None, description="Random seed (optional)"),
        steps: int | None = Query(None, description="Sampling steps (optional)"),
        cfg_scale: float | None = Query(None, description="CFG scale (optional)"),
        negative_prompt: str | None = Query(None, description="Negative prompt (optional)"),
    ) -> None:
        self.prompt = prompt
        self.model = model
        self.generation_profile = generation_profile
        self.count = count
        self.size = size
        self.aspect_ratio = aspect_ratio
        self.seed = seed
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.negative_prompt = negative_prompt


@router.post("/environments/{env_id}/images/generate")
async def generate_environment_images(
    env_id: str,
    request: Request,
    params: EnvironmentImageGenerateParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    env = get_owned_environment_or_404(db, env_id, current_user)
    if not ai_service.ai_manager:
        raise HTTPException(status_code=503, detail="AI manager is not initialized; cannot generate environment images")

    payload = await read_json_payload(request)

    try:
        req = resolve_environment_text_to_image_request(
            payload,
            prompt=params.prompt,
            model=params.model,
            count=params.count,
            size=params.size,
            aspect_ratio=params.aspect_ratio,
            generation_profile=params.generation_profile,
            seed=params.seed,
            steps=params.steps,
            cfg_scale=params.cfg_scale,
            negative_prompt=params.negative_prompt,
        )
        saved = await generate_environment_images_service(
            db=db,
            env=env,
            request=req,
            ai_service=ai_service,
            require_upload=bool(oss_service),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"success": True, "data": {"images": saved, "count": len(saved)}}


@router.post("/environments/{env_id}/images/generate-async")
async def generate_environment_images_async(
    env_id: str,
    request: Request,
    params: EnvironmentImageGenerateParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Async environment text-to-image: create Task and delegate to Celery."""
    env = get_owned_environment_or_404(db, env_id, current_user)
    if not ai_service.ai_manager:
        raise HTTPException(status_code=503, detail="AI manager is not initialized; cannot generate environment images")

    body = await read_json_payload(request)

    req = resolve_environment_text_to_image_request(
        body,
        prompt=params.prompt,
        model=params.model,
        count=params.count,
        size=params.size,
        aspect_ratio=params.aspect_ratio,
        generation_profile=params.generation_profile,
        seed=params.seed,
        steps=params.steps,
        cfg_scale=params.cfg_scale,
        negative_prompt=params.negative_prompt,
    )
    payload = build_environment_text_to_image_task_payload(env_id=env.id, request=req)

    task = Task(
        title=f"Environment text-to-image - environment {env_id}",
        description="Generate environment images asynchronously",
        task_type=TaskType.ENVIRONMENT_IMAGE_GENERATION,
        prompt=compose_environment_prompt(env, req.prompt),
        parameters=json.dumps(payload, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    environment_image_generate_task.delay(task.id, payload, current_user.id)

    return {"success": True, "data": {"task_id": task.id, "status": task.status}}
