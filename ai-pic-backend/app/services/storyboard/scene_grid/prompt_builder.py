"""LLM prompt builders for scene grid sheets and grid-to-video generation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.schemas.storyboard_scene_grid import (
    SceneGridPromptModel,
    SceneGridVideoPromptModel,
)
from app.services.storyboard.dynamic_prompt.context_builder import (
    build_scene_context,
)
from app.services.storyboard.scene_grid.layout import SceneGridLayout
from app.utils.json_utils import extract_json_block

logger = get_logger("storyboard_scene_grid")

DEFAULT_CELL_DURATION = 1.2
MIN_VIDEO_SECONDS = 4
MAX_VIDEO_SECONDS = 15


async def build_sheet_prompt(
    script: Any,
    scene_number: int,
    frames: List[dict],
    ref_ctx: Any,
    *,
    layout: SceneGridLayout,
    aspect_ratio: str,
    style: Optional[str],
    has_character_refs: bool,
    has_environment_refs: bool,
    ai_manager: Any,
) -> Dict[str, Any]:
    """Build the grid sheet image prompt, preferring LLM with static fallback."""
    scene_context = build_scene_context(
        script,
        scene_number,
        ref_ctx,
        [str(f.get("description") or "") for f in frames],
        style=style,
    )
    frame_inputs = [
        {
            "shot_type": f.get("shot_type") or "",
            "camera_movement": f.get("camera_movement") or "",
            "composition": f.get("composition") or "",
            "duration": f.get("duration_seconds"),
            "description": str(f.get("description") or f.get("ai_prompt") or "")[:200],
        }
        for f in frames
    ]
    variables = {
        **scene_context,
        "frames": frame_inputs,
        "panel_count": layout.panel_count,
        "rows": layout.rows,
        "columns": layout.columns,
        "aspect_ratio": aspect_ratio,
        "has_character_refs": has_character_refs,
        "has_environment_refs": has_environment_refs,
    }
    if ai_manager is not None:
        parsed = await _generate_json(
            ai_manager,
            PromptTemplate.STORYBOARD_SCENE_GRID_PROMPT.value,
            variables,
            SceneGridPromptModel,
            "scene_grid_sheet_prompt",
        )
        if parsed is not None:
            return {
                "sheet_prompt": parsed.sheet_prompt,
                "cells": [cell.model_dump() for cell in parsed.cells],
                "prompt_source": "llm_dynamic",
            }
    return _fallback_sheet_prompt(scene_context, frame_inputs, layout, aspect_ratio)


async def build_video_prompt(
    script: Any,
    scene_number: int,
    cells: List[dict],
    ref_ctx: Any,
    *,
    total_duration: float,
    aspect_ratio: str,
    style: Optional[str],
    ai_manager: Any,
) -> Dict[str, Any]:
    """Build the grid-to-continuous-video prompt with static fallback."""
    scene_context = build_scene_context(
        script,
        scene_number,
        ref_ctx,
        [str(cell.get("caption") or "") for cell in cells],
        style=style,
    )
    variables = {
        **scene_context,
        "cells": cells,
        "total_duration": round(total_duration, 1),
        "aspect_ratio": aspect_ratio,
    }
    if ai_manager is not None:
        parsed = await _generate_json(
            ai_manager,
            PromptTemplate.STORYBOARD_SCENE_GRID_VIDEO_PROMPT.value,
            variables,
            SceneGridVideoPromptModel,
            "scene_grid_video_prompt",
        )
        if parsed is not None:
            return {
                "video_prompt": parsed.video_prompt,
                "prompt_source": "llm_dynamic",
            }
    return _fallback_video_prompt(scene_context, cells, total_duration, aspect_ratio)


def cell_durations(frames: List[dict], panel_count: int) -> List[float]:
    """Per-panel durations from frame durations, padded/cycled to panel_count."""
    durations: List[float] = []
    for frame in frames[:panel_count]:
        try:
            value = float(frame.get("duration_seconds") or DEFAULT_CELL_DURATION)
        except (TypeError, ValueError):
            value = DEFAULT_CELL_DURATION
        durations.append(max(0.5, value))
    while len(durations) < panel_count:
        durations.append(DEFAULT_CELL_DURATION)
    return durations


def clamp_total_duration(durations: List[float]) -> int:
    total = int(round(sum(durations)))
    return max(MIN_VIDEO_SECONDS, min(MAX_VIDEO_SECONDS, total))


async def _generate_json(
    ai_manager: Any,
    template_name: str,
    variables: Dict[str, Any],
    schema_model: Any,
    schema_name: str,
) -> Optional[Any]:
    prompt = prompt_manager.render_prompt(template_name, variables)
    system_prompt = prompt_manager.render_prompt(
        PromptTemplate.SYSTEM_PROMPT_JSON_STRICT.value, {}
    )
    for attempt in range(2):
        try:
            response = await ai_manager.generate_text(
                prompt=prompt,
                temperature=0.5,
                model=settings.STORYBOARD_DYNAMIC_PROMPT_MODEL,
                json_schema={
                    "name": schema_name,
                    "schema": schema_model.model_json_schema(),
                },
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.warning("%s LLM call failed (attempt %s): %s", schema_name, attempt + 1, exc)
            continue
        if not getattr(response, "success", False):
            continue
        content = response.data if isinstance(response.data, str) else str(response.data)
        normalized = extract_json_block(content)
        if not normalized:
            continue
        try:
            return schema_model.model_validate(normalized)
        except Exception:
            logger.warning("%s JSON invalid (attempt %s)", schema_name, attempt + 1)
    return None


def _fallback_sheet_prompt(
    scene_context: Dict[str, Any],
    frame_inputs: List[Dict[str, Any]],
    layout: SceneGridLayout,
    aspect_ratio: str,
) -> Dict[str, Any]:
    scene = scene_context.get("scene") or {}
    cells = []
    lines = []
    for index in range(1, layout.panel_count + 1):
        frame = frame_inputs[(index - 1) % max(1, len(frame_inputs))] if frame_inputs else {}
        description = str(frame.get("description") or f"Jing Tou{index}")
        title = description[:6] or f"Jing Tou{index}"
        cells.append({"panel_index": index, "title": title, "caption": title})
        lines.append(
            f"{index:02d}｜{title}：{frame.get('shot_type') or 'medium shot'}，{description}。"
            f"Shuo Ming Lan Wen Zi Xie：“{title}”。"
        )
    characters = scene_context.get("characters") or []
    char_lines = "；".join(f"{c['name']}：{c['appearance']}" for c in characters)
    sheet_prompt = "\n".join(
        [
            f"generate Yi Zhang Heng Xiang {aspect_ratio} De Gao Wan Cheng Du Zhong Wen{layout.panel_count}Gong Ge Dong Zuo Fen Jing Tu。",
            "[Zheng Ti Ding Wei]film Ji Xie Shi Fen Jing Ban, You Zhen Shi film Ju Zhao Zu Cheng, Bu Shi Su Miao Cao Tu, Ka Tong or Cha Hua, Shi He Zuo Wei AI video Sheng Cheng reference Tu.",
            f"【Zheng Ti Ban Shi】{layout.rows} Xing × {layout.columns} Lie Gong {layout.panel_count} Ge；"
            "Mei Ge Zuo Shang Jiao has Hei Di Bai Zi Cu Ti ID; Mei Ge Xia Fang has Bai Se note Lan Xie Zhong Wen shot name.",
            f"【scene She Ding】Gu Ding Zai Tong Yi Kong Jian：{scene.get('location') or 'Tong Yi scene'}，"
            f"{scene.get('time') or ''}；{scene.get('description') or ''}；scene Bu De Qie Huan。",
            f"【Zhu Jiao She Ding】{char_lines or 'character Wai Mao Quan Tu Bao Chi Yi Zhi'}。",
            "[shot content]",
            *lines,
            "[frame requirement]Mei Ge only a shot Shun Jian; Chu ID and note Lan Wai frame interior Bu De Chu Xian Qi Ta Wen Zi, Zi Mu, Shui Yin, logo; "
            "Jing Bie Ji Wei Zhu Ge change, Xiang Lin Ge keep action Lian Xu Gan.",
        ]
    )
    return {"sheet_prompt": sheet_prompt, "cells": cells, "prompt_source": "fallback"}


def _fallback_video_prompt(
    scene_context: Dict[str, Any],
    cells: List[dict],
    total_duration: float,
    aspect_ratio: str,
) -> Dict[str, Any]:
    characters = scene_context.get("characters") or []
    char_lines = "；".join(f"{c['name']}：{c['appearance']}" for c in characters)
    shot_lines = [
        f"Jing Tou{cell.get('panel_index')}（Yue{cell.get('duration') or DEFAULT_CELL_DURATION}Miao）："
        f"{cell.get('caption') or cell.get('title') or ''}"
        for cell in cells
    ]
    video_prompt = "\n".join(
        [
            "Shi Yong input storyboard Tu Zuo Wei action storyboard reference.strict reference Qi Zhong shot Shun Xu, action Luo Ji, character Diao Du and Jie Zou advance, "
            "Dan Zui Zhong output Bi Xu Shi complete Lian Xu film frame, Bu De Chu Xian storyboard Ge Zi, ID, note Lan, Wen Zi, Bian Kuang or Zhi Zhang background.",
            f"【Zheng Ti Feng Ge】Dian Ying Ji Xie Shi Zhi Gan，Zong Shi Zhang Yue {round(total_duration, 1)} Miao，Hua Fu {aspect_ratio}。",
            f"【Zhu Jiao She Ding】{char_lines or 'Quan Pian character Mian Bu, Fu Zhuang, Ti Xing Bao Chi Yi Zhi'}。",
            "[shot and content She Ji]",
            *shot_lines,
            "[frame requirement]shot has Ming Xian Jing Bie and Ji Wei change, action Lian Guan Zi Ran, Bu De Chu Xian any Wen Zi and Shui Yin.",
        ]
    )
    return {"video_prompt": video_prompt, "prompt_source": "fallback"}
