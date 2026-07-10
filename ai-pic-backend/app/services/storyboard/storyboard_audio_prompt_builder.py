"""Audio timeline -> storyboard visual prompt helpers.

Goal:
- Keep storyboard `description` suitable for UI (may include dialogue text).
- Generate a separate, *visual-only* prompt description for AI generation:
  - No literal dialogue lines (avoid subtitles/reading).
  - No readable screen text (avoid model hallucinated UI text).
  - Dialogue beats should explicitly describe speaking/lip movement.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate

_QUOTED_TEXT_RE = re.compile(r"[\"“”‘’「」『』](?P<body>.{1,120}?)[\"“”‘’「」『』]")
_FILE_LIKE_RE = re.compile(
    r"(?P<name>[\w\u4e00-\u9fff\-\_]{1,60})\.(?:pdf|docx?|txt|pptx?|xlsx?|png|jpe?g|webp|mp3|mp4)",
    re.IGNORECASE,
)
_MULTI_SPACE_RE = re.compile(r"\s+")


def _compact(text: str) -> str:
    return _MULTI_SPACE_RE.sub(" ", (text or "").strip())


def _strip_quoted_text(text: str) -> str:
    """Replace quoted/screen text with a generic placeholder."""
    if not text:
        return ""
    return _QUOTED_TEXT_RE.sub("(content Mo Hu not allowed Du)", text)


def _strip_file_like_tokens(text: str) -> str:
    if not text:
        return ""
    return _FILE_LIKE_RE.sub("(file/Fu Jian)", text)


def _looks_like_document_read(text: str) -> bool:
    if not isinstance(text, str):
        return False
    t = text.strip()
    if not t:
        return False
    if "_" in t:
        return True
    lowered = t.lower()
    if ".pdf" in lowered or ".doc" in lowered:
        return True
    keywords = ("Li Hun Xie Yi", "Cao An", "Tiao Kuan", "Jing Shen Chu Hu", "Xu Gou Zhai Wu", "Fu Jian")
    return any(k in t for k in keywords)


def _infer_dialogue_intent(text: str) -> Optional[str]:
    t = (text or "").strip()
    if not t:
        return None
    if "？" in t or "?" in t:
        return "Yi Wen/Zhui Wen"
    if "！" in t or "!" in t:
        return "EmotionJi Lie"
    if any(k in t for k in ("Bu Shi", "missing", "Bie Wu Hui")):
        return "Jie Shi/Bian Jie"
    if any(k in t for k in ("you Cong Shen Me Shi Hou", "you Dao Di", "Suan Ji")):
        return "Zhi Wen/Zhi Kong"
    return None


def _performance_for_intent(intent: str | None, *, voiceover: bool) -> dict[str, str]:
    if voiceover:
        return {
            "expression": "Ya Yi Yan Shen and Xi Wei Hu Xi change",
            "gesture": "Shen Ti Ting in Yuan Wei, Shou Zhi Qing Wei Shou Jin or Ting Dun",
            "shot_goal": "Yong Chen Mo Fan Ying Cheng Jie narrationEmotion, not Biao Xian Kai Kou Shuo Hua",
        }
    if intent == "Yi Wen/Zhui Wen":
        return {
            "expression": "Mei Tou Wei Zhou, Yan Shen Zhui Wen Dui Fang",
            "gesture": "Shang Shen Qing Wei Qian Qing, Shou Bu has Ke Zhi Zhui Wen action",
            "shot_goal": "Tu Chu character Shi Tan and Xin Xi Ya Li",
        }
    if intent == "EmotionJi Lie":
        return {
            "expression": "Yan Kuang Jin Beng, Zui Jiao Yong Li, EmotionWai Lu",
            "gesture": "Jian Jing Beng Jin, Shou Bu action Geng Ming Xian Dan not Guo Du Kua Zhang",
            "shot_goal": "Fang Da conflict Bao Dian and short drama Jie Zou",
        }
    if intent == "Jie Shi/Bian Jie":
        return {
            "expression": "Shen Qing Ji Qie You Ke Zhi, Mu Guang Shan Bi after retry Kan Xiang Dui Fang",
            "gesture": "Shou Zhang Qing Tai Zuo Jie Shi action, Shen Ti keep Fang Yu Zi Tai",
            "shot_goal": "Biao Xian character Wu Jie after Bian Jie Ya Li",
        }
    if intent == "Zhi Wen/Zhi Kong":
        return {
            "expression": "Mu Guang Rui Li, Biao Qing Leng Ying, Ya Po Gan Zeng Qiang",
            "gesture": "Shen Ti Ding Zhu, Shou Bu Zhi Xiang or Ya Di action Xing Cheng Dui Zhi",
            "shot_goal": "Xing Cheng Dui Zhi relationship and suspense Ya Po",
        }
    return {
        "expression": "Zi Ran Kou Xing and Wei Biao Qing change",
        "gesture": "Tou Bu and Shou Bu has Xi Xiao Fan Ying, action Tie He Shuo Hua Jie Zou",
        "shot_goal": "Jiao Dai characterEmotionand relationship advance",
    }


def build_visual_prompt_description(
    *,
    beat_type: str,
    speaker_name: str | None,
    text: str | None,
    dialogue_action: Any = None,
) -> str:
    """Build a visual-only description for storyboard prompt generation."""
    raw_text = text or ""
    clean_text = _compact(_strip_file_like_tokens(_strip_quoted_text(raw_text)))

    if beat_type == "pause":
        rendered = prompt_manager.render_prompt(
            PromptTemplate.STORYBOARD_AUDIO_VISUAL_PAUSE.value, {}
        )
        return _compact(rendered)

    if beat_type == "action":
        base = clean_text or "action shot"
        rendered = prompt_manager.render_prompt(
            PromptTemplate.STORYBOARD_AUDIO_VISUAL_ACTION.value,
            {
                "action": base,
                "performance": "action has clear Mu Di and Fan Ying Jie Zou, characterEmotionthrough Zi Tai Ti Xian",
            },
        )
        return _compact(rendered)

    # dialogue beat
    speaker = (speaker_name or "").strip() or "character"
    action_str = str(dialogue_action or "").strip()
    is_voiceover = any(k in action_str for k in ("Nei Xin Du Bai", "Xin Sheng", "OS", "narration"))

    if _looks_like_document_read(raw_text) or _looks_like_document_read(clean_text):
        rendered = prompt_manager.render_prompt(
            PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_READ_TEXT.value,
            {
                "speaker": speaker,
                "reaction": "Du to key Xin Xi after Yan Shen Zhou Bian and Shou Bu Ting Dun",
            },
        )
        return _compact(rendered)

    intent = _infer_dialogue_intent(clean_text)
    performance = _performance_for_intent(intent, voiceover=is_voiceover)
    template_name = (
        PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_VOICEOVER.value
        if is_voiceover
        else PromptTemplate.STORYBOARD_AUDIO_VISUAL_DIALOGUE_SPOKEN.value
    )
    rendered = prompt_manager.render_prompt(
        template_name,
        {
            "speaker": speaker,
            "intent": intent,
            "expression": performance["expression"],
            "gesture": performance["gesture"],
            "shot_goal": performance["shot_goal"],
        },
    )
    return _compact(rendered)
