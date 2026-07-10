"""
TTS Shi Pao Jie Dian Dan Yuan Ce Shi

test Duration Orchestrator De TTS Shi length Gu Suan logic.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.duration_orchestrator.constants import WORDS_PER_SECOND
from app.services.duration_orchestrator.nodes.tts_trial import (
 estimate_duration_from_dialogues,
 tts_trial_node,
)
from app.services.duration_orchestrator.state import SceneBudget


class TestEstimateDurationFromDialogues:
 """test dialogue Shi length Gu Suan"""

 def test_estimate_normal_dialogues(self):
 """normal dialogue De duration Gu Suan"""
 dialogues = [
 {"character": "Xiao Ming", "content": "Hello, world"}, # 4 chars
 {"character": "Xiao Hong", "content": "Goodbye, friend"}, # 4 chars
 ]
 # 8 chars / WORDS_PER_SECOND chars/s
 duration_ms = estimate_duration_from_dialogues(dialogues)
 assert 1600 <= duration_ms <= 1800

 def test_estimate_empty_dialogues(self):
 """Kong dialogue list"""
 duration_ms = estimate_duration_from_dialogues([])
 assert duration_ms == 0

 def test_estimate_with_custom_rate(self):
 """Zi Ding Yi speech rate"""
 dialogues = [{"content": "test content test content"}] # 8 chars
 # 8 chars / 4 chars/s = 2s = 2000ms
 duration_ms = estimate_duration_from_dialogues(dialogues, speaking_rate=4.0)
 assert duration_ms == 2000

 def test_estimate_long_dialogue(self):
 """length dialogue De duration Gu Suan"""
 # int(60 * WORDS_PER_SECOND) chars should be ~60 seconds
 long_text = "A" * int(60 * WORDS_PER_SECOND)
 dialogues = [{"content": long_text}]
 duration_ms = estimate_duration_from_dialogues(dialogues)
 assert 58000 <= duration_ms <= 62000 # ~60 seconds


class TestTtsTrialNode:
 """test TTS Shi Pao Jie Dian"""

 @pytest.fixture
 def base_state(self):
 """basic Ce Shi Zhuang Tai"""
 return {
 "scene_budgets": [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=int(60 * WORDS_PER_SECOND),
 min_duration_seconds=51,
 max_duration_seconds=69,
),
 ],
 "current_scene_index": 0,
 "generated_dialogues": {
 1: [
 {"scene_number": 1, "character": "Xiao Ming", "content": "Hello, world"},
 {"scene_number": 1, "character": "Xiao Hong", "content": "Goodbye, friend"},
 ],
 },
 "reasoning": [],
 "use_actual_tts": False,
 }

 @pytest.mark.asyncio
 async def test_estimate_mode(self, base_state):
 """Gu Suan Mo Shi"""
 result = await tts_trial_node(base_state)

 assert "scene_budgets" in result
 budget = result["scene_budgets"][0]
 assert budget.actual_duration_seconds is not None
 assert budget.actual_duration_seconds > 0

 @pytest.mark.asyncio
 async def test_updates_reasoning(self, base_state):
 """update Tui Li Ri Zhi"""
 result = await tts_trial_node(base_state)

 assert "reasoning" in result
 assert len(result["reasoning"]) > 0
 assert "Zi Shu Gu Suan" in result["reasoning"][0]

 @pytest.mark.asyncio
 async def test_no_dialogues(self, base_state):
 """none dialogue Shi return Kong"""
 base_state["generated_dialogues"] = {}

 result = await tts_trial_node(base_state)

 assert result == {}

 @pytest.mark.asyncio
 async def test_index_out_of_bounds(self, base_state):
 """Suo Yin Yue Jie"""
 base_state["current_scene_index"] = 99

 result = await tts_trial_node(base_state)

 assert result == {}

 @pytest.mark.asyncio
 async def test_actual_tts_mode_fallback(self, base_state):
 """actual TTS Mo Shi Jiang Ji Wei Gu Suan"""
 base_state["use_actual_tts"] = True
 # Mei You tts_service, Ying Gai Jiang Ji Wei Gu Suan Mo Shi

 result = await tts_trial_node(base_state)

 assert "scene_budgets" in result
 budget = result["scene_budgets"][0]
 assert budget.actual_duration_seconds is not None

 @pytest.mark.asyncio
 async def test_actual_tts_mode_with_service(self, base_state):
 """actual TTS Mo Shi You service"""
 mock_tts_service = MagicMock()
 mock_tts_service.generate_speech = AsyncMock(
 return_value={"duration": 2.5} # 2.5 seconds
)

 base_state["use_actual_tts"] = True
 base_state["tts_service"] = mock_tts_service
 base_state["voice_config"] = {"voice_type": "test"}

 result = await tts_trial_node(base_state)

 assert "scene_budgets" in result
 budget = result["scene_budgets"][0]
 assert budget.actual_duration_seconds is not None
 # TTS was called
 assert mock_tts_service.generate_speech.called

 @pytest.mark.asyncio
 async def test_calculates_deviation(self, base_state):
 """Ji Suan Pian Cha"""
 result = await tts_trial_node(base_state)

 # 8 chars / WORDS_PER_SECOND, target is 60s
 # deviation should be negative (too short)
 budget = result["scene_budgets"][0]
 assert budget.actual_duration_seconds < budget.target_duration_seconds
