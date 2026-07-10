from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.task import Task, TaskType
from app.models.user import User
from app.prompts.template_audit import build_prompt_template_audit
from app.repositories.environment_repository import EnvironmentRepository
from app.repositories.virtual_ip_repository import VirtualIPRepository
from app.schemas.production_canvas import (
    ProductionCanvasSkillExecuteRequest,
    ProductionCanvasSkillExecuteResponse,
    ProductionCanvasSkillResult,
)
from app.services.production_canvas.execution_common import (
    blocked_result,
    skill_definition,
)
from app.services.story_structure.environment_image_prompts import (
    compose_environment_prompt,
)
from app.services.story_structure.environment_image_requests import (
    build_environment_text_to_image_task_payload,
    resolve_environment_text_to_image_request,
)
from app.services.task_worker_assets import (
    environment_image_generate_task,
    virtual_ip_image_generate_task,
)
from app.utils.model_utils import DEFAULT_OPENAI_IMAGE_MODEL


def _image_model(request: ProductionCanvasSkillExecuteRequest) -> str:
    return request.model or DEFAULT_OPENAI_IMAGE_MODEL


def _running_response(
    *,
    request: ProductionCanvasSkillExecuteRequest,
    skill_id: str,
    title: str,
    detail: str,
    task: Task,
    outputs: dict,
) -> ProductionCanvasSkillExecuteResponse:
    skill = skill_definition(skill_id)
    return ProductionCanvasSkillExecuteResponse(
        task_id=task.id,
        task_status=task.status.value,
        skill_result=ProductionCanvasSkillResult(
            skill=skill_id,
            label=skill.label if skill else skill_id,
            status="running",
            title=title,
            detail=detail,
            outputs={
                **outputs,
                "dispatched_task_id": task.id,
                "task_status": task.status.value,
                **({"canvas_run_id": request.run_id} if request.run_id else {}),
            },
            reuse_targets=skill.reuse_targets if skill else [],
        ),
    )


def execute_virtual_ip_image_generation(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    if request.virtual_ip_id is None:
        return blocked_result(
            request,
            title="Virtual IP Image waiting IP context",
            detail="need first Bang Ding virtual_ip_id, Zhi Hou Cai will submit existing Xu Ni IP Tu Sheng Cheng Ren Wu.",
            required_inputs=["virtual_ip_id"],
        )

    virtual_ip = VirtualIPRepository(db).get_owned_by_id(request.virtual_ip_id, user)
    payload = {
        "virtual_ip_id": virtual_ip.id,
        "virtual_ip_business_id": getattr(virtual_ip, "business_id", None),
        "virtual_ip_name": virtual_ip.name,
        "aggregated_description": "，".join(
            item
            for item in [
                (virtual_ip.description or "").strip(),
                (getattr(virtual_ip, "style_prompt", None) or "").strip(),
            ]
            if item
        ),
        "style": "realistic",
        "style_preset_id": None,
        "style_spec": None,
        "category": "portrait",
        "model": _image_model(request),
        "count": 1,
        "size": None,
        "aspect_ratio": request.aspect_ratio,
        "generation_profile": None,
        "seed": None,
        "steps": None,
        "cfg_scale": None,
        "negative_prompt": None,
        "additional_prompts": [request.prompt],
        "is_default": False,
        "prompt_template": build_prompt_template_audit("virtual_ip_image"),
    }
    task = Task(
        title=f"Sheng Chan Hua Bu Zhi Xing Virtual IP Image - {virtual_ip.name}",
        description="Production canvas virtual_ip.image skill dispatch",
        task_type=TaskType.VIRTUAL_IP_IMAGE_GENERATION,
        prompt=f"VirtualIP image gen for {virtual_ip.name}",
        parameters=json.dumps(payload, ensure_ascii=False),
        target_business_id=request.run_id,
        user_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    virtual_ip_image_generate_task.delay(task.id, payload, user.id)
    return _running_response(
        request=request,
        skill_id="virtual_ip.image",
        title="submit existing Xu Ni IP Tu Sheng Cheng Ren Wu",
        detail="background through existing VIRTUAL_IP_IMAGE_GENERATION worker execute.",
        task=task,
        outputs={
            "virtual_ip_id": virtual_ip.id,
            "virtual_ip_ids": [virtual_ip.id],
            "model": payload["model"],
            "aspect_ratio": request.aspect_ratio,
        },
    )


def execute_environment_image_generation(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    if request.environment_id is None:
        return blocked_result(
            request,
            title="Environment Image waiting environment context",
            detail="need first Bang Ding environment_id, Zhi Hou Cai will submit existing environment Tu Sheng Cheng Ren Wu.",
            required_inputs=["environment_id"],
        )

    environment = EnvironmentRepository(db).get_owned_by_identifier(
        request.environment_id,
        user,
    )
    image_request = resolve_environment_text_to_image_request(
        {"prompt": request.prompt},
        prompt=request.prompt,
        model=_image_model(request),
        count=1,
        size=None,
        aspect_ratio=request.aspect_ratio,
    )
    payload = build_environment_text_to_image_task_payload(
        env_id=environment.id,
        request=image_request,
    )
    task = Task(
        title=f"Sheng Chan Hua Bu Zhi Xing Environment Image - Huan Jing{environment.id}",
        description="Production canvas environment.image skill dispatch",
        task_type=TaskType.ENVIRONMENT_IMAGE_GENERATION,
        prompt=compose_environment_prompt(environment, image_request.prompt),
        parameters=json.dumps(payload, ensure_ascii=False),
        target_business_id=request.run_id,
        user_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    environment_image_generate_task.delay(task.id, payload, user.id)
    return _running_response(
        request=request,
        skill_id="environment.image",
        title="submit existing environment Tu Sheng Cheng Ren Wu",
        detail="background through existing ENVIRONMENT_IMAGE_GENERATION worker execute.",
        task=task,
        outputs={
            "environment_id": environment.id,
            "environment_ids": [environment.id],
            "model": payload.get("model"),
            "aspect_ratio": payload.get("aspect_ratio"),
        },
    )
