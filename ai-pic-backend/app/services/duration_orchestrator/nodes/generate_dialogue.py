"""
dialogue Sheng Cheng node

Gen Ju scene Yu Suan call ScriptLangGraphAgent Sheng Cheng dialogue.
"""

from typing import Any, Dict

from app.core.logging import get_logger
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus
from app.services.duration_orchestrator.utils import count_dialogue_words

logger = get_logger()


async def generate_dialogue_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
 dialogue Sheng Cheng node.

 Gen Ju current scene Yu Suan Yue Shu, call ScriptLangGraphAgent Sheng Cheng dialogue.

 input status:
 - scene_budgets: scene Yu Suan list
 - current_scene_index: current scene index
 - script_agent: ScriptLangGraphAgent instance
 - episode: Episode data
 - story: Story data
 - generation_config: Sheng Cheng configuration

 output status update:
 - scene_budgets: update Sheng Cheng Jie Guo
 - generated_dialogues: Tian Jia Sheng Cheng dialogue
 - reasoning: Tian Jia Sheng Cheng log
    """
    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        logger.warning("generate_dialogue_node: current index Yue Jie")
        return {}

    budget: SceneBudget = budgets[current_index]
    script_agent = state.get("script_agent")
    episode = state.get("episode", {})
    story = state.get("story", {})
    generation_config = state.get("generation_config", {})

    if not script_agent:
        logger.error("generate_dialogue_node: missing script_agent")
        return {
            "errors": state.get("errors", []) + ["missing_script_agent"],
        }

    # update status as Jin Xing in
    budget.status = SceneStatus.IN_PROGRESS
    budget.attempt_count += 1

    logger.info(
        "generate_dialogue_node: Kai Shi Sheng Cheng scene %d dialogue",
        budget.scene_number,
        extra={
            "event": "dialogue_generation_started",
            "episode_id": state.get("episode_id"),
            "scene_number": budget.scene_number,
            "target_duration_seconds": budget.target_duration_seconds,
            "target_word_count": budget.target_word_count,
            "attempt": budget.attempt_count,
        },
    )

    # Zhun Bei scene Yu Suan list(only Bao Han current scene)
    # Zhe Yang Script Agent Canas current scene Sheng Cheng Fu He word count requirement dialogue
    current_budgets = [budget]

    try:
        # call ScriptLangGraphAgent
        result = await script_agent.generate(
            episode=episode,
            story=story,
            format_type=generation_config.get("format_type", "short_video"),
            language=generation_config.get("language", "zh"),
            dialogue_style=generation_config.get("dialogue_style", "natural"),
            scene_detail_level=generation_config.get("scene_detail_level", "detailed"),
            additional_requirements=generation_config.get("additional_requirements"),
            style_preferences=generation_config.get("style_preferences"),
            model=generation_config.get("model"),
            prefer_provider=generation_config.get("prefer_provider"),
            temperature=generation_config.get("temperature", 0.7),
            scene_budgets=current_budgets,
        )

        if not result or "error" in result:
            error_msg = result.get("error", "unknown_error") if result else "no_result"
            logger.warning(
                "generate_dialogue_node: scene %d Sheng Cheng failed: %s",
                budget.scene_number,
                error_msg,
            )
            budget.status = SceneStatus.PENDING
            return {
                "scene_budgets": budgets,
                "errors": state.get("errors", [])
                + [f"scene_{budget.scene_number}_generation_failed: {error_msg}"],
            }

        # extract Sheng Cheng dialogue
        content = result.get("content", {})
        dialogues = content.get("dialogues", []) if isinstance(content, dict) else []

        # Guo Lv Chu current scene dialogue
        scene_dialogues = [
            d for d in dialogues if d.get("scene_number") == budget.scene_number
        ]

        # Ji Suan Shi Ji word count
        actual_word_count = count_dialogue_words(scene_dialogues)
        budget.actual_word_count = actual_word_count

        logger.info(
            "generate_dialogue_node: scene %d dialogue Sheng Cheng complete",
            budget.scene_number,
            extra={
                "event": "dialogue_generation_completed",
                "episode_id": state.get("episode_id"),
                "scene_number": budget.scene_number,
                "dialogue_count": len(scene_dialogues),
                "actual_word_count": actual_word_count,
                "target_word_count": budget.target_word_count,
                "word_count_ratio": round(actual_word_count / budget.target_word_count, 2)
                if budget.target_word_count > 0
                else 0,
            },
        )

        # update Sheng Cheng dialogue
        generated_dialogues = state.get("generated_dialogues", {})
        generated_dialogues[budget.scene_number] = scene_dialogues

        reasoning = state.get("reasoning", [])
        reasoning.append(
            f"scene {budget.scene_number} dialogue generate Wan Cheng: "
            f"{len(scene_dialogues)} Tiao dialogue，"
            f"{actual_word_count} Zi (Mu Biao {budget.target_word_count} Zi)"
        )

        return {
            "scene_budgets": budgets,
            "generated_dialogues": generated_dialogues,
            "reasoning": reasoning,
            "last_generation_result": result,
        }

    except Exception as exc:
        logger.exception(
            "generate_dialogue_node: scene %d Sheng Cheng exception",
            budget.scene_number,
        )
        budget.status = SceneStatus.PENDING
        return {
            "scene_budgets": budgets,
            "errors": state.get("errors", [])
            + [f"scene_{budget.scene_number}_exception: {str(exc)}"],
        }


def should_proceed_to_tts(state: Dict[str, Any]) -> str:
    """
 Lu You function: determine Shi Fou Ying Gai Jin Ru TTS Shi Pao Jie Duan.

    Returns:
 "tts" - has dialogue, Jin Ru TTS Jie Duan
 "retry" - none dialogue or failed, retry
 "failed" - reach maximum retry Ci Shu
    """
    from app.services.duration_orchestrator.constants import MAX_RETRY_ATTEMPTS

    budgets = state.get("scene_budgets", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(budgets):
        return "failed"

    budget: SceneBudget = budgets[current_index]
    generated_dialogues = state.get("generated_dialogues", {})
    scene_dialogues = generated_dialogues.get(budget.scene_number, [])

    if not scene_dialogues:
        if budget.attempt_count >= MAX_RETRY_ATTEMPTS:
            return "failed"
        return "retry"

    return "tts"
