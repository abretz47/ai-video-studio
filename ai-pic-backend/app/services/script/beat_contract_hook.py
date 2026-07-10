from __future__ import annotations

from typing import Any

_HOOK_MARKERS = (
    "exception",
    "alarm",
    "Bao Jing",
    "countdown",
    "Qing Ling",
    "Gui Ling",
    "delete",
    "Diu Shi",
    "Shi Qu",
    "Ju Jue",
    "lock",
    "Dong Jie",
    "error",
    "failed",
    "crisis",
    "threat",
    "shadow",
    "evidence",
    "ID",
    "truth",
    "twist",
    "Zui Hou",
    "Bi Xu",
    "Shui",
    "cannot",
    "Zu Zhi",
    "Qiang",
    "Gai",
    "Gai Le",
)


def opening_hook_issues(scene: Any) -> list[dict[str, Any]]:
    if scene.scene_number != 1 or not scene.beats:
        return []

    beat = scene.beats[0]
    if beat.beat_type != "hook":
        return []

    screen_text = _opening_screen_text(beat)
    if any(marker in screen_text for marker in _HOOK_MARKERS):
        return []

    return [
        {
            "check_id": "opening_hook_substance",
            "message": "opening hook must show an immediate threat or reversal",
            "scene_number": scene.scene_number,
            "beat_order_index": beat.order_index,
            "evidence": {"screen_text": screen_text},
        }
    ]


def _opening_screen_text(beat: Any) -> str:
    parts = [
        beat.visible_event,
        *[action.content for action in beat.action_lines],
        *[line.content for line in beat.dialogue_lines],
    ]
    return _compact_text("".join(parts))


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
