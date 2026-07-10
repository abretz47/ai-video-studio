from __future__ import annotations

import json
from collections import Counter

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.video_generation_task_repository import (
    VideoGenerationTaskRepository,
)
from app.schemas.production_canvas import (
    ProductionCanvasSkillExecuteRequest,
    ProductionCanvasSkillExecuteResponse,
    ProductionCanvasSkillResult,
)
from app.services.production_canvas.execution_common import (
    blocked_result,
    decode_parameters,
    load_task,
    skill_definition,
)
from app.services.production_canvas.run_persistence import load_canvas_skill_run


def _int_output(outputs: dict, key: str) -> int | None:
    value = outputs.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _execution_task_ids(nodes) -> list[int]:
    task_ids = set()
    for node in nodes:
        outputs = getattr(node, "outputs", {}) or {}
        for key in ("dispatched_task_id", "task_id"):
            task_id = _int_output(outputs, key)
            if task_id:
                task_ids.add(task_id)
    return sorted(task_ids)


def _dict_from_json(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _string_value(value) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _provider_from_model(model: str | None) -> str | None:
    if not model or ":" not in model:
        return None
    provider, _ = model.split(":", 1)
    return provider or None


def _merge_numeric_counts(target: dict[str, float], source: dict | None) -> None:
    if not isinstance(source, dict):
        return
    for key, value in source.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            target[key] = target.get(key, 0) + value


def _media_task_lineage(db: Session, user: User, task_ids: list[int]) -> dict:
    video_repo = VideoGenerationTaskRepository(db)
    provider_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    usage_totals: dict[str, float] = {}
    tasks = []
    for task_id in task_ids:
        task = load_task(db, user, task_id)
        if task is None:
            continue
        params = decode_parameters(task.parameters)
        requested_model = _string_value(params.get("model"))
        requested_provider = _provider_from_model(requested_model)
        provider_tasks = []
        for item in video_repo.list_by_task_id(task.id):
            result = _dict_from_json(item.result)
            metadata = item.generation_metadata if isinstance(item.generation_metadata, dict) else {}
            provider = (
                _string_value(result.get("provider_used"))
                or _string_value(metadata.get("provider"))
                or item.provider
            )
            model = (
                _string_value(result.get("model_used"))
                or _string_value(metadata.get("model"))
                or item.model
            )
            usage = result.get("usage") if isinstance(result.get("usage"), dict) else None
            if usage is None and isinstance(metadata.get("usage"), dict):
                usage = metadata.get("usage")
            if provider:
                provider_counts[provider] += 1
            if model:
                model_counts[model] += 1
            _merge_numeric_counts(usage_totals, usage)
            provider_tasks.append(
                {
                    "video_generation_task_id": item.id,
                    "provider": provider,
                    "provider_task_id": item.provider_task_id,
                    "model": model,
                    "model_type": item.model_type,
                    "status": item.status.value,
                    "frame_index": item.frame_index,
                    "usage": usage or {},
                    "cost": result.get("cost") or metadata.get("cost"),
                    "error_message": item.error_message,
                }
            )
        tasks.append(
            {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "task_status": task.status.value,
                "requested_model": requested_model,
                "requested_provider": requested_provider,
                "frame_indexes": params.get("frame_indexes")
                if isinstance(params.get("frame_indexes"), list)
                else None,
                "result_file_path": task.result_file_path,
                "error_message": task.error_message,
                "provider_tasks": provider_tasks,
            }
        )
    return {
        "task_lineage": tasks,
        "provider_counts": dict(provider_counts),
        "model_counts": dict(model_counts),
        "usage_totals": usage_totals,
    }


def _report_run_summary(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse | None:
    if not request.run_id:
        return None
    run = load_canvas_skill_run(db, user, request.run_id)
    if run is None:
        return None

    skill = skill_definition("report.summarize")
    saved = run.saved_state
    nodes = saved.nodes if saved and saved.nodes else run.nodes
    edge_count = len(saved.edges) if saved else 0
    task = load_task(db, user, run.task_id)
    task_ids = _execution_task_ids(nodes)
    lineage = _media_task_lineage(db, user, task_ids)
    return ProductionCanvasSkillExecuteResponse(
        task_id=task.id if task else run.task_id,
        task_status=task.status.value if task else None,
        skill_result=ProductionCanvasSkillResult(
            skill="report.summarize",
            label=skill.label if skill else "Report Skill",
            status="review",
            title="Hui Zong Hua Bu execute evidence",
            detail=(
                f"Hua Bu run {run.run_id} Yi Hui Zong {len(nodes)} Ge Jie Dian、"
                f"{edge_count} Tiao Lian Xian He {len(task_ids)} Ge task Zheng Ju。"
            ),
            outputs={
                "report_source": "production_canvas_run",
                "canvas_run_id": run.run_id,
                "canvas_task_id": run.task_id,
                "node_count": len(nodes),
                "edge_count": edge_count,
                "status_counts": dict(Counter(node.status for node in nodes)),
                "execution_task_ids": task_ids,
                **lineage,
                "selected_node_id": saved.selected_node_id if saved else None,
                "saved_state_present": saved is not None,
            },
            reuse_targets=skill.reuse_targets if skill else [],
        ),
    )


def execute_report_summary(
    db: Session,
    user: User,
    request: ProductionCanvasSkillExecuteRequest,
) -> ProductionCanvasSkillExecuteResponse:
    skill = skill_definition("report.summarize")
    run_summary = _report_run_summary(db, user, request)
    if run_summary is not None:
        return run_summary

    task = load_task(db, user, request.task_id)
    if task is None:
        return blocked_result(
            request,
            title="Report Skill waiting Ren Wu evidence",
            detail="need first Bang Ding can access task_id, Zhi Hou Cai will Hui Zong existing Ren Wu evidence.",
            required_inputs=["task_id"],
        )

    params = decode_parameters(task.parameters)
    lineage = _media_task_lineage(db, user, [task.id])
    source_kind = params.get("kind") if isinstance(params.get("kind"), str) else None
    canvas_run_id = request.run_id or task.target_business_id
    if not canvas_run_id and source_kind == "production_canvas_run":
        canvas_run_id = task.business_id
    return ProductionCanvasSkillExecuteResponse(
        task_id=task.id,
        task_status=task.status.value,
        skill_result=ProductionCanvasSkillResult(
            skill="report.summarize",
            label=skill.label if skill else "Report Skill",
            status="review",
            title="Hui Zong existing Ren Wu evidence",
            detail=(
                f"task #{task.id}《{task.title}》Dang Qian status {task.status.value}；"
                "can continue in Ren Wu Ye check parameters, failed Xin Xi and Chan Wu path."
            ),
            outputs={
                "task_id": task.id,
                "task_business_id": task.business_id,
                "task_type": task.task_type.value,
                "task_status": task.status.value,
                "source_kind": source_kind,
                "canvas_run_id": canvas_run_id,
                "result_file_path": task.result_file_path,
                "error_message": task.error_message,
                "parameter_keys": sorted(params.keys()),
                **lineage,
            },
            reuse_targets=skill.reuse_targets if skill else [],
        ),
    )
