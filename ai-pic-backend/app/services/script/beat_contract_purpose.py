from __future__ import annotations

from typing import Any

_VAGUE_PURPOSE_PHRASES = (
    "advance plot",
    "drive plot",
    "story continue",
    "Foreshadowingplot",
    "Zhi Zao Xuan Nian",
    "Liu Xia suspense",
    "Zhi Zao conflict",
    "drive conflict",
    "escalate conflict",
    "Chu Xian Zhuan Zhe",
    "Fa Sheng twist",
    "complete Zhuan Zhe",
    "Cheng Shang Qi Xia",
    "Emotionchange",
    "relationship change",
)


def purpose_issues(scene: Any) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for beat in scene.beats:
        purpose = _compact_text(beat.dramatic_purpose)
        if _visible_len(purpose) < 4 or any(
            phrase in purpose for phrase in _VAGUE_PURPOSE_PHRASES
        ):
            issues.append(
                {
                    "check_id": "beat_dramatic_purpose_specificity",
                    "message": "beat dramatic purpose must name a concrete story turn",
                    "scene_number": scene.scene_number,
                    "beat_order_index": beat.order_index,
                    "evidence": {"dramatic_purpose": beat.dramatic_purpose},
                }
            )
    return issues


def _visible_len(text: str) -> int:
    return len("".join(ch for ch in text if not ch.isspace()))


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
