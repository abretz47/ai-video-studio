from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.prompts.manager import prompt_manager
from app.utils.json_utils import extract_json_block

from .story_novel_export_ai import generate_story_novel_text
from .story_novel_export_utils import clip_text

logger = logging.getLogger(__name__)


def plan_intro_from_plan(
    plan: Dict[str, Any],
    *,
    story_title: str,
) -> Tuple[str, str, str, str]:
    question_title = (
        plan.get("question_title")
        if isinstance(plan.get("question_title"), str)
        else f"Ru He Ping Jia《{story_title}》Zhe Ge story？"
    )
    question_detail = (
        plan.get("question_detail")
        if isinstance(plan.get("question_detail"), str)
        else "Xiang Kan a has Gou Zi, has twist, Jie Zou Zai Xian Zhang Wen story, Zui Hao Shi Lian Xu update Na Zhong."
    )
    narrator_profile = (
        plan.get("narrator_profile")
        if isinstance(plan.get("narrator_profile"), str)
        else "Li Yi related: Xie Guo Yi Xie Zhang Wen story.Yi Xia as Ge Ren Jing Li Gai Bian, Xi Jie Qing Wu Shen Jiu."
    )
    running_summary_seed = (
        plan.get("running_summary_seed")
        if isinstance(plan.get("running_summary_seed"), str)
        else ""
    )
    question_detail = question_detail.replace("\\n", "\n")
    narrator_profile = narrator_profile.replace("\\n", "\n")
    return question_title, question_detail, narrator_profile, running_summary_seed


