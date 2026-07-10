"""Opening-hook substance checks for provider-chain script scoring."""

from __future__ import annotations

from typing import Any

_HOOK_MARKERS = (
    "anomaly",
    "alert",
    "alarm",
    "warning",
    "countdown",
    "zeroed out",
    "reset to zero",
    "deleted",
    "lost",
    "lose",
    "rejected",
    "locked",
    "frozen",
    "error",
    "failed",
    "crisis",
    "threat",
    "shadow",
    "evidence",
    "ID",
    "truth",
    "reversal",
    "final",
    "must",
    "who",
    "cannot",
    "stop",
    "grab",
    "changed",
    "was changed",
    "reused",
    "same image",
    "identical",
    "hidden marker",
    "blank",
    "missing",
    "lacking",
    "no hook",
    "won't pay",
    "payment refused",
    "rejected",
    "gone dark",
    "leaving",
)


def opening_hook_failed_checks(scenes: list[dict[str, Any]]) -> list[str]:
    if not scenes:
        return []

    beats = scenes[0].get("beats") if isinstance(scenes[0].get("beats"), list) else []
    first_beat = beats[0] if beats and isinstance(beats[0], dict) else None
    if not first_beat or first_beat.get("beat_type") != "hook":
        return []

    screen_text = _opening_screen_text(first_beat)
    if any(marker in screen_text for marker in _HOOK_MARKERS):
        return []
    return ["opening_hook_substance"]


def _opening_screen_text(beat: dict[str, Any]) -> str:
    parts = [str(beat.get("visible_event") or "")]
    actions = beat.get("action") or beat.get("action_lines") or []
    if isinstance(actions, list):
        for item in actions:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("content") or ""))
    dialogue = beat.get("dialogue") or beat.get("dialogue_lines") or []
    if isinstance(dialogue, list):
        for line in dialogue:
            if isinstance(line, dict):
                parts.append(str(line.get("line") or line.get("content") or ""))
    return _compact_text("".join(parts))


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
