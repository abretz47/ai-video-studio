"""
Duration Orchestrator Agent

Ji Yu LangGraph Duan to Duan duration Bi Huan validation system.

core Liu Cheng: 
1. allocate_budget: Fen Pei scene when Zhang Yu Suan
2. generate_dialogue: Sheng Cheng Fu He word count Yue Shu dialogue
3. tts_trial: Gu Suan/Ce Liang Shi Ji when Zhang
4. validate_duration: validation when Zhang Shi Fou Da Biao
5. commit_scene/prepare_retry: submit or Zhun Bei retry
6. assemble_episode: assemble Zui Zhong episode
7. final_validation: validation total duration ±10%
"""

from typing import Any, Callable, Dict, List, Optional

from app.core.logging import get_logger
from app.services.duration_orchestrator.nodes import (
    allocate_budget_node,
    assemble_episode_node,
    commit_scene_node,
    final_validation_node,
    generate_dialogue_node,
    prepare_retry_node,
    should_commit_or_retry,
    should_continue_or_assemble,
    should_proceed_to_generation,
    should_proceed_to_tts,
    tts_trial_node,
    validate_duration_node,
)

try:
    from langgraph.graph import END, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

logger = get_logger()

# Progress callback type
ProgressCallback = Callable[[str, Dict[str, Any]], None]


