"""
TTS Shi Pao node

call TTS service get dialogue Shi Ji when Zhang, Yong Yu validation scene when Zhang Shi Fou Da Biao.
"""

import logging
from typing import Any, Dict, List

from app.services.duration_orchestrator.constants import WORDS_PER_SECOND
from app.services.duration_orchestrator.state import SceneBudget
from app.services.duration_orchestrator.utils import count_dialogue_words

logger = logging.getLogger(__name__)


def estimate_duration_from_dialogues(
    dialogues: List[Dict[str, Any]],
    speaking_rate: float = WORDS_PER_SECOND,
) -> int:
    """
 Gen Ju dialogue word count Gu Suan when Zhang(Hao Miao).

 Zhe Shi quick Gu Suan mode, not call Shi Ji TTS.
 Yong Yu quick validation dialogue word count Shi Fou in target range interior.

    Args:
 dialogues: dialogue list, Mei Ge Yuan Su Bao Han content character Duan
 speaking_rate: Mei Miao Han Zi Shu(default 4.7, Lai Zi Xian Shang TTS Yu Su Jiao Zhun)

    Returns:
 Gu Suan when Zhang(Hao Miao)
    """
    word_count = count_dialogue_words(dialogues)
    duration_seconds = word_count / speaking_rate
    return int(duration_seconds * 1000)


async def tts_trial_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 TTS Shi Pao node.

 get scene dialogue Shi Ji or Gu Suan when Zhang.

 support Liang Zhong mode: 
 1. Gu Suan mode(default): Gen Ju word count quick Gu Suan, Wu Xu call TTS
 2. Shi Ji mode: call TTS service get Zhen Shi when Zhang

 input status:
 - scene_budgets: scene Yu Suan list
 - current_scene_index: current scene index
 - generated_dialogues: Sheng Cheng dialogue
 - use_actual_tts: Shi Fou Shi Yong Shi Ji TTS(default False)
 - tts_service: TTS service instance(Shi Ji mode need)

 output status update:
 - scene_budgets: update Shi Ji when Zhang
 - reasoning: Tian Jia Shi Pao log
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)
    use_actual_tts = state.get("use_actual_tts", False)

    if current_index >= len(budgets):
        logger.warning("tts_trial_node: current index Yue Jie")
        return {}

    budget: SceneBudget = budgets[current_index]
    generated_dialogues = state.get("generated_dialogues", {})
    scene_dialogues = generated_dialogues.get(budget.scene_number, [])

    if not scene_dialogues:
        logger.warning(
            "tts_trial_node: scene %d none dialogue data",
            budget.scene_number,
        )
        return {}

    reasoning = state.get("reasoning", [])

    if use_actual_tts:
        # Shi Ji TTS mode
        actual_duration_ms = await _run_actual_tts(
            state=state,
            dialogues=scene_dialogues,
            budget=budget,
        )
    else:
        # Gu Suan mode
        actual_duration_ms = estimate_duration_from_dialogues(scene_dialogues)

    # Zhuan Huan as seconds
    actual_duration_seconds = actual_duration_ms / 1000.0
    budget.actual_duration_seconds = actual_duration_seconds

    # Ji Suan Pian Cha
    target_seconds = budget.target_duration_seconds
    deviation = actual_duration_seconds - target_seconds
    deviation_percent = (deviation / target_seconds * 100) if target_seconds > 0 else 0

    mode_label = "TTSShi Ce" if use_actual_tts else "word count Gu Suan"
    logger.info(
        "tts_trial_node: scene %d %scomplete",
        budget.scene_number,
        mode_label,
        extra={
            "scene_number": budget.scene_number,
            "mode": "actual" if use_actual_tts else "estimate",
            "actual_duration_seconds": actual_duration_seconds,
            "target_duration_seconds": target_seconds,
            "deviation_seconds": deviation,
            "deviation_percent": deviation_percent,
        },
    )

    reasoning.append(
        f"scene {budget.scene_number} {mode_label}: "
        f"{actual_duration_seconds:.1f}s (Mu Biao {target_seconds}s, "
        f"Pian Cha {deviation:+.1f}s / {deviation_percent:+.0f}%)"
    )

    return {
        "scene_budgets": budgets,
        "reasoning": reasoning,
    }


async def _run_actual_tts(
    state: Dict[str, Any],
    dialogues: List[Dict[str, Any]],
    budget: SceneBudget,
) -> int:
    """
 call Shi Ji TTS service get when Zhang.

 Shi Yong sampling Ce Lve: Ru Guo dialogue Chao Guo 5 Tiao, sampling 3 Tiao Ji Suan Ping Jun Yu Su.

    Args:
 state: status Zi Dian
 dialogues: dialogue list
 budget: scene Yu Suan

    Returns:
 Gu Suan total duration(Hao Miao)
    """
    tts_service = state.get("tts_service")
    voice_config = state.get("voice_config", {})

    if not tts_service:
        logger.warning("tts_trial_node: none TTS service, Jiang Ji as Gu Suan mode")
        return estimate_duration_from_dialogues(dialogues)

    # sampling Ce Lve: Chao Guo 5 Tiao dialogue when sampling 3 Tiao
    sample_size = 3
    if len(dialogues) <= sample_size:
        sample_dialogues = dialogues
    else:
        # sampling Shou, in, Wei
        mid_index = len(dialogues) // 2
        sample_dialogues = [
            dialogues[0],
            dialogues[mid_index],
            dialogues[-1],
        ]

    total_sample_chars = 0
    total_sample_duration_ms = 0

    try:
        for dlg in sample_dialogues:
            content = dlg.get("content", "")
            if not content:
                continue

            # call TTS get when Zhang
            result = await tts_service.generate_speech(
                text=content,
                voice_type=voice_config.get("voice_type"),
                speed=voice_config.get("speed", 1.0),
                prefer_provider=voice_config.get("provider"),
            )

            if result and result.get("duration"):
                duration_ms = int(result["duration"] * 1000)
                total_sample_chars += len(content)
                total_sample_duration_ms += duration_ms

        if total_sample_chars > 0 and total_sample_duration_ms > 0:
            # Ji Suan Shi Ji Yu Su
            actual_chars_per_second = total_sample_chars / (
                total_sample_duration_ms / 1000
            )

            # Yong Shi Ji Yu Su Gu Suan total duration
            total_chars = count_dialogue_words(dialogues)
            estimated_total_ms = int(total_chars / actual_chars_per_second * 1000)

            logger.info(
                "tts_trial_node: sampling TTS complete",
                extra={
                    "scene_number": budget.scene_number,
                    "sample_count": len(sample_dialogues),
                    "actual_chars_per_second": actual_chars_per_second,
                    "total_chars": total_chars,
                    "estimated_total_ms": estimated_total_ms,
                },
            )
            return estimated_total_ms

    except Exception as exc:
        logger.warning(
            "tts_trial_node: TTS sampling failed, Jiang Ji as Gu Suan mode: %s",
            exc,
        )

    # Jiang Ji as Gu Suan mode
    return estimate_duration_from_dialogues(dialogues)
