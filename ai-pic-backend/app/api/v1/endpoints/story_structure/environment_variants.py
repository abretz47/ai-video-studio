"""
Story Structure environment image variant endpoints.

Image-to-image variant generation for environments (sync and async).
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
    generate_environment_image_variants as generate_environment_image_variants_service,
)
from app.services.story_structure.environment_image_prompts import (
    compose_environment_variant_prompt,
)
from app.services.story_structure.environment_image_requests import (
    build_environment_variant_task_payload,
    resolve_environment_image_variant_request,
)
from app.services.task_worker import environment_image_variant_task
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from .environment_image_helpers import get_owned_environment_or_404, read_json_payload

router = APIRouter()


class EnvironmentImageVariantParams:
    def __init__(
        self,
        base_image: str | None = Query(None, description="Base image URL or relative path"),
        prompt: str | None = Query(None, description="Variant prompt"),
        model: str | None = Query(None, description="Model, in the form provider:model_id"),
        generation_profile: str | None = Query(
            None,
            description="Generation parameter tier (backend resolves default steps/cfg/negative_prompt by provider+model)",
        ),
        count: int = Query(1, ge=1, le=4, description="Generation count"),
        size: str | None = Query(None, description="Resolution/size"),
        aspect_ratio: str | None = Query(None, description="Aspect ratio, such as 16:9 or 1:1"),
        seed: int | None = Query(None, description="Random seed (optional)"),
        steps: int | None = Query(None, description="Sampling steps (optional)"),
        cfg_scale: float | None = Query(None, description="CFG scale (optional)"),
        negative_prompt: str | None = Query(None, description="Negative prompt (optional)"),
        strength: float | None = Query(
            None, ge=0.0, le=1.0, description="Image-to-image strength (optional)"
        ),
        image_reference: str | None = Query(
            None, description="Reference dimension (optional), such as subject/face"
        ),
        image_fidelity: float | None = Query(
            None, ge=0.0, le=1.0, description="Image reference strength (optional)"
        ),
        human_fidelity: float | None = Query(
            None, ge=0.0, le=1.0, description="Character reference strength (optional)"
        ),
    ) -> None:
        self.base_image = base_image
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
        self.strength = strength
        self.image_reference = image_reference
        self.image_fidelity = image_fidelity
        self.human_fidelity = human_fidelity


@router.post("/environments/{env_id}/images/variants")
async def generate_environment_image_variants(
    env_id: str,
    request: Request,
    params: EnvironmentImageVariantParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    env = get_owned_environment_or_404(db, env_id, current_user)
    if not ai_service.ai_manager:
        raise HTTPException(status_code=503, detail="AI manager is not initialized; cannot generate variants")

    payload = await read_json_payload(request)

    try:
        base_fallback = env.reference_images[0] if env.reference_images else None
        req = resolve_environment_image_variant_request(
            payload,
            base_image=params.base_image,
            fallback_base_image=base_fallback,
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
            strength=params.strength,
            image_reference=params.image_reference,
            image_fidelity=params.image_fidelity,
            human_fidelity=params.human_fidelity,
        )
        if not req.base_image:
            raise HTTPException(status_code=400, detail="Missing base image")
        saved = await generate_environment_image_variants_service(
            db=db,
            env=env,
            request=req,
            ai_service=ai_service,
            require_upload=bool(oss_service),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"success": True, "data": {"images": saved, "count": len(saved)}}


@router.post("/environments/{env_id}/images/variants-async")
async def generate_environment_image_variants_async(
    env_id: str,
    request: Request,
    params: EnvironmentImageVariantParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Async environment image-to-image: create Task and delegate to Celery."""
    env = get_owned_environment_or_404(db, env_id, current_user)
    if not ai_service.ai_manager:
        raise HTTPException(status_code=503, detail="AI manager is not initialized; cannot generate variants")

    body = await read_json_payload(request)

    base_fallback = env.reference_images[0] if env.reference_images else None
    req = resolve_environment_image_variant_request(
        body,
        base_image=params.base_image,
        fallback_base_image=base_fallback,
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
        strength=params.strength,
        image_reference=params.image_reference,
        image_fidelity=params.image_fidelity,
        human_fidelity=params.human_fidelity,
    )
    if not req.base_image:
        raise HTTPException(status_code=400, detail="Missing base image")

    payload = build_environment_variant_task_payload(env_id=env.id, request=req)

    task = Task(
        title=f"Environment image-to-image - environment {env_id}",
        description="Generate environment image variants asynchronously",
        task_type=TaskType.ENVIRONMENT_IMAGE_VARIANT_GENERATION,
        prompt=compose_environment_variant_prompt(env, req.prompt),
        parameters=json.dumps(payload, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    environment_image_variant_task.delay(task.id, payload, current_user.id)

    return {"success": True, "data": {"task_id": task.id, "status": task.status}}
