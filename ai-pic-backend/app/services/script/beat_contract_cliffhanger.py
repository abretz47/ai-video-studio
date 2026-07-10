from __future__ import annotations

from typing import Any

from app.services.script.beat_contract_specificity import (
    is_cliffhanger_beat,
    is_specific_text,
)

_RESOLVED_ENDING_PHRASES = (
    "Ren Wu complete",
    "Quan Bu Xi Mie",
    "Quan Bu Hui Fu",
    "Hui Fu Zheng Chang",
    "crisis Jie Chu",
    "Zhen Xiang Da Bai",
    "Yuan Man Jie Shu",
    "An Quan Li Kai",
    "successful Na Hui",
    "Na Hui Quan Bu",
    "Jiang Jin Quan Na Hui",
    "Quan Bu Jiang Jin",
)

_UNRESOLVED_THREAT_CUES = (
    "Shui",
    "Hai",
    "Que",
    "Tu Ran",
    "countdown",
    "delete",
    "Xiao Shi",
    "shadow",
    "Mo Sheng",
    "unknown",
    "Xin",
    "Men Kai",
    "Wei Jie",
)


def cliffhanger_issues(beat: Any, scene_number: int) -> list[dict[str, Any]]:
    if not is_cliffhanger_beat(beat):
        return []

    issues: list[dict[str, Any]] = []
    if not _has_specific_cliffhanger(beat):
        issues.append(
            {
                "check_id": "cliffhanger_specificity",
                "message": "cliffhanger beat must leave a concrete unresolved threat",
                "scene_number": scene_number,
                "beat_order_index": beat.order_index,
                "evidence": {
                    "visible_event": beat.visible_event,
                    "cliffhanger_tag": beat.cliffhanger_tag,
                },
            }
        )
    if _looks_resolved_without_threat(beat):
        issues.append(
            {
                "check_id": "cliffhanger_unresolved_threat",
                "message": "cliffhanger beat must not fully resolve the story",
                "scene_number": scene_number,
                "beat_order_index": beat.order_index,
                "evidence": {
                    "visible_event": beat.visible_event,
                    "cliffhanger_tag": beat.cliffhanger_tag,
                },
            }
        )
    return issues


def _looks_resolved_without_threat(beat: Any) -> bool:
    text = _compact_text(
        " ".join(
            [
                beat.visible_event,
                beat.cliffhanger_tag or "",
                *[action.content for action in beat.action_lines],
                *[line.content for line in beat.dialogue_lines],
            ]
        )
    )
    has_resolution = any(phrase in text for phrase in _RESOLVED_ENDING_PHRASES)
    has_unresolved_cue = any(phrase in text for phrase in _UNRESOLVED_THREAT_CUES)
    return has_resolution and not has_unresolved_cue


def _has_specific_cliffhanger(beat: Any) -> bool:
    return is_specific_text(
        " ".join(
            [
                beat.visible_event,
                beat.cliffhanger_tag or "",
                *[action.content for action in beat.action_lines],
            ]
        )
    )


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
