"""Final-cliffhanger checks for provider-chain script scoring."""

from __future__ import annotations

from typing import Any

_RESOLVED_ENDING_PHRASES = (
    "task complete",
    "all extinguished",
    "all restored",
    "back to normal",
    "crisis resolved",
    "truth revealed",
    "happy ending",
    "safely departed",
    "successfully recovered",
    "recovered everything",
    "all bonuses recovered",
    "full bonus",
)

_TERMINAL_FAILURE_PHRASES = (
    "data lost",
    "logs lost",
    "deletion complete",
    "already deleted",
    "command executed",
    "executed",
    "too late",
    "progress bar at 100%",
    "at 100%",
    "complete failure",
)

_UNRESOLVED_THREAT_CUES = (
    "who",
    "still",
    "yet",
    "suddenly",
    "countdown",
    "delete",
    "disappear",
    "shadow",
    "stranger",
    "unknown",
    "new",
    "door opens",
    "unresolved",
)


def cliffhanger_failed_checks(scenes: list[dict[str, Any]]) -> list[str]:
    final_beats = _scene_beats(scenes[-1]) if scenes else []
    if not final_beats:
        return []
    final_beat = final_beats[-1]
    if _looks_resolved_without_threat(final_beat):
        return ["cliffhanger_unresolved_threat"]
    return []


def _looks_resolved_without_threat(beat: dict[str, Any]) -> bool:
    text = _compact_text(
        " ".join(
            [
                str(beat.get("visible_event") or ""),
                str(beat.get("cliffhanger_tag") or ""),
                *_beat_action_lines(beat),
                *[
                    str(line.get("line") or line.get("content") or "")
                    for line in _beat_dialogue_lines(beat)
                ],
            ]
        )
    )
    has_resolution = any(phrase in text for phrase in _RESOLVED_ENDING_PHRASES)
    has_terminal_failure = any(phrase in text for phrase in _TERMINAL_FAILURE_PHRASES)
    has_unresolved_cue = any(phrase in text for phrase in _UNRESOLVED_THREAT_CUES)
    return has_terminal_failure or (has_resolution and not has_unresolved_cue)


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())


def _scene_beats(scene: dict[str, Any]) -> list[dict[str, Any]]:
    beats = scene.get("beats")
    if not isinstance(beats, list):
        return []
    return [beat for beat in beats if isinstance(beat, dict)]


def _beat_action_lines(beat: dict[str, Any]) -> list[str]:
    actions = beat.get("action") or beat.get("action_lines") or []
    if not isinstance(actions, list):
        return []
    texts: list[str] = []
    for item in actions:
        if isinstance(item, str):
            texts.append(item)
        elif isinstance(item, dict) and item.get("content"):
            texts.append(str(item["content"]))
    return texts


def _beat_dialogue_lines(beat: dict[str, Any]) -> list[dict[str, Any]]:
    dialogue = beat.get("dialogue") or beat.get("dialogue_lines") or []
    if not isinstance(dialogue, list):
        return []
    return [line for line in dialogue if isinstance(line, dict)]
