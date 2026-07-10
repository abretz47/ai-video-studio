from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from app.core.validators.script_dialogue_quality import looks_like_writer_note
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate
from app.services.duration_orchestrator.constants import WORDS_PER_SECOND
from app.services.duration_orchestrator.state import SceneBudget
from app.utils.json_utils import extract_json_block

BuildWordCountConstraints = Callable[[List[SceneBudget], List[Dict[str, Any]]], str]


def _to_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _filter_scene_items(
    items: Sequence[Dict[str, Any]],
    allowed_scene_numbers: Set[int],
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        scene_no = _to_int(item.get("scene_number"))
        if scene_no in allowed_scene_numbers:
            filtered.append(item)
    return filtered


def _exclude_scene_items(
    items: Sequence[Dict[str, Any]],
    excluded_scene_numbers: Set[int],
) -> List[Dict[str, Any]]:
    kept: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        scene_no = _to_int(item.get("scene_number"))
        if scene_no not in excluded_scene_numbers:
            kept.append(item)
    return kept


async def try_fill_pending_scenes_after_react(
    *,
    ai_manager: Any,
    episode: Dict[str, Any],
    story: Dict[str, Any],
    scenes: Sequence[Dict[str, Any]],
    pending_budgets: Sequence[SceneBudget],
    dialogue_style: str,
    language: str,
    format_type: str,
    temperature: float,
    model: Optional[str],
    prefer_provider: Optional[str],
    existing_dialogues: Sequence[Dict[str, Any]],
    existing_stage_directions: Sequence[Dict[str, Any]],
    build_word_count_constraints: BuildWordCountConstraints,
) -> Optional[Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[int]]]:
    """Try to fill missing/out-of-tolerance scenes after REACT max retries.

    This is a last-resort strategy to avoid accepting obviously incomplete
    results (e.g., early scenes missing dialogues) after repeated retries.
    """
    pending_scene_numbers = sorted(
        {b.scene_number for b in pending_budgets if b.scene_number}
    )
    if not pending_scene_numbers:
        return None
    pending_set = set(pending_scene_numbers)

    pending_scenes: List[Dict[str, Any]] = []
    for idx, sc in enumerate(scenes, start=1):
        if not isinstance(sc, dict):
            continue
        scene_no = _to_int(sc.get("scene_number")) or idx
        if scene_no in pending_set:
            pending_scenes.append(sc)

    if not pending_scenes:
        return None

    base_prompt = prompt_manager.render_prompt(
        PromptTemplate.SCRIPT_DIALOGUES.value,
        {
            "episode": episode,
            "story": story,
            "scenes": pending_scenes,
            "dialogue_style": dialogue_style,
            "language": language,
            "format_type": format_type,
        },
    )
    base_prompt = (
        base_prompt
        + "\n\n## Zhong Yao: only Bu Quan Yi Xia scene\n"
        + f"you may only generate dialogue and stage directions for these scene_number values: {pending_scene_numbers}\n"
        + "Hard requirement: each scene must contain at least 2 lines of dialogue, and scene_number must be an accurate integer.\n"
        + 'Do not output screenwriter/assistant meta-language (for example "you can use this here"), and do not repeat template lines across scenes.\n'
        + "Do not output content for any other scene.\n"
    )

    constraints_text = build_word_count_constraints(
        list(pending_budgets), pending_scenes
    )
    base_prompt = base_prompt + constraints_text

    schema = {
        "name": "script_dialogues_fill_missing",
        "schema": {
            "type": "object",
            "properties": {
                "dialogues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {
                                "anyOf": [{"type": "integer"}, {"type": "null"}]
                            },
                            "character": {
                                "anyOf": [{"type": "string"}, {"type": "null"}]
                            },
                            "content": {"type": "string"},
                            "emotion": {
                                "anyOf": [{"type": "string"}, {"type": "null"}]
                            },
                            "action": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        },
                    },
                },
                "stage_directions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {
                                "anyOf": [{"type": "integer"}, {"type": "null"}]
                            },
                            "timing": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                            "content": {"type": "string"},
                            "type": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        },
                    },
                },
            },
        },
    }

    new_dialogues: List[Dict[str, Any]] = []
    new_stage: List[Dict[str, Any]] = []
    passed_constraints = False

    prompt = base_prompt
    budgets_by_scene = {b.scene_number: b for b in pending_budgets if b.scene_number}

    for attempt in range(3):
        resp = await ai_manager.generate_text(
            prompt=prompt,
            temperature=(
                min(0.6, temperature)
                if attempt == 0
                else (0.4 if attempt == 1 else 0.2)
            ),
            model=model,
            prefer_provider=prefer_provider,
            json_schema=schema,
            system_prompt="you Shi professional script dialogue and Wu Tai Zhi Shi Xie Shou, Qing strict An JSON return.",
        )
        if not getattr(resp, "success", False):
            continue

        parsed = (
            resp.data
            if isinstance(resp.data, dict)
            else extract_json_block(
                resp.data if isinstance(resp.data, str) else str(resp.data)
            )
        )
        if not isinstance(parsed, dict):
            continue

        new_dialogues = _filter_scene_items(parsed.get("dialogues") or [], pending_set)
        new_stage = _filter_scene_items(
            parsed.get("stage_directions") or [], pending_set
        )

        per_scene_counts = {
            s: len([d for d in new_dialogues if _to_int(d.get("scene_number")) == s])
            for s in pending_scene_numbers
        }
        has_writer_notes = any(
            looks_like_writer_note(str(d.get("content") or ""))
            for d in new_dialogues
            if isinstance(d, dict)
        )
        if has_writer_notes:
            prompt = (
                base_prompt
                + "\n\n## REACT Bo Hui\n"
                + 'Do not output screenwriter/assistant meta-language (for example "you can use this here"). Rewrite everything as in-scene dialogue and do not keep meta-language.\n'
            )
            continue

        missing = [s for s, c in per_scene_counts.items() if c < 2]
        if not missing:
            # Additional guard: ensure dialogue duration is within scene budget tolerance.
            too_short: list[str] = []
            too_long: list[str] = []
            for scene_no in pending_scene_numbers:
                budget = budgets_by_scene.get(scene_no)
                if not budget:
                    continue
                total_chars = sum(
                    len(str(d.get("content") or ""))
                    for d in new_dialogues
                    if isinstance(d, dict)
                    and _to_int(d.get("scene_number")) == scene_no
                )
                est_seconds = total_chars / WORDS_PER_SECOND if total_chars > 0 else 0.0
                if budget.min_duration_seconds and est_seconds < float(
                    budget.min_duration_seconds
                ):
                    need = int(
                        (budget.target_duration_seconds - est_seconds)
                        * WORDS_PER_SECOND
                    )
                    min_chars = int(
                        float(budget.min_duration_seconds) * WORDS_PER_SECOND
                    )
                    too_short.append(
                        f"{scene_no}(Dang Qian≈{est_seconds:.1f}s，at least≈{budget.min_duration_seconds}s；Zi Fu Shu≥{min_chars}，Jian Yi Zai+{max(need, 20)}Zi)"
                    )
                elif budget.max_duration_seconds and est_seconds > float(
                    budget.max_duration_seconds
                ):
                    over = int(
                        (est_seconds - budget.target_duration_seconds)
                        * WORDS_PER_SECOND
                    )
                    too_long.append(
                        f"{scene_no}(Dang Qian≈{est_seconds:.1f}s，Zui Duo≈{budget.max_duration_seconds}s；Jian Yi Shan Jian≈{max(over, 20)}Zi)"
                    )

            if not too_short and not too_long:
                passed_constraints = True
                break

            reject_lines: list[str] = []
            if too_short:
                reject_lines.append("Yi Xia scene dialogue duration Reng insufficient: " + "；".join(too_short))
            if too_long:
                reject_lines.append("Yi Xia scene dialogue when Zhang Guo Chang: " + "；".join(too_long))

            prompt = (
                base_prompt
                + "\n\n## REACT Bo Hui(duration not Da Biao)\n"
                + "\n".join(reject_lines)
                + "\nYing Xing requirement: strict Man Zu Ge scene word count/when Zhang Yue Shu; Zhi Neng output Zhi Ding scene_number; Jin Zhi Bian Ju/Zhu Shou Yuan Yu Yan and Kua scene Chong Fu template line.\n"
            )
            continue

        prompt = (
            base_prompt
            + "\n\n## REACT Bo Hui\n"
            + f"Yi Xia scene dialogue Tiao Shu Reng Bu Zu 2 Ju：{missing}；Dang Qian Ji Shu：{per_scene_counts}\n"
            + "Qing Jin Zhen Dui Zhe Xie scene Bu Zu to 2-3 Ju dialogue.\n"
        )

    if not passed_constraints:
        return None

    if not new_dialogues and not new_stage:
        return None

    merged_dialogues = (
        _exclude_scene_items(existing_dialogues, pending_set) + new_dialogues
    )
    merged_stage = (
        _exclude_scene_items(existing_stage_directions, pending_set) + new_stage
    )

    return merged_dialogues, merged_stage, pending_scene_numbers
