from __future__ import annotations

from app.schemas.production_canvas import (
    CanvasNodeStatus,
    ProductionCanvasPlanRequest,
    ProductionCanvasSkillResult,
)
from app.services.production_canvas.asset_selection import CanvasAssetSelection
from app.services.production_canvas.skills import list_canvas_skill_definitions


def _asset_names(assets) -> str:
    return "、".join(asset.name for asset in assets)


def _asset_title(selection: CanvasAssetSelection) -> str:
    ip_names = _asset_names(selection.selected.virtual_ips)
    env_names = _asset_names(selection.selected.environments)
    if ip_names and env_names:
        return f"Yi Xuan Ze {ip_names} He {env_names}"
    if ip_names:
        return f"Yi Xuan Ze IP：{ip_names}；Huan Jing Dai Que Ren"
    if env_names:
        return f"IP Dai Que Ren；Yi Xuan Ze Huan Jing：{env_names}"
    return "pending Que Ren IP and environment Zi Chan"


def _asset_detail(selection: CanvasAssetSelection) -> str:
    ip_names = _asset_names(selection.selected.virtual_ips) or "pending Xuan Ze IP"
    env_names = _asset_names(selection.selected.environments) or "pending Xuan Ze environment"
    return f"Fu Yong Xian You IP：{ip_names}；Huan Jing：{env_names}"


def _asset_status(selection: CanvasAssetSelection) -> CanvasNodeStatus:
    if selection.selected.virtual_ips or selection.selected.environments:
        return "review"
    return "blocked"


def _downstream_status(
    request: ProductionCanvasPlanRequest,
    selection: CanvasAssetSelection,
    skill_id: str,
) -> CanvasNodeStatus:
    if skill_id == "virtual_ip.image" and selection.selected.virtual_ips:
        return "ready"
    if skill_id == "environment.image" and selection.selected.environments:
        return "ready"
    if skill_id == "script.generate" and request.episode_id:
        return "ready"
    if (
        skill_id
        in {
            "storyboard.plan",
            "image.candidates",
            "video.candidates",
            "timeline.assemble",
        }
        and request.script_id
    ):
        return "ready"
    if skill_id == "report.summarize" and request.task_id:
        return "ready"
    return "blocked"


def _downstream_outputs(
    request: ProductionCanvasPlanRequest,
    selection: CanvasAssetSelection,
) -> dict:
    outputs = dict(selection.outputs())
    if request.episode_id:
        outputs["episode_id"] = request.episode_id
    if request.script_id:
        outputs["script_id"] = request.script_id
    if request.task_id:
        outputs["task_id"] = request.task_id
    return outputs


def _required_inputs(
    request: ProductionCanvasPlanRequest,
    selection: CanvasAssetSelection,
    skill_id: str,
) -> list[str]:
    if skill_id == "virtual_ip.image" and not selection.selected.virtual_ips:
        return ["virtual_ip_id"]
    if skill_id == "environment.image" and not selection.selected.environments:
        return ["environment_id"]
    if skill_id == "script.generate" and request.episode_id is None:
        return ["episode_id"]
    if (
        skill_id
        in {
            "storyboard.plan",
            "image.candidates",
            "video.candidates",
            "timeline.assemble",
        }
        and request.script_id is None
    ):
        return ["script_id"]
    if skill_id == "report.summarize" and request.task_id is None:
        return ["task_id"]
    return []


def _downstream_detail(
    request: ProductionCanvasPlanRequest,
    selection: CanvasAssetSelection,
    skill_id: str,
) -> str:
    if not _required_inputs(request, selection, skill_id):
        return "background Fu Yong existing API, service or worker; Qian Duan only Zhan Shi execute Jie Guo."
    return "need first Bu Qi execute context, Zhi Hou Cai will call existing Sheng Cheng API, service or worker."


def build_canvas_skill_results(
    request: ProductionCanvasPlanRequest,
    selection: CanvasAssetSelection,
) -> list[ProductionCanvasSkillResult]:
    asset_outputs = selection.outputs()
    downstream_outputs = _downstream_outputs(request, selection)
    results: list[ProductionCanvasSkillResult] = []
    for skill in list_canvas_skill_definitions():
        if skill.id == "brief.compose":
            results.append(
                ProductionCanvasSkillResult(
                    skill=skill.id,
                    label=skill.label,
                    status="ready",
                    title="Cong Liao Tian target Sheng Cheng production brief",
                    detail=f"Mu Biao：{request.prompt}",
                    outputs={"prompt": request.prompt},
                    reuse_targets=skill.reuse_targets,
                )
            )
            continue
        if skill.id == "asset.select":
            results.append(
                ProductionCanvasSkillResult(
                    skill=skill.id,
                    label=skill.label,
                    status=_asset_status(selection),
                    title=_asset_title(selection),
                    detail=_asset_detail(selection),
                    outputs=asset_outputs,
                    reuse_targets=skill.reuse_targets,
                )
            )
            continue
        outputs = dict(downstream_outputs)
        required_inputs = _required_inputs(request, selection, skill.id)
        if required_inputs:
            outputs["required_inputs"] = required_inputs
        results.append(
            ProductionCanvasSkillResult(
                skill=skill.id,
                label=skill.label,
                status=_downstream_status(request, selection, skill.id),
                title=skill.description,
                detail=_downstream_detail(request, selection, skill.id),
                outputs=outputs,
                reuse_targets=skill.reuse_targets,
            )
        )
    return results
