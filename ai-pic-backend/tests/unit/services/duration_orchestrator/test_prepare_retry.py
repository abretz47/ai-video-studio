"""
retry Zhun Bei Jie Dian Dan Yuan Ce Shi

test Duration Orchestrator retry Zhun Bei logic。
"""

import pytest
from app.services.duration_orchestrator.constants import MAX_RETRY_ATTEMPTS
from app.services.duration_orchestrator.nodes.prepare_retry import (
    prepare_retry_node,
    should_retry_or_fail,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus


class TestPrepareRetryNode:
    """test retry Zhun Bei Jie Dian"""

    @pytest.fixture
    def base_state(self):
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
                    actual_duration_seconds=30,  # Tai Duan
                    actual_word_count=68,
                    attempt_count=1,
                ),
            ],
            "current_scene_index": 0,
            "generated_dialogues": {
                1: [{"scene_number": 1, "content": "test dialogue"}],
            },
            "reasoning": [],
        }

    def test_generates_adjustment_hint(self, base_state):
        """generate Tiao Zheng Jian Yi"""
        result = prepare_retry_node(base_state)

        budget = result["scene_budgets"][0]
        assert budget.adjustment_hint is not None
        assert budget.last_rejection_reason == "duration_too_short"

    def test_clears_generated_dialogues(self, base_state):
        """Qing Kong already generate dialogue"""
        result = prepare_retry_node(base_state)

        assert 1 not in result["generated_dialogues"]

    def test_status_remains_pending(self, base_state):
        """status keep for Dai Chu Li"""
        result = prepare_retry_node(base_state)

        budget = result["scene_budgets"][0]
        assert budget.status == SceneStatus.PENDING

    def test_updates_reasoning(self, base_state):
        """update Tui Li Ri Zhi"""
        result = prepare_retry_node(base_state)

        assert len(result["reasoning"]) > 0
        assert "retry" in result["reasoning"][0]

    def test_force_commit_at_max_retries(self, base_state):
        """Da Dao Zui Da retry Ci Shu when Qiang Zhi Ti Jiao"""
        base_state["scene_budgets"][0].attempt_count = MAX_RETRY_ATTEMPTS

        result = prepare_retry_node(base_state)

        budget = result["scene_budgets"][0]
        assert budget.status == SceneStatus.COMMITTED
        assert budget.last_rejection_reason == "max_retries_exceeded"

    def test_index_out_of_bounds(self, base_state):
        """Suo Yin Yue Jie when return Kong"""
        base_state["current_scene_index"] = 99

        result = prepare_retry_node(base_state)

        assert result == {}

    def test_duration_too_long_hint(self, base_state):
        """when Zhang Guo Chang Tiao Zheng Jian Yi"""
        base_state["scene_budgets"][0].actual_duration_seconds = 90  # Tai Zhang
        base_state["scene_budgets"][0].actual_word_count = 200

        result = prepare_retry_node(base_state)

        budget = result["scene_budgets"][0]
        assert budget.last_rejection_reason == "duration_too_long"
        assert "Shan Jian" in budget.adjustment_hint


class TestShouldRetryOrFail:
    """test Lu You Han Shu"""

    def test_retry_when_pending(self):
        """Dai Chu Li when retry"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                    status=SceneStatus.PENDING,
                    attempt_count=1,
                ),
            ],
            "current_scene_index": 0,
        }

        result = should_retry_or_fail(state)

        assert result == "retry"

    def test_commit_when_committed(self):
        """already Ti Jiao when return commit"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                    status=SceneStatus.COMMITTED,
                ),
            ],
            "current_scene_index": 0,
        }

        result = should_retry_or_fail(state)

        assert result == "commit"

    def test_commit_at_max_retries(self):
        """Da Dao Zui Da retry Ci Shu when return commit"""
        state = {
            "scene_budgets": [
                SceneBudget(
                    scene_number=1,
                    scene_index=0,
                    target_duration_seconds=60,
                    target_word_count=135,
                    min_duration_seconds=51,
                    max_duration_seconds=69,
                    status=SceneStatus.PENDING,
                    attempt_count=MAX_RETRY_ATTEMPTS,
                ),
            ],
            "current_scene_index": 0,
        }

        result = should_retry_or_fail(state)

        assert result == "commit"

    def test_commit_when_index_exceeds(self):
        """Suo Yin Chao Chu when return commit"""
        state = {
            "scene_budgets": [],
            "current_scene_index": 0,
        }

        result = should_retry_or_fail(state)

        assert result == "commit"
