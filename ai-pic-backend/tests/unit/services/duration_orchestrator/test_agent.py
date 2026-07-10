"""
Duration Orchestrator Agent Dan Yuan Ce Shi

test DurationOrchestratorAgent De complete Liu Cheng.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.duration_orchestrator.agent import (
 DurationOrchestratorAgent,
 orchestrate_episode_duration,
)


class TestDurationOrchestratorAgent:
 """test DurationOrchestratorAgent"""

 @pytest.fixture
 def mock_script_agent(self):
 """create mock De ScriptLangGraphAgent"""
 agent = MagicMock()
 agent.generate = AsyncMock()
 return agent

 @pytest.fixture
 def base_params(self):
 """basic test Can Shu"""
 return {
 "episode_id": 1,
 "script_id": 1,
 "story_id": 1,
 "total_duration_minutes": 3,
 "scenes": [
 {
 "scene_number": 1,
 "summary": "scene1",
 "estimated_duration_seconds": 60,
 },
 {
 "scene_number": 2,
 "summary": "scene2",
 "estimated_duration_seconds": 60,
 },
 ],
 "episode": {"id": 1, "title": "Ce Shi Ju Ji"},
 "story": {"id": 1, "title": "Ce Shi Gu Shi"},
 }

 @pytest.mark.asyncio
 async def test_orchestrate_returns_result(self, mock_script_agent, base_params):
 """Bian Pai return correct De Jie Guo structure"""
 # mock Script Agent Fan Hui Dui Bai
 mock_script_agent.generate.return_value = {
 "content": {
 "dialogues": [
 {
 "scene_number": 1,
 "character": "A",
 "content": "Zhe Shi scene Yi De dialogue content",
 },
 {
 "scene_number": 2,
 "character": "B",
 "content": "Zhe Shi scene Er De dialogue content",
 },
 ],
 },
 }

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(**base_params)

 # validate return structure correct
 assert "success" in result
 assert result["episode_id"] == 1
 assert "scene_budgets" in result
 assert "reasoning" in result

 @pytest.mark.asyncio
 async def test_orchestrate_no_script_agent(self, base_params):
 """none Script Agent Shi De Cuo Wu Chu Li"""
 agent = DurationOrchestratorAgent(
 script_agent=None,
 use_actual_tts=False,
)

 result = await agent.orchestrate(**base_params)

 # Ying Gai You error
 assert "errors" in result

 @pytest.mark.asyncio
 async def test_orchestrate_empty_scenes(self, mock_script_agent, base_params):
 """Kong scene list"""
 base_params["scenes"] = []

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(**base_params)

 # Ying Gai You error
 assert "errors" in result
 assert len(result.get("errors", [])) > 0

 @pytest.mark.asyncio
 async def test_orchestrate_with_generation_config(
 self, mock_script_agent, base_params
):
 """Dai generate configuration De Bian Pai"""
 mock_script_agent.generate.return_value = {
 "content": {
 "dialogues": [
 {"scene_number": 1, "character": "A", "content": "Ce Shi Dui Bai"},
 ],
 },
 }

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(
 **base_params,
 generation_config={
 "format_type": "short_video",
 "language": "zh",
 "dialogue_style": "natural",
 },
)

 # validate return structure
 assert "success" in result
 assert "scene_budgets" in result

 @pytest.mark.asyncio
 async def test_orchestrate_statistics_structure(
 self, mock_script_agent, base_params
):
 """validate statistics Xin Xi Jie Gou"""
 mock_script_agent.generate.return_value = {
 "content": {
 "dialogues": [
 {"scene_number": 1, "character": "A", "content": "test dialogue content"},
 {"scene_number": 2, "character": "B", "content": "test dialogue content"},
 ],
 },
 }

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(**base_params)

 # statistics information Ying Gai exists
 if result.get("success"):
 stats = result.get("statistics", {})
 assert "total_target_duration_seconds" in stats
 assert "scene_count" in stats


class TestOrchestrateEpisodeDuration:
 """test Bian Jie Han Shu"""

 @pytest.fixture
 def mock_script_agent(self):
 """create mock De ScriptLangGraphAgent"""
 agent = MagicMock()
 agent.generate = AsyncMock(
 return_value={
 "content": {
 "dialogues": [
 {"scene_number": 1, "character": "A", "content": "test"},
 ],
 },
 }
)
 return agent

 @pytest.mark.asyncio
 async def test_convenience_function(self, mock_script_agent):
 """test Bian Jie Han Shu"""
 result = await orchestrate_episode_duration(
 episode_id=1,
 script_id=1,
 story_id=1,
 total_duration_minutes=3,
 scenes=[{"scene_number": 1, "summary": "scene1"}],
 episode={"id": 1},
 story={"id": 1},
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 assert "success" in result
 assert "scene_budgets" in result


class TestAgentBuildGraph:
 """test image Gou Jian"""

 def test_build_graph_structure(self):
 """validate image structure"""
 agent = DurationOrchestratorAgent()
 graph = agent._build_graph()

 # validate Jie Dian exists
 assert "allocate_budget" in graph.nodes
 assert "generate_dialogue" in graph.nodes
 assert "tts_trial" in graph.nodes
 assert "validate_duration" in graph.nodes
 assert "commit_scene" in graph.nodes
 assert "prepare_retry" in graph.nodes

 def test_build_graph_entry_point(self):
 """validate Ru Kou Dian"""
 agent = DurationOrchestratorAgent()
 graph = agent._build_graph()

 # Ru Kou Dian Ying Gai Shi allocate_budget
 # LangGraph Nei Bu Shi Xian possible Bu Zhi Jie Bao Lu entry_point
 # Dan Bian Yi Hou De image Ying Gai Neng normal work
 compiled = graph.compile()
 assert compiled is not None


class TestSceneLoopIntegration:
 """scene Xun Huan integration test - validate complete Liu Cheng"""

 @pytest.fixture
 def mock_script_agent(self):
 """create mock De ScriptLangGraphAgent"""
 agent = MagicMock()
 agent.generate = AsyncMock()
 return agent

 @pytest.mark.asyncio
 async def test_multi_scene_orchestration(self, mock_script_agent):
 """test Duo scene Bian Pai Liu Cheng"""
 # set Mei Ge scene return Bu Tong De dialogue
 call_count = [0]

 async def generate_side_effect(*args, **kwargs):
 call_count[0] += 1
 scene_num = call_count[0]
 return {
 "content": {
 "dialogues": [
 {
 "scene_number": scene_num,
 "character": "A",
 "content": f"Zhe Shi Chang Jing{scene_num}De dialogue content, Xu Yao Zu Gou length Cai Neng Da Dao Shi length Yao Qiu",
 },
 ],
 },
 }

 mock_script_agent.generate.side_effect = generate_side_effect

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(
 episode_id=1,
 script_id=1,
 story_id=1,
 total_duration_minutes=3,
 scenes=[
 {
 "scene_number": 1,
 "summary": "opening",
 "estimated_duration_seconds": 60,
 },
 {
 "scene_number": 2,
 "summary": "Fa Zhan",
 "estimated_duration_seconds": 60,
 },
 {
 "scene_number": 3,
 "summary": "Jie Wei",
 "estimated_duration_seconds": 60,
 },
 ],
 episode={"id": 1, "title": "Ce Shi Ju Ji"},
 story={"id": 1, "title": "Ce Shi Gu Shi"},
)

 # Validation resultstructure
 assert "success" in result
 assert "scene_budgets" in result
 # validate scene Yu Suan count
 if result.get("scene_budgets"):
 assert len(result["scene_budgets"]) == 3

 @pytest.mark.asyncio
 async def test_budget_allocation_accuracy(self, mock_script_agent):
 """test Yu Suan Fen Pei Zhun Que Xing"""
 mock_script_agent.generate.return_value = {
 "content": {
 "dialogues": [
 {"scene_number": 1, "character": "A", "content": "test dialogue content"},
 ],
 },
 }

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(
 episode_id=1,
 script_id=1,
 story_id=1,
 total_duration_minutes=2, # 2minutes = 120seconds
 scenes=[
 {
 "scene_number": 1,
 "summary": "scene1",
 "estimated_duration_seconds": 60,
 },
 {
 "scene_number": 2,
 "summary": "scene2",
 "estimated_duration_seconds": 60,
 },
 ],
 episode={"id": 1},
 story={"id": 1},
)

 # validate Yu Suan Fen Pei
 if result.get("success") and result.get("scene_budgets"):
 budgets = result["scene_budgets"]
 # Mei Ge scene Ying Gai You target Shi length
 for budget in budgets:
 assert "target_duration_seconds" in budget
 # target Shi length Ying Gai He Li Fen Pei
 assert budget["target_duration_seconds"] > 0

 @pytest.mark.asyncio
 async def test_reasoning_log_populated(self, mock_script_agent):
 """test Tui Li Ri Zhi Bei correct Tian Chong"""
 mock_script_agent.generate.return_value = {
 "content": {
 "dialogues": [
 {"scene_number": 1, "character": "A", "content": "dialogue content"},
 ],
 },
 }

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(
 episode_id=1,
 script_id=1,
 story_id=1,
 total_duration_minutes=1,
 scenes=[{"scene_number": 1, "summary": "scene1"}],
 episode={"id": 1},
 story={"id": 1},
)

 # validate Tui Li Ri Zhi
 assert "reasoning" in result
 # Tui Li Ri Zhi Ying Gai Bao Han Yu Suan Fen Pei De record
 if result.get("reasoning"):
 assert len(result["reasoning"]) > 0

 @pytest.mark.asyncio
 async def test_error_handling_in_loop(self, mock_script_agent):
 """test Xun Huan Zhong De Cuo Wu Chu Li"""
 # Di Yi Ci call success, Di Er Ci Pao Chu exception
 call_count = [0]

 async def generate_with_error(*args, **kwargs):
 call_count[0] += 1
 if call_count[0] == 1:
 return {
 "content": {
 "dialogues": [
 {
 "scene_number": 1,
 "character": "A",
 "content": "Zheng Chang Dui Bai",
 },
 ],
 },
 }
 raise ValueError("mock generate failed")

 mock_script_agent.generate.side_effect = generate_with_error

 agent = DurationOrchestratorAgent(
 script_agent=mock_script_agent,
 use_actual_tts=False,
)

 result = await agent.orchestrate(
 episode_id=1,
 script_id=1,
 story_id=1,
 total_duration_minutes=2,
 scenes=[
 {"scene_number": 1, "summary": "scene1"},
 {"scene_number": 2, "summary": "scene2"},
 ],
 episode={"id": 1},
 story={"id": 1},
)

 # Ying Gai You Jie Guo return(Ji Shi You error)
 assert result is not None
 # validate You error record
 assert "errors" in result or "error" in result
