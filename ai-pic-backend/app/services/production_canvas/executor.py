from __future__ import annotations

from app.models.user import User
from app.schemas.generation_requests import ScriptGenerationRequest
from app.schemas.production_canvas import (
    ProductionCanvasSkillExecuteRequest,
    ProductionCanvasSkillExecuteResponse,
    ProductionCanvasSkillResult,
)
from app.services.production_canvas.execution_common import (
    blocked_result,
    load_script,
    skill_definition,
)
from app.services.production_canvas.asset_generation import (
    execute_environment_image_generation,
    execute_virtual_ip_image_generation,
)
from app.services.production_canvas.immediate_execution import (
    execute_asset_selection,
    execute_brief_compose,
)
from app.services.production_canvas.media_execution import (
    execute_storyboard_images,
    execute_storyboard_video_candidates,
)
from app.services.production_canvas.report_execution import execute_report_summary
from app.services.script.generation_queue import queue_script_generation_task
from app.services.script.timeline_pipeline_queue import queue_timeline_pipeline_task
from app.services.storyboard.generation_queue import queue_storyboard_generation_task
from sqlalchemy.orm import Session


def _execute_script_generation(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    skill = skill_definition("script.generate")
    if request.episode_id is None:
        return blocked_result(
            request,
            title="Script Skill waiting episode context",
            detail="need first Bang Ding episode_id, Zhi Hou Cai will submit existing SCRIPT_GENERATION Ren Wu.",
            required_inputs=["episode_id"],
        )

    script_request = ScriptGenerationRequest(
        episode_id=request.episode_id,
        generation_mode="production",
        auto_timeline_pipeline=True,
        additional_requirements=request.prompt,
    )
    task = queue_script_generation_task(
        db,
        user,
        script_request,
        title=f"Sheng Chan Hua Bu Zhi Xing Script Skill - episode{request.episode_id}",
        description="Production canvas script.generate skill dispatch",
        prompt=request.prompt,
        target_business_id=request.run_id,
    )
    return _running_response(
        skill_id="script.generate",
        label=skill.label if skill else "Script Skill",
        title="submit existing script Sheng Cheng Ren Wu",
        detail="background through existing SCRIPT_GENERATION Celery worker execute.",
        task=task,
        outputs={"episode_id": request.episode_id},
        reuse_targets=skill.reuse_targets if skill else [],
        canvas_run_id=request.run_id,
    )


def _execute_storyboard_generation(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    skill = skill_definition("storyboard.plan")
    script = load_script(db, user, request.script_id)
    if script is None:
        return blocked_result(
            request,
            title="Storyboard Skill waiting script context",
            detail="need first Bang Ding script_id, Zhi Hou Cai will submit existing STORYBOARD_GENERATION Ren Wu.",
            required_inputs=["script_id"],
        )

    task = queue_storyboard_generation_task(
        db,
        user,
        script,
        title=f"Sheng Chan Hua Bu Zhi Xing Storyboard Skill - script{script.id}",
        description="Production canvas storyboard.plan skill dispatch",
        prompt=request.prompt,
        target_business_id=request.run_id,
    )
    return _running_response(
        skill_id="storyboard.plan",
        label=skill.label if skill else "Storyboard Skill",
        title="submit existing storyboard Sheng Cheng Ren Wu",
        detail="background through existing STORYBOARD_GENERATION Celery worker execute.",
        task=task,
        outputs={"script_id": script.id, "episode_id": script.episode_id},
        reuse_targets=skill.reuse_targets if skill else [],
        canvas_run_id=request.run_id,
    )


def _execute_timeline_pipeline(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    skill = skill_definition("timeline.assemble")
    script = load_script(db, user, request.script_id)
    if script is None:
        return blocked_result(
            request,
            title="Timeline Skill waiting script context",
            detail="need first Bang Ding script_id, Zhi Hou Cai will submit existing TIMELINE_PIPELINE Ren Wu.",
            required_inputs=["script_id"],
        )

    task = queue_timeline_pipeline_task(
        db,
        user,
        script,
        title=f"Sheng Chan Hua Bu Zhi Xing Timeline Skill - script{script.id}",
        description="Production canvas timeline.assemble skill dispatch",
        prompt=request.prompt,
        target_business_id=request.run_id,
    )
    return _running_response(
        skill_id="timeline.assemble",
        label=skill.label if skill else "Timeline Skill",
        title="submit existing time Xian Liu Shui Xian Ren Wu",
        detail="background through existing TIMELINE_PIPELINE Celery worker execute.",
        task=task,
        outputs={"script_id": script.id, "episode_id": script.episode_id},
        reuse_targets=skill.reuse_targets if skill else [],
        canvas_run_id=request.run_id,
    )


def _running_response(
    *,
    skill_id: str,
    label: str,
    title: str,
    detail: str,
    task,
    outputs: dict,
    reuse_targets: list,
    canvas_run_id: str | None,
) -> ProductionCanvasSkillExecuteResponse:
    return ProductionCanvasSkillExecuteResponse(
        task_id=task.id,
        task_status=task.status.value,
        skill_result=ProductionCanvasSkillResult(
            skill=skill_id,
            label=label,
            status="running",
            title=title,
            detail=detail,
            outputs={
                **outputs,
                "dispatched_task_id": task.id,
                "task_status": task.status.value,
                **({"canvas_run_id": canvas_run_id} if canvas_run_id else {}),
            },
            reuse_targets=reuse_targets,
        ),
    )


def execute_canvas_skill(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    if request.skill == "brief.compose":
        return execute_brief_compose(request)
    if request.skill == "asset.select":
        return execute_asset_selection(db, user, request)
    if request.skill == "virtual_ip.image":
        return execute_virtual_ip_image_generation(db, user, request)
    if request.skill == "environment.image":
        return execute_environment_image_generation(db, user, request)
    if request.skill == "script.generate":
        return _execute_script_generation(db, user, request)
    if request.skill == "storyboard.plan":
        return _execute_storyboard_generation(db, user, request)
    if request.skill == "image.candidates":
        return execute_storyboard_images(db, user, request)
    if request.skill == "video.candidates":
        return execute_storyboard_video_candidates(db, user, request)
    if request.skill == "timeline.assemble":
        return _execute_timeline_pipeline(db, user, request)
    if request.skill == "report.summarize":
        return execute_report_summary(db, user, request)

    return blocked_result(
        request,
        title=f"{request.skill} Zan Wei Jie Ru Zi Dong Zhi Xing",
        detail="current Skill Yi Deng Ji background Fu Yong target, Dan Hai missing Jie Ru clear Ren Wu Pai Fa Qi.",
        required_inputs=["dispatcher"],
    )
