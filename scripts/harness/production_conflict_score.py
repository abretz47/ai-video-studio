"""Scene conflict checks for provider-chain script scoring."""

from __future__ import annotations

from typing import Any

_VAGUE_CONFLICT_PHRASES = (
    "advancing the plot",
    "driving the plot",
    "plot continues",
    "story continues",
    "creating suspense",
    "leaving suspense",
    "creating conflict",
    "driving conflict",
    "escalating conflict",
    "plot twist",
    "reversal occurs",
    "twist complete",
    "relationship changes",
    "emotional change",
)

_STAKES_MARKERS = (
    "second",
    "minute",
    "hour",
    "countdown",
    "zeroed out",
    "reset to zero",
    "lost",
    "deleted",
    "permanent",
    "bonus",
    "contract",
    "client",
    "acceptance",
    "release",
    "go live",
    "evidence",
    "file",
    "log",
    "permission",
    "asset",
    "video",
    "audio",
    "order",
    "invoice",
    "deduction",
    "compensation",
    "balance",
    "alarm",
    "alert",
    "outage",
    "ban",
    "locked",
)

_OPPOSITION_MARKERS = (
    "system",
    "permission",
    "shadow",
    "client",
    "teammate",
    "supplier",
    "backend",
    "review",
    "log",
    "console",
    "countdown",
    "alert",
    "lock",
    "rejected",
    "deleted",
    "tampered",
    "banned",
    "screen",
    "file",
    "interface",
    "callback",
    "invoice",
    "model",
    "asset",
    "boss",
    "reviewer",
    "insider",
    "modifier",
    "operator",
    "intruder",
)


def conflict_failed_checks(scenes: list[dict[str, Any]]) -> list[str]:
    failed: list[str] = []
    for scene in scenes:
        if not _is_specific_text(_scene_field(scene, "question")):
            failed.append("scene_conflict_question")
        if not _has_marker(_scene_field(scene, "stakes"), _STAKES_MARKERS):
            failed.append("scene_conflict_stakes")
        if not _has_marker(_scene_field(scene, "opposition"), _OPPOSITION_MARKERS):
            failed.append("scene_conflict_opposition")
        if not _is_specific_text(_scene_field(scene, "turn")):
            failed.append("scene_conflict_turn")
    return failed


def _scene_field(scene: dict[str, Any], field: str) -> str:
    value = scene.get(field)
    if value:
        return str(value)
    conflict = scene.get("conflict")
    if isinstance(conflict, dict):
        return str(conflict.get(field) or "")
    return ""


def _is_specific_text(value: str) -> bool:
    text = _compact_text(value)
    if len(text) < 4:
        return False
    return not any(phrase in text for phrase in _VAGUE_CONFLICT_PHRASES)


def _compact_text(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())


def _has_marker(text: str, markers: tuple[str, ...]) -> bool:
    compacted = _compact_text(text)
    return any(marker in compacted for marker in markers)
