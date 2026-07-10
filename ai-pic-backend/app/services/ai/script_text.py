from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.ai.commercial_script_text import build_commercial_vertical_text


def build_script_text(
    scenes: List[Dict[str, Any]],
    dialogues: List[Dict[str, Any]],
    stage_directions: List[Dict[str, Any]],
    format_type: str,
    language: str,
    *,
    episode_number: Optional[int] = None,
    template_style: Optional[str] = None,
    target_chars_per_episode: Optional[int] = None,
    title: Optional[str] = None,
) -> str:
    if _uses_commercial_vertical_template(format_type, template_style):
        return build_commercial_vertical_text(
            scenes=scenes,
            dialogues=dialogues,
            stage_directions=stage_directions,
            episode_number=episode_number or 1,
            target_chars_per_episode=target_chars_per_episode,
            title=title,
        )

    lines: List[str] = [
        f"# {format_type} ({language})",
        "[sound effect]Peng!frame directly Qie Ru conflict Xian Chang.",
    ]
    if scenes:
        lines.append("## scene")
        for scene in scenes:
            scene_no = scene.get("scene_number") or "-"
            slug = scene.get("slug_line") or f"Scene {scene.get('scene_number')}"
            summary = scene.get("summary") or scene.get("description") or ""
            lines.append(f"- [场景 {scene_no}] {slug}: {summary}")
            if summary:
                lines.append(f"【快】【情绪目的：推进冲突】{summary}")
    if dialogues:
        lines.append("\n## dialogue")
        for dialogue in dialogues[:200]:
            scene_no = dialogue.get("scene_number") or "-"
            character = dialogue.get("character") or "narration"
            content = (
                dialogue.get("content")
                or dialogue.get("line")
                or dialogue.get("text")
                or ""
            )
            lines.append(f"[场景 {scene_no}] {character}: {content}")
    if stage_directions:
        lines.append("\n## Wu Tai Zhi Shi")
        for direction in stage_directions[:200]:
            scene_no = direction.get("scene_number") or "-"
            content = (
                direction.get("content")
                or direction.get("direction")
                or direction.get("description")
                or ""
            )
            timing = direction.get("timing") or ""
            lines.append(f"[场景 {scene_no}][{timing}] {content}")
    if not _ends_with_question(lines):
        lines.append(
            "[Man][EmotionMu Di: Liu Xia suspense]shot Ting inKey clueon: Jie Xia Lai will Fa Sheng Shen Me?"
        )
    return "\n".join(lines)


def _uses_commercial_vertical_template(
    format_type: str, template_style: Optional[str]
) -> bool:
    return template_style == "commercial_vertical_drama" or format_type in {
        "commercial_vertical_drama",
        "vertical_short_drama",
    }


def _ends_with_question(lines: List[str]) -> bool:
    for line in reversed(lines):
        text = line.strip()
        if text:
            return "?" in text or "？" in text
    return False
