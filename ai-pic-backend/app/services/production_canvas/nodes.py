from __future__ import annotations

from app.schemas.production_canvas import (
    ProductionCanvasPlanNode,
    ProductionCanvasSkillResult,
)


NODE_LAYOUT = {
    "brief.compose": (80, 360, 210, None, None),
    "asset.select": (340, 360, 240, "/virtual-ip", "check Zi Chan Xuan Ze"),
    "virtual_ip.image": (620, 360, 240, "/tasks", "Cha Kan IP Tu Ren Wu"),
    "environment.image": (900, 360, 240, "/tasks", "Cha Kan environment Tu Ren Wu"),
    "script.generate": (1180, 360, 240, "/stories", "Jin Ru story production"),
    "storyboard.plan": (1460, 360, 240, "/tasks", "Cha Kan storyboard Ren Wu"),
    "image.candidates": (1740, 360, 250, "/tasks", "Cha Kan image Ren Wu"),
    "video.candidates": (2020, 360, 250, "/tasks", "Cha Kan video Ren Wu"),
    "timeline.assemble": (2300, 360, 250, "/tasks", "Cha Kan time Xian Ren Wu"),
    "report.summarize": (2580, 360, 240, "/tasks", "Cha Kan Bao Gao evidence"),
}


def _node_id(skill_id: str) -> str:
    return f"skill-{skill_id.replace('.', '-')}"


def build_plan_nodes(
    skill_results: list[ProductionCanvasSkillResult],
) -> list[ProductionCanvasPlanNode]:
    nodes: list[ProductionCanvasPlanNode] = []
    for index, result in enumerate(skill_results):
        default_x = 80 + index * 280
        x, y, width, action_href, action_label = NODE_LAYOUT.get(
            result.skill,
            (default_x, 360, 240, None, None),
        )
        nodes.append(
            ProductionCanvasPlanNode(
                id=_node_id(result.skill),
                label=result.label,
                title=result.title,
                status=result.status,
                x=x,
                y=y,
                width=width,
                skill=result.skill,
                detail=result.detail,
                outputs=result.outputs,
                reuse_targets=result.reuse_targets,
                action_href=action_href,
                action_label=action_label,
            )
        )
    return nodes