def _normalize_key_beats(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    beats: List[str] = []
    for raw in value:
        text = str(raw or "").strip()
        if text:
            beats.append(text)
    return beats


def _distribute_target_words(*, target_words: int, chapter_total: int) -> List[int]:
    if chapter_total <= 0:
        return []
    base = max(1, target_words // chapter_total)
    remainder = max(0, target_words - base * chapter_total)
    targets = []
    for idx in range(chapter_total):
        targets.append(base + (1 if idx < remainder else 0))
    return targets


def _normalize_plan_chapters(
    plan: Dict[str, Any],
    *,
    chapter_total: int,
    target_words: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    chapters_raw = (
        plan.get("chapters") if isinstance(plan.get("chapters"), list) else []
    )
    distributed_targets = _distribute_target_words(
        target_words=target_words,
        chapter_total=chapter_total,
    )
    chapters: List[Dict[str, Any]] = []
    for idx in range(1, chapter_total + 1):
        source = chapters_raw[idx - 1] if idx - 1 < len(chapters_raw) else {}
        title = (
            str(source.get("title") or "").strip() if isinstance(source, dict) else ""
        )
        chapter_goal = (
            str(source.get("chapter_goal") or "").strip()
            if isinstance(source, dict)
            else ""
        )
        cliffhanger_hint = ""
        if isinstance(source, dict):
            cliffhanger_hint = str(
                source.get("cliffhanger_hint") or source.get("cliffhanger") or ""
            ).strip()

        if not title:
            title = f"Geng Xin {idx}"
        if not cliffhanger_hint:
            cliffhanger_hint = "below Yi Zhang Chu Xian Yi Wai Zhuan Zhe, Ju Shi Zhou Ran escalate."

        chapters.append(
            {
                "chapter_number": idx,
                "title": title,
                "target_words": (
                    distributed_targets[idx - 1] if distributed_targets else 0
                ),
                "chapter_goal": chapter_goal,
                "cliffhanger_hint": cliffhanger_hint,
            }
        )

    normalized_plan: Dict[str, Any] = dict(plan or {})
    normalized_plan["chapters"] = chapters
    return normalized_plan, chapters


async def generate_zhihu_plan_compact(
    *,
    story_payload: Dict[str, Any],
    target_words: int,
    chapter_total: int,
    model_id: Optional[str],
    prefer_provider: Optional[str],
    system_prompt: str,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    plan_prompt = prompt_manager.render_prompt(
        "story_novel_zhihu_plan_compact",
        {
            "story": story_payload,
            "target_words": target_words,
            "chapter_count": chapter_total,
        },
    )
    plan_text = await generate_story_novel_text(
        prompt=plan_prompt,
        system_prompt=system_prompt,
        model=model_id,
        prefer_provider=prefer_provider,
        temperature=0.2,
        max_tokens=3200,
    )

    plan = extract_json_block(plan_text) or {}
    chapters = plan.get("chapters") if isinstance(plan, dict) else None
    if not isinstance(chapters, list) or not chapters:
        plan_text_retry = await generate_story_novel_text(
            prompt=plan_prompt,
            system_prompt=system_prompt,
            model=model_id,
            prefer_provider=prefer_provider,
            temperature=0.1,
            max_tokens=3400,
        )
        plan = extract_json_block(plan_text_retry) or {}
        chapters = plan.get("chapters") if isinstance(plan, dict) else None
    if not isinstance(chapters, list) or not chapters:
        logger.warning("Zhihu novel plan parse failed; using fallback plan generator.")
        fallback_plan = _fallback_zhihu_plan(
            story_payload=story_payload, chapter_total=chapter_total
        )
        return _normalize_plan_chapters(
            fallback_plan,
            chapter_total=chapter_total,
            target_words=target_words,
        )

    return _normalize_plan_chapters(
        plan, chapter_total=chapter_total, target_words=target_words
    )


def _fallback_zhihu_plan(
    *, story_payload: Dict[str, Any], chapter_total: int
) -> Dict[str, Any]:
    title = str(story_payload.get("title") or "").strip()
    synopsis = story_payload.get("synopsis")
    running_summary_seed = (
        clip_text(synopsis, 900)
        if isinstance(synopsis, str) and synopsis.strip()
        else ""
    )
    episodes = (
        story_payload.get("episodes")
        if isinstance(story_payload.get("episodes"), list)
        else []
    )

    chapters: list[dict[str, Any]] = []
    for idx in range(1, chapter_total + 1):
        episode = episodes[idx - 1] if idx - 1 < len(episodes) else {}
        chapter_title = ""
        chapter_goal = ""
        cliffhanger_hint = ""
        if isinstance(episode, dict) and episode:
            chapter_title = str(episode.get("title") or "").strip()
            chapter_goal = str(episode.get("summary") or "").strip()
            plot_points = episode.get("plot_points")
            if isinstance(plot_points, list) and plot_points:
                if not chapter_goal:
                    first_points = [
                        str(x or "").strip()
                        for x in plot_points[:3]
                        if str(x or "").strip()
                    ]
                    if first_points:
                        chapter_goal = "；".join(first_points)
                cliffhanger_hint = str(plot_points[-1] or "").strip()

        if not chapter_title:
            chapter_title = f"Geng Xin {idx}"
        if not chapter_goal:
            chapter_goal = "advance Zhu Xian conflict and Mai below Xin Yin Guo."
        if not cliffhanger_hint:
            cliffhanger_hint = "Zhang Mo Chu Xian Yi Wai Zhuan Zhe, below Yi Zhang Ju Shi Zhou Ran escalate."

        chapters.append(
            {
                "chapter_number": idx,
                "title": clip_text(chapter_title, 120) or chapter_title,
                "chapter_goal": clip_text(chapter_goal, 520) or chapter_goal,
                "cliffhanger_hint": clip_text(cliffhanger_hint, 260)
                or cliffhanger_hint,
            }
        )

    return {
        "question_title": title or "Ru He Ping Jia Zhe Ge story?",
        "question_detail": "Xiang Kan a has Gou Zi, has twist, Jie Zou Zai Xian Zhang Wen story, Zui Hao Shi Lian Xu update Na Zhong.\\nMa Fan Lai Dian Zhen Shi Xi Jie, Bu Yao Kong Fan.",
        "narrator_profile": "Li Yi related: Xie Guo Yi Xie Zhang Wen story.Yi Xia as Ge Ren Jing Li Gai Bian, Xi Jie Qing Wu Shen Jiu.",
        "running_summary_seed": running_summary_seed or "",
        "chapters": chapters,
    }


async def generate_zhihu_chapter_beats(
    *,
    story_payload: Dict[str, Any],
    plan_context: Dict[str, Any],
    ledger: Dict[str, Any],
    previous_tail: str,
    previous_cliffhanger: str,
    chapter: Dict[str, Any],
    running_summary: str,
    model_id: Optional[str],
    prefer_provider: Optional[str],
    system_prompt: str,
) -> List[str]:
    beats_prompt = prompt_manager.render_prompt(
        "story_novel_zhihu_chapter_beats",
        {
            "story": story_payload,
            "plan": plan_context,
            "ledger": ledger,
            "previous_tail": previous_tail,
            "previous_cliffhanger": previous_cliffhanger,
            "chapter": chapter,
            "running_summary": running_summary,
        },
    )
    beats_text = await generate_story_novel_text(
        prompt=beats_prompt,
        system_prompt=system_prompt,
        model=model_id,
        prefer_provider=prefer_provider,
        temperature=0.2,
        max_tokens=1400,
    )
    payload = extract_json_block(beats_text) or {}
    beats = _normalize_key_beats(
        payload.get("key_beats") if isinstance(payload, dict) else None
    )
    if len(beats) >= 5:
        return beats[:9]

    retry_text = await generate_story_novel_text(
        prompt=beats_prompt,
        system_prompt=system_prompt,
        model=model_id,
        prefer_provider=prefer_provider,
        temperature=0.1,
        max_tokens=1600,
    )
    retry_payload = extract_json_block(retry_text) or {}
    beats = _normalize_key_beats(
        retry_payload.get("key_beats") if isinstance(retry_payload, dict) else None
    )
    if len(beats) >= 5:
        return beats[:9]

    fallback = beats[:9]
    if len(fallback) < 5:
        fallback.extend(
            [
                (
                    f"Cheng Jie Shang Yi Zhang Ka Dian：{previous_cliffhanger}（Ji Xu Xian Chang，Jiao Dai Ka Dian Zhi Hou Fa Sheng Le Shen Me）"
                    if previous_cliffhanger
                    else "Yong a specific scene quick Ru Xi, Pao Chu Ben Zhang conflict."
                ),
                "Yin Ru Xin Zu Ai or Dui Li Mian, Po Shi Zhu Jue Xing Dong.",
                "through Yi Chang specific Hu Dong/Dui Hua advance conflict and Xin Xi reveal.",
                "Chu Xian Yi Ci Wu Hui, twist or Dai Jia, Tai GaoEmotionand Feng Xian.",
                "Zhu Jue Zuo Chu key Xuan Ze, as subsequent Mai below Yin Guo.",
                "Ju Shi Tui Dao Zhang Mo Gou Zi before Lin Jie Dian.",
            ][: 5 - len(fallback)]
        )
    elif previous_cliffhanger:
        # Ensure the opening beat always responds to the cliffhanger even when partial beats exist.
        fallback[0] = (
            f"Cheng Jie Shang Yi Zhang Ka Dian：{previous_cliffhanger}（Ji Xu Xian Chang，Jiao Dai Ka Dian Zhi Hou Fa Sheng Le Shen Me）"
        )
    return fallback[:9]
