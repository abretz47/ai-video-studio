"""
ScriptLangGraphAgent word count Yue Shu Dan Yuan Ce Shi

test ScriptLangGraphAgent De word count Yue Shu integration.
"""

from unittest.mock import MagicMock

import pytest
from app.services.duration_orchestrator.state import SceneBudget
from app.services.script_agent import ScriptLangGraphAgent


class TestBuildWordCountConstraints:
 """test word count Yue Shu Gou Jian"""

 @pytest.fixture
 def mock_service(self):
 """create mock De AIService"""
 service = MagicMock()
 service.ai_manager = MagicMock()
 return service

 @pytest.fixture
 def agent(self, mock_service):
 """create ScriptLangGraphAgent Shi Li"""
 return ScriptLangGraphAgent(mock_service)

 def test_empty_budgets_returns_empty_string(self, agent):
 """Kong Yu Suan list return Kong Zi Fu Chuan"""
 result = agent._build_word_count_constraints([], [])
 assert result == ""

 def test_single_budget_constraint(self, agent):
 """Dan scene Yu Suan Yue Shu"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
),
 ]
 scenes = [{"scene_number": 1, "summary": "Ce Shi Chang Jing"}]

 result = agent._build_word_count_constraints(budgets, scenes)

 assert "60 seconds" in result
 assert "135" in result
 assert "51" in result
 assert "69" in result

 def test_multiple_budget_constraints(self, agent):
 """Duo scene Yu Suan Yue Shu"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=30,
 target_word_count=68,
 min_duration_seconds=26,
 max_duration_seconds=35,
),
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
),
 ]
 scenes = [
 {"scene_number": 1, "summary": "scene1"},
 {"scene_number": 2, "summary": "scene2"},
 ]

 result = agent._build_word_count_constraints(budgets, scenes)

 assert "scene 1" in result
 assert "scene 2" in result
 assert "30 seconds" in result
 assert "60 seconds" in result

 def test_retry_hint_included(self, agent):
 """retry prompt Bei Bao Han"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 attempt_count=1,
 adjustment_hint="Qing Zeng Jia Yue30Zi De Dui Bai",
),
 ]
 scenes = [{"scene_number": 1}]

 result = agent._build_word_count_constraints(budgets, scenes)

 assert "Tiao Zheng Jian Yi" in result
 assert "Zeng Jia Yue30character" in result
 assert "Di 2 Ci Zhong Shi" in result

 def test_no_retry_hint_for_first_attempt(self, agent):
 """Shou Ci Chang Shi Bu Bao Han retry prompt"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 attempt_count=0, # Shou Ci Chang Shi
),
 ]
 scenes = [{"scene_number": 1}]

 result = agent._build_word_count_constraints(budgets, scenes)

 assert "Tiao Zheng Jian Yi" not in result


class TestGenerateMethodSignature:
 """test generate Fang Fa Qian Ming"""

 @pytest.fixture
 def mock_service(self):
 """create mock De AIService"""
 service = MagicMock()
 service.ai_manager = None # Mo Ni Wu AI manager
 return service

 @pytest.fixture
 def agent(self, mock_service):
 """create ScriptLangGraphAgent Shi Li"""
 return ScriptLangGraphAgent(mock_service)

 @pytest.mark.asyncio
 async def test_accepts_scene_budgets_parameter(self, agent):
 """Jie Shou scene_budgets Can Shu"""
 budgets = [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
),
 ]

 # Ying Gai Neng normal call, Bu Hui Pao Chu Can Shu error
 # Yin Wei Mei You ai_manager, Hui Fan Hui None
 result = await agent.generate(
 episode={"id": 1},
 story={"id": 1},
 format_type="short_video",
 language="zh",
 dialogue_style="natural",
 scene_detail_level="detailed",
 additional_requirements=None,
 style_preferences=None,
 model=None,
 prefer_provider=None,
 temperature=0.7,
 scene_budgets=budgets,
)

 # none AI manager Shi Fan Hui None
 assert result is None

 @pytest.mark.asyncio
 async def test_scene_budgets_optional(self, agent):
 """scene_budgets Can Shu Ke Xuan"""
 # Bu Chuan scene_budgets Ying Gai Ye Neng normal call
 result = await agent.generate(
 episode={"id": 1},
 story={"id": 1},
 format_type="short_video",
 language="zh",
 dialogue_style="natural",
 scene_detail_level="detailed",
 additional_requirements=None,
 style_preferences=None,
 model=None,
 prefer_provider=None,
 temperature=0.7,
)

 # none AI manager Shi Fan Hui None
 assert result is None


class TestEstimateDialogueDuration:
 """test dialogue Shi length Gu Suan De Lu Bang Xing"""

 @pytest.fixture
 def mock_service(self):
 service = MagicMock()
 service.ai_manager = MagicMock()
 return service

 @pytest.fixture
 def agent(self, mock_service):
 return ScriptLangGraphAgent(mock_service)

 def test_string_scene_number_is_counted(self, agent):
 dialogues = [
 {"scene_number": "1", "content": "1234"},
 {"scene_number": 2, "content": "5678"},
 ]
 assert agent._estimate_dialogue_duration(dialogues, 1) > 0


class TestCharacterValidation:
 """test character Jiao Yan Jie Guo character Duan"""

 @pytest.fixture
 def agent(self):
 service = MagicMock()
 service.ai_manager = MagicMock()
 return ScriptLangGraphAgent(service)

 def test_unknown_speakers_are_returned_as_unknown_names(self, agent):
 content = {
 "dialogues": [
 {"scene_number": 1, "character": "Chen Zhe", "content": "Wo Lai Chu Li."},
 {"scene_number": 1, "character": "Stranger", "content": "Gen Wo Zou."},
 {"scene_number": 1, "character": "voiceover", "content": "Ye Se Ya Di."},
 ]
 }

 result = agent._validate_script_characters(content, [{"name": "Chen Zhe"}])

 assert result["character_validation_passed"] is False
 assert result["unknown_names"] == ["Stranger"]
 assert "Stranger" in result["character_warnings"][0]
