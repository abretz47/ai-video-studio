"""TTS emotion normalization helpers."""

from __future__ import annotations

from typing import Sequence

ALLOWED_TTS_EMOTIONS = {
    "happy",
    "sad",
    "angry",
    "fearful",
    "disgusted",
    "surprised",
    "calm",
    "fluent",
    "whisper",
}


def normalize_tts_emotion(
    emotion: str | None,
    *,
    action: str | None = None,
) -> str | None:
    """Normalize emotion string to allowed TTS emotion labels."""
    if not emotion and not action:
        return None

    raw = " ".join(
        v.strip()
        for v in [emotion or "", action or ""]
        if isinstance(v, str) and v.strip()
    )
    if not raw:
        return None

    raw_lower = raw.lower()

    if isinstance(emotion, str) and emotion.strip().lower() in ALLOWED_TTS_EMOTIONS:
        return emotion.strip().lower()

    def _has_any(tokens: Sequence[str]) -> bool:
        return any(tok in raw_lower for tok in tokens)

    if _has_any(
        ["whisper", "Di Yu", "Er Yu", "Ya Di", "Xiao Sheng", "Qiao Sheng", "Qing Sheng", "Di Sheng", "Zi Yu"]
    ):
        return "whisper"
    if _has_any(["angry", "angry", "angry", "Nao Huo", "Nu", "Huo Da", "Bao Zao"]):
        return "angry"
    if _has_any(
        [
            "sad",
            "sad",
            "sad",
            "frustrated",
            "Geng Ye",
            "Ku",
            "sad",
            "Tan Qi",
            "Tan Kou Qi",
            "Tan Yi Kou Qi",
            "Tan Xi",
            "Chang Tan",
        ]
    ):
        return "sad"
    if _has_any(["happy", "happy", "happy", "joy", "excited", "excited", "Huan Kuai", "pleasant"]):
        return "happy"
    if _has_any(["surprised", "surprised", "Chi Jing", "shocked", "Jing"]):
        return "surprised"
    if _has_any(["fearful", "afraid", "fear", "tense", "Huang", "Dan Xin", "anxious", "Wei Ju"]):
        return "fearful"
    if _has_any(["disgusted", "Yan Wu", "E Xin", "Fan Gan"]):
        return "disgusted"
    if _has_any(
        [
            "calm",
            "neutral",
            "thoughtful",
            "calm",
            "calm",
            "Zhong Xing",
            "Chen Wen",
            "Yan Su",
            "thoughtful",
            "Ke Zhi",
        ]
    ):
        return "calm"
    if _has_any(
        [
            "fluent",
            "confident",
            "assertive",
            "Zi Xin",
            "Jian Ding",
            "Guo Duan",
            "professional",
            "Liu Li",
            "Cong Rong",
        ]
    ):
        return "fluent"

    return None
