"""Dramatic-purpose checks for provider-chain script scoring."""

from __future__ import annotations

from typing import Any

_VAGUE_PURPOSE_PHRASES = (
    "advancing the plot",
    "driving the plot",
    "story continues",
    "setting up the plot",
    "creating suspense",
    "leaving suspense",
    "creating conflict",
    "driving conflict",
    "escalating conflict",
    "plot twist",
    "reversal occurs",
    "twist complete",
    "transitional",
    "emotional change",
    "relationship changes",
)


def purpose_failed_checks(scenes: list[dict[str, Any]]) -> list[str]:
    failed: list[str] = []
    for scene in scenes:
        beats = scene.get("beats")
        if not isinstance(beats, list):
            continue
        for beat in beats:
            if not isinstance(beat, dict):
                continue
            purpose = _compact_text(str(beat.get("dramatic_purpose") or ""))
            if len(purpose) < 4 or purpose in _VAGUE_PURPOSE_PHRASES:
                failed.append("beat_dramatic_purpose_specificity")
    return failed


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