class DurationOrchestratorAgent:
    """
 Duration Orchestrator Agent - Duan Dao Duan duration Bi Huan validation.

 through scene Ji Bi Huan validation Que Bao episode when Zhang Fu He target: 
 - Mei Ge scene Sheng Cheng after Li Ji validation when Zhang
 - not Da Biao then retry Sheng Cheng(Zui multiple3Ci)
 - Da Biao after lock and adjust subsequent scene Yu Suan
    """

    def __init__(
        self,
        script_agent=None,
        tts_service=None,
        use_actual_tts: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """
 Chu Shi Hua Duration Orchestrator.

        Args:
 script_agent: ScriptLangGraphAgent instance, Yong Yu Sheng Cheng dialogue
 tts_service: TTS service instance, Yong Yu Shi Ji when Zhang Ce Liang
 use_actual_tts: Shi Fou Shi Yong Shi Ji TTS(False then Shi Yong word count Gu Suan)
 progress_callback: Ke Xuan Jin Du Hui Diao function, Qian Ming as (event: str, data: dict) -> None
        """
        self.script_agent = script_agent
        self.tts_service = tts_service
        self.use_actual_tts = use_actual_tts
        self.progress_callback = progress_callback
        self.logger = logger

    def _emit_progress(self, event: str, data: Dict[str, Any]) -> None:
        """Emit a progress event if callback is configured."""
        if self.progress_callback:
            try:
                self.progress_callback(event, data)
            except Exception as exc:
                self.logger.warning(
                    "Progress callback failed",
                    extra={"event": event, "error": str(exc)},
                )
        # Also log the event for audit trail
        self.logger.info(
            f"duration_orchestrator_progress: {event}",
            extra={"event": event, **data},
        )

    def _build_graph(self) -> "StateGraph":
        """
 build LangGraph StateGraph.

 node Liu Cheng:
            allocate_budget
                ↓
            generate_dialogue ←─────────────┐
                ↓                           │
            tts_trial                       │
                ↓                           │
            validate_duration               │
                ↓                           │
            ┌───┴───┐                       │
            │       │                       │
        commit   prepare_retry ─────────────┘
            │
            ↓
        ┌───┴───┐
        │       │
        continue assemble_episode
        (loop)    ↓
             final_validation
                  ↓
                 END
        """
        graph = StateGraph(dict)

        # Tian Jia all node
        graph.add_node("allocate_budget", allocate_budget_node)
        graph.add_node("generate_dialogue", generate_dialogue_node)
        graph.add_node("tts_trial", tts_trial_node)
        graph.add_node("validate_duration", validate_duration_node)
        graph.add_node("commit_scene", commit_scene_node)
        graph.add_node("prepare_retry", prepare_retry_node)
        graph.add_node("assemble_episode", assemble_episode_node)
        graph.add_node("final_validation", final_validation_node)

        # She Zhi entry point Dian
        graph.set_entry_point("allocate_budget")

        # allocate_budget → generate_dialogue or assemble_episode (Kong scene Tiao Guo)
        graph.add_conditional_edges(
            "allocate_budget",
            should_proceed_to_generation,
            {
                "generate": "generate_dialogue",
                "assemble": "assemble_episode",
                "failed": END,
            },
        )

        # generate_dialogue → tts_trial or retry
        graph.add_conditional_edges(
            "generate_dialogue",
            should_proceed_to_tts,
            {
                "tts": "tts_trial",
                "retry": "generate_dialogue",
                "failed": END,
            },
        )

        # tts_trial → validate_duration
        graph.add_edge("tts_trial", "validate_duration")

        # validate_duration → commit_scene or prepare_retry
        graph.add_conditional_edges(
            "validate_duration",
            should_commit_or_retry,
            {
                "commit": "commit_scene",
                "retry": "prepare_retry",
                "next": "commit_scene",
            },
        )

        # prepare_retry → generate_dialogue (retry Sheng Cheng)
        graph.add_edge("prepare_retry", "generate_dialogue")

        # commit_scene → continue (below a scene) or assemble_episode (complete)
        graph.add_conditional_edges(
            "commit_scene",
            should_continue_or_assemble,
            {
                "continue": "generate_dialogue",
                "assemble": "assemble_episode",
            },
        )

        # assemble_episode → final_validation
        graph.add_edge("assemble_episode", "final_validation")

        # final_validation → END
        graph.add_edge("final_validation", END)

        return graph

    async def orchestrate(
        self,
        *,
        episode_id: int,
        script_id: int,
        story_id: int,
        total_duration_minutes: int,
        scenes: List[Dict[str, Any]],
        episode: Dict[str, Any],
        story: Dict[str, Any],
        generation_config: Optional[Dict[str, Any]] = None,
        voice_config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        """
 execute Duan Dao Duan duration Bi Huan validation.

        Args:
 episode_id: episode ID
 script_id: script ID
 story_id: story ID
 total_duration_minutes: target total duration(minutes)
 scenes: scene list(Lai Zi Episode Agent)
 episode: Episode data
 story: Story data
 generation_config: dialogue Sheng Cheng configuration
 voice_config: TTS voice configuration
 progress_callback: Ke Xuan Jin Du Hui Diao function(Fu Gai instance Ji Hui Diao)

        Returns:
 Bao Han all scene dialogue, when Zhang Xin Xi and Tui Li log Jie Guo Zi Dian
        """
        # Use method-level callback if provided, otherwise fall back to instance
        callback = progress_callback or self.progress_callback
        if callback and callback != self.progress_callback:
            self.progress_callback = callback

        if not LANGGRAPH_AVAILABLE:
            self.logger.error("LangGraph not available")
            return {
                "success": False,
                "error": "langgraph_not_available",
            }

        # build Chu Shi Zhuang Tai
        initial_state = {
            # basic Xin Xi
            "episode_id": episode_id,
            "script_id": script_id,
            "story_id": story_id,
            "total_duration_minutes": total_duration_minutes,
            "scenes_from_episode": scenes,
            # context data
            "episode": episode,
            "story": story,
            "generation_config": generation_config or {},
            "voice_config": voice_config or {},
            # service instance
            "script_agent": self.script_agent,
            "tts_service": self.tts_service,
            "use_actual_tts": self.use_actual_tts,
            # status Zhui Zong
            "scene_budgets": [],
            "current_scene_index": 0,
            "generated_dialogues": {},
            "committed_scenes": {},
            "phase": "allocating",
            "reasoning": [],
            "errors": [],
        }

        self.logger.info(
            "DurationOrchestratorAgent: Kai Shi Bian Pai",
            extra={
                "episode_id": episode_id,
                "total_duration_minutes": total_duration_minutes,
                "scene_count": len(scenes),
                "use_actual_tts": self.use_actual_tts,
            },
        )

        # Emit orchestration_started event
        self._emit_progress(
            "orchestration_started",
            {
                "episode_id": episode_id,
                "script_id": script_id,
                "total_duration_minutes": total_duration_minutes,
                "scene_count": len(scenes),
            },
        )

        # build and execute Tu
        graph = self._build_graph()
        app = graph.compile()

        try:
            result = await app.ainvoke(initial_state)
        except Exception as exc:
            self.logger.exception("DurationOrchestratorAgent: execute failed")
            return {
                "success": False,
                "error": str(exc),
                "reasoning": initial_state.get("reasoning", []),
            }

        # extract Jie Guo
        scene_budgets = result.get("scene_budgets", [])
        committed_scenes = result.get("committed_scenes", {})
        errors = result.get("errors", [])

        # Cong assemble_episode and final_validation node get Jie Guo
        assembled_episode = result.get("assembled_episode", {})
        final_validation = result.get("final_validation_result", {})
        statistics = result.get("statistics", {})

        # Ru Guo missing Tong Ji Xin Xi(Ke Neng Tu Wei complete execute), Shou Dong Ji Suan
        if not statistics:
            total_actual_duration = sum(
                b.actual_duration_seconds or 0 for b in scene_budgets
            )
            total_target_duration = total_duration_minutes * 60
            duration_ratio = (
                total_actual_duration / total_target_duration
                if total_target_duration > 0
                else 0
            )
            total_retries = sum(b.attempt_count for b in scene_budgets)
            avg_retries = total_retries / len(scene_budgets) if scene_budgets else 0

            statistics = {
                "total_target_duration_seconds": total_target_duration,
                "total_actual_duration_seconds": total_actual_duration,
                "duration_ratio": round(duration_ratio, 4),
                "scene_count": len(scene_budgets),
                "total_retries": total_retries,
                "avg_retries_per_scene": round(avg_retries, 2),
            }

        # Que Ding Zui Zhong successful status(Ji Yu final_validation Jie Guo)
        success = result.get("success", len(errors) == 0)
        if final_validation:
            success = final_validation.get("passed", success) and len(errors) == 0

        self.logger.info(
            "DurationOrchestratorAgent: Bian Pai complete",
            extra={
                "episode_id": episode_id,
                "scene_count": statistics.get("scene_count", len(scene_budgets)),
                "total_actual_duration": statistics.get(
                    "total_actual_duration_seconds", 0
                ),
                "total_target_duration": statistics.get(
                    "total_target_duration_seconds", 0
                ),
                "duration_ratio": statistics.get("duration_ratio", 0),
                "total_retries": statistics.get("total_retries", 0),
                "avg_retries": statistics.get("avg_retries_per_scene", 0),
                "error_count": len(errors),
                "final_validation_passed": final_validation.get("passed"),
            },
        )

        # Emit orchestration_completed event
        self._emit_progress(
            "orchestration_completed",
            {
                "episode_id": episode_id,
                "success": success,
                "scene_count": statistics.get("scene_count", len(scene_budgets)),
                "total_actual_duration_seconds": statistics.get(
                    "total_actual_duration_seconds", 0
                ),
                "total_target_duration_seconds": statistics.get(
                    "total_target_duration_seconds", 0
                ),
                "duration_ratio": statistics.get("duration_ratio", 0),
                "total_retries": statistics.get("total_retries", 0),
                "error_count": len(errors),
            },
        )

        return {
            "success": success,
            "episode_id": episode_id,
            "script_id": script_id,
            # scene Jie Guo
            "scene_budgets": [b.to_dict() for b in scene_budgets],
            "committed_scenes": committed_scenes,
            "generated_dialogues": result.get("generated_dialogues", {}),
            # assemble Jie Guo
            "assembled_episode": assembled_episode,
            # Zui Zhong validation Jie Guo
            "final_validation": final_validation,
            # Tong Ji Xin Xi
            "statistics": statistics,
            # log
            "reasoning": result.get("reasoning", []),
            "errors": errors,
        }


async def orchestrate_episode_duration(
    *,
    episode_id: int,
    script_id: int,
    story_id: int,
    total_duration_minutes: int,
    scenes: List[Dict[str, Any]],
    episode: Dict[str, Any],
    story: Dict[str, Any],
    script_agent=None,
    tts_service=None,
    use_actual_tts: bool = False,
    generation_config: Optional[Dict[str, Any]] = None,
    voice_config: Optional[Dict[str, Any]] = None,
    progress_callback: Optional[ProgressCallback] = None,
) -> Dict[str, Any]:
    """
 Bian Jie function: execute episode when Zhang Bian Pai.

 Zhe Shi DurationOrchestratorAgent.orchestrate() Jian Hua Feng Zhuang.

    Args:
 episode_id: episode ID
 script_id: script ID
 story_id: story ID
 total_duration_minutes: target total duration(minutes)
 scenes: scene list(Lai Zi Episode Agent)
 episode: Episode data
 story: Story data
 script_agent: ScriptLangGraphAgent instance
 tts_service: TTS service instance
 use_actual_tts: Shi Fou Shi Yong Shi Ji TTS
 generation_config: dialogue Sheng Cheng configuration
 voice_config: TTS voice configuration
 progress_callback: Jin Du Hui Diao function (event: str, data: dict) -> None

    Returns:
 Bao Han all scene dialogue, when Zhang Xin Xi and Tui Li log Jie Guo Zi Dian
    """
    agent = DurationOrchestratorAgent(
        script_agent=script_agent,
        tts_service=tts_service,
        use_actual_tts=use_actual_tts,
        progress_callback=progress_callback,
    )

    return await agent.orchestrate(
        episode_id=episode_id,
        script_id=script_id,
        story_id=story_id,
        total_duration_minutes=total_duration_minutes,
        scenes=scenes,
        episode=episode,
        story=story,
        generation_config=generation_config,
        voice_config=voice_config,
    )
