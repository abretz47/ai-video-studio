"""Script dialogue quality validators.

These helpers are used by script-generation agents to detect common LLM failure
modes (assistant meta-notes, repetitive filler lines, etc.) and trigger REACT
regeneration before persisting results.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

_PUNCTUATION = set(
    " \t\r\n" "，。！？!?….,、;；:：" "\"“”‘’'`" "()（）[]【】{}<>《》" "—-~～"
)


def _normalize_text(text: str) -> str:
    return "".join(ch for ch in text.strip().lower() if ch not in _PUNCTUATION)


def looks_like_writer_note(text: str) -> bool:
    """Heuristic: detect assistant/writer meta-notes accidentally output as dialogue."""
    s = (text or "").strip()
    if not s:
        return False

    if s.startswith(("prompt: ", "Zhu: ", "Bei Zhu: ", "suggestion: ")):
        return True

    locators = ("here", "Ci Chu", "Zhe Yi Duan", "Zhe Duan", "Zhe Yi Mu", "Ben Duan", "Ben Chang", "Ci Shi")
    verbs = (
        "Can",
        "suggestion",
        "Ying Gai",
        "need",
        "Yong Lai",
        "Yong Yu",
        "Tu Chu",
        "Jia Qiang",
        "Ti Xian",
        "Biao Xian",
        "Foreshadowing",
    )
    targets = ("conflict", "Emotion", "Zhang Li", "Jie Zou", "atmosphere", "Zhuan Zhe", "twist", "Conflict")

    has_locator = any(k in s for k in locators)
    has_meta_signal = any(k in s for k in verbs) or any(k in s for k in targets)
    if has_locator and has_meta_signal:
        return True

    return False


def find_reused_short_dialogues(
    dialogues: Sequence[dict],
    *,
    max_chars: int = 40,
    min_repeats: int = 2,
) -> set[str]:
    """Return normalized dialogue contents that are suspiciously repeated."""
    normalized: list[str] = []
    for d in dialogues:
        if not isinstance(d, dict):
            continue
        content = d.get("content")
        if not isinstance(content, str):
            continue
        raw = content.strip()
        if not raw or len(raw) > max_chars:
            continue
        normalized.append(_normalize_text(raw))

    counts = Counter([n for n in normalized if n])
    return {k for k, v in counts.items() if v >= min_repeats}


@dataclass(frozen=True, slots=True)
class SceneDialogueIssue:
    code: str
    message: str


def validate_scene_dialogues(
    scene_dialogues: Sequence[dict],
    *,
    min_lines: int = 2,
    repeated_short_norms: set[str] | None = None,
) -> list[SceneDialogueIssue]:
    """Validate a single scene's dialogues and return issues (empty means ok)."""
    issues: list[SceneDialogueIssue] = []

    if len([d for d in scene_dialogues if isinstance(d, dict)]) < min_lines:
        issues.append(
            SceneDialogueIssue(
                code="too_few_lines",
                message=f"对白条数不足（至少 {min_lines} 句）",
            )
        )

    for d in scene_dialogues:
        if not isinstance(d, dict):
            continue
        content = d.get("content")
        if not isinstance(content, str):
            continue
        if looks_like_writer_note(content):
            issues.append(
                SceneDialogueIssue(
                    code="writer_note",
                    message="Jian Ce to Yi Si Bian Ju/Zhu Shou Yuan Yu Yan(for example"hereCan…"), need Gai Xie as Xi Nei line",
                )
            )
            break

    if repeated_short_norms:
        for d in scene_dialogues:
            if not isinstance(d, dict):
                continue
            content = d.get("content")
            if not isinstance(content, str):
                continue
            if _normalize_text(content) in repeated_short_norms:
                issues.append(
                    SceneDialogueIssue(
                        code="reused_filler",
                        message="Jian Ce to Kua scene Chong Fu template line(Qing Ti Huan as and Ben scene related specific line)",
                    )
                )
                break

    return issues
