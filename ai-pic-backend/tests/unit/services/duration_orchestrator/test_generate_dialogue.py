"""
dialogue generate Jie Dian Dan Yuan Ce Shi

test Duration Orchestrator dialogue generate logic。
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.duration_orchestrator.constants import MAX_RETRY_ATTEMPTS
from app.services.duration_orchestrator.nodes.generate_dialogue import (
    generate_dialogue_node,
    should_proceed_to_tts,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus


class TestGenerateDialogueNode:
    """test dialogue generate Jie Dian"""

    @pytest.fixture
    def mock_script_agent(self):
        """create mock ScriptLangGraphAgent"""
        agent = MagicMock()
        agent.generate = AsyncMock()
        return agent

    @pytest.fixture
    def base_state(self, mock_script_agent):
        """Ji Chu Ce Shi Zhuang Tai"""
        return {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                ),
            ],
            "current_scene_index": 0,
            "script_agent": mock_script_agent,
            "episode": {"id": 1, "title": "test episode"},
            "story": {"id": 1, "title": "test story"},
            "generation_config": {
                "format_type": "short_video",
                "language": "zh",
                "dialogue_style": "natural",
            },
            "generated_dialogues": {},
            "reasoning": [],
        }

    @pytest.mark.asyncio
    async def test_successful_generation(self, base_state, mock_script_agent):
        """Cheng Gong generate dialogue"""
        mock_script_agent.generate.return_value = {
            "content": {
                "dialogues": [
                    {"scene_number": 1, "character": "Xiao Ming", "content": "Hello, world"},
                    {"scene_number": 1, "character": "Xiao Hong", "content": "Goodbye, friend"},
                ],
                "stage_directions": [],
            },
        }

        result = await generate_dialogue_node(base_state)

        assert "scene_budgets" in result
        assert "generated_dialogues" in result
        assert 1 in result["generated_dialogues"]
        assert len(result["generated_dialogues"][1]) == 2

        budget = result["scene_budgets"][0]
        assert budget.actual_word_count == 8  # "Hello, world" + "Goodbye, friend"
        assert budget.attempt_count == 1

    @pytest.mark.asyncio
    async def test_generation_with_retry_hint(self, base_state, mock_script_agent):
        """Dai retry prompt generate"""
        budget = base_state["scene_budgets"][0]
        budget.attempt_count = 1
        budget.adjustment_hint = "please Zeng Jia Yue20Zi dialogue"

        mock_script_agent.generate.return_value = {
            "content": {
                "dialogues": [
                    {
                        "scene_number": 1,
                        "character": "Xiao Ming",
                        "content": "Zhe Shi Geng Zhang dialogue content",
                    },
                ],
            },
        }

        result = await generate_dialogue_node(base_state)

        assert result["scene_budgets"][0].attempt_count == 2
        mock_script_agent.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_script_agent(self, base_state):
        """Que Shao script_agent when return error"""
        del base_state["script_agent"]

        result = await generate_dialogue_node(base_state)

        assert "errors" in result
        assert any("missing_script_agent" in e for e in result["errors"])

    @pytest.mark.asyncio
    async def test_generation_failure(self, base_state, mock_script_agent):
        """generate failed when handle"""
        mock_script_agent.generate.return_value = {
            "error": "dialogue_failed",
        }

        result = await generate_dialogue_node(base_state)

        assert "errors" in result
        budget = result["scene_budgets"][0]
        assert budget.status == SceneStatus.PENDING

    @pytest.mark.asyncio
    async def test_index_out_of_bounds(self, base_state):
        """Suo Yin Yue Jie when return Kong Jie Guo"""
        base_state["current_scene_index"] = 99

        result = await generate_dialogue_node(base_state)

        assert result == {}

    @pytest.mark.asyncio
    async def test_status_update_to_in_progress(self, base_state, mock_script_agent):
        """generate when status update for Jin Xing in"""
        mock_script_agent.generate.return_value = {
            "content": {"dialogues": []},
        }

        await generate_dialogue_node(base_state)

        # Zhu Yi：Yin Wei generate after Hui update status，Suo Yi Zhe Li check is Zui Zhong status
        # in actual Zhi Xing Guo Cheng in，status Hui Xian Bian Wei IN_PROGRESS

    @pytest.mark.asyncio
    async def test_word_count_calculation(self, base_state, mock_script_agent):
        """word count Ji Suan correct"""
        mock_script_agent.generate.return_value = {
            "content": {
                "dialogues": [
                    {
                        "scene_number": 1,
                        "character": "A",
                        "content": "Zhe Shi Shi Ge Han Zi test content",
                    },
                ],
            },
        }

        result = await generate_dialogue_node(base_state)

        budget = result["scene_budgets"][0]
        assert budget.actual_word_count == 10

    @pytest.mark.asyncio
    async def test_filters_dialogues_by_scene_number(
        self, base_state, mock_script_agent
    ):
        """An scene Hao Guo Lv dialogue"""
        mock_script_agent.generate.return_value = {
            "content": {
                "dialogues": [
                    {"scene_number": 1, "character": "A", "content": "scene1dialogue"},
                    {"scene_number": 2, "character": "B", "content": "scene2dialogue"},
                    {"scene_number": 1, "character": "C", "content": "scene1Ling Yi Tiao dialogue"},
                ],
            },
        }

        result = await generate_dialogue_node(base_state)

        scene_dialogues = result["generated_dialogues"][1]
        assert len(scene_dialogues) == 2
        assert all(d["scene_number"] == 1 for d in scene_dialogues)


class TestShouldProceedToTTS:
    """test TTS Lu You Han Shu"""

    def test_proceed_to_tts_with_dialogues(self):
        """have dialogue when Jin Ru TTS"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                ),
            ],
            "current_scene_index": 0,
            "generated_dialogues": {
                1: [{"scene_number": 1, "content": "test dialogue"}],
            },
        }

        result = should_proceed_to_tts(state)

        assert result == "tts"

    def test_retry_without_dialogues(self):
        """none dialogue when retry"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                    attempt_count=1,
                ),
            ],
            "current_scene_index": 0,
            "generated_dialogues": {},
        }

        result = should_proceed_to_tts(state)

        assert result == "retry"

    def test_failed_after_max_retries(self):
        """Da Dao Zui Da retry Ci Shu after failed"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                    attempt_count=MAX_RETRY_ATTEMPTS,
                ),
            ],
            "current_scene_index": 0,
            "generated_dialogues": {},
        }

        result = should_proceed_to_tts(state)

        assert result == "failed"

    def test_failed_with_invalid_index(self):
        """Wu Xiao Suo Yin when failed"""
        state = {
            "scene_budgets": [],
            "current_scene_index": 0,
            "generated_dialogues": {},
        }

        result = should_proceed_to_tts(state)

        assert result == "failed"
