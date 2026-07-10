"""Text utilities for dialogue processing."""

from __future__ import annotations

import re

from app.core.logging import get_logger

logger = get_logger()


_ONLY_PUNCT_OR_SPACE = re.compile(
    r"^[\s\.\,\!\?\-\—\_\~\·\…\，\。\！\？\、\：\；\"\"\(\)\（\）]+$"
)

_LEADING_INLINE_ACTION_RE = re.compile(
    r"^\s*[\(\（\[\【](?P<action>[^)\）\]\】]{1,200})[\)\）\]\】]\s*"
)
_TRAILING_INLINE_ACTION_RE = re.compile(
    r"\s*[\(\（\[\【](?P<action>[^)\）\]\】]{1,200})[\)\）\]\】]\s*$"
)
_SPEECH_ATTR_RE = re.compile(
    r"^\s*(?P<attr>.{1,80}?)(?P<sep>[:：]|\s+|“|\"|‘|'|「|『)(?P<text>.+)$"
)
_TRIVIAL_SPEECH_ATTR_RE = re.compile(
    r"^(?:I|you|Ta|Ta|Ta|Wo Men|Ni Men|Ta Men|Ta Men|Da Jia|Zhong Ren|Suo You Ren)(?:Men)?(?:Shuo|Shuo Dao|Wen|Wen Dao|Da|Da Dao)$"
)

_SPEECH_ATTR_SUFFIXES: tuple[str, ...] = tuple(
    sorted(
        {
            "Di Sheng Shuo",
            "Qing Sheng Shuo",
            "Xiao Sheng Shuo",
            "Da Sheng Shuo",
            "Xiao Zhe Shuo",
            "Leng Leng Di Shuo",
            "Di Gu Dao",
            "Ni Nan Dao",
            "Pao Xiao Dao",
            "Hou Dao",
            "Han Dao",
            "Shuo Dao",
            "Wen Dao",
            "Da Dao",
            "Shuo",
            "Wen",
            "Da",
        },
        key=len,
        reverse=True,
    )
)


def norm_name(name: str) -> str:
    """Normalize character name for comparison."""

    return "".join((name or "").strip().lower().split())


def looks_like_silence(text: str) -> bool:
    """Check if text represents silence or pause."""

    cleaned = (text or "").strip()
    if not cleaned:
        return True
    if _ONLY_PUNCT_OR_SPACE.match(cleaned):
        return True
    lowered = cleaned.lower()
    if lowered in {"...", "……", "…", "(Chen Mo)", "(silence)", "[silence]"}:
        return True
    return False


def sanitize_dialogue_content(
    content: str,
    *,
    action: str | None = None,
) -> tuple[str, str | None]:
    """
    Remove inline stage directions from dialogue text.

    Examples:
 - "(Tan Qi)Ni Hao" -> text="Ni Hao", action+="Tan Qi"
 - "Tan Yi Kou Qi, Zhan Qi Lai Shuo: Ni Hao" -> text="Ni Hao", action+="Tan Yi Kou Qi, Zhan Qi Lai Shuo"
    """

    text = str(content or "").strip()
    actions: list[str] = []

    if isinstance(action, str) and action.strip():
        actions.append(action.strip())

    while True:
        m = _LEADING_INLINE_ACTION_RE.match(text)
        if not m:
            break
        inline = m.group("action").strip()
        if inline:
            actions.append(inline)
        text = text[m.end() :].strip()

    while True:
        m = _TRAILING_INLINE_ACTION_RE.search(text)
        if not m:
            break
        inline = m.group("action").strip()
        if inline:
            actions.append(inline)
        text = text[: m.start()].strip()

    m = _SPEECH_ATTR_RE.match(text)
    if m:
        attr = (m.group("attr") or "").strip()
        attr_no_space = "".join(attr.split())
        suffix_ok = any(attr_no_space.endswith(suf) for suf in _SPEECH_ATTR_SUFFIXES)
        if (
            suffix_ok
            and attr_no_space
            and not _TRIVIAL_SPEECH_ATTR_RE.match(attr_no_space)
        ):
            actions.append(attr)
            text = m.group("text").strip()

    combined_action = "；".join(actions) if actions else None
    return text, combined_action
