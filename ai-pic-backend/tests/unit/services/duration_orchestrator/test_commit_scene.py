"""
scene Ti Jiao Jie Dian Dan Yuan Ce Shi

test Duration Orchestrator De scene Ti Jiao He Yu Suan Zai Ping Heng logic.
"""

import pytest
from app.services.duration_orchestrator.nodes.commit_scene import (
 commit_scene_node,
 should_continue_or_assemble,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus


class TestCommitSceneNode:
 """test scene Ti Jiao Jie Dian"""

 @pytest.fixture
 def base_state(self):
 """basic Ce Shi Zhuang Tai"""
 return {
 "scene_budgets": [
 SceneBudget(
 scene_number=1,
 scene_index=0,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 actual_duration_seconds=55,
 attempt_count=1,
),
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
),
 ],
 "current_scene_index": 0,
 "generated_dialogues": {
 1: [{"scene_number": 1, "content": "Ce Shi Dui Bai"}],
 },
 "committed_scenes": {},
 "reasoning": [],
 }

 def test_commit_scene_status(self, base_state):
 """Ti Jiao Hou status Bian Wei COMMITTED"""
 result = commit_scene_node(base_state)

 budget = result["scene_budgets"][0]
 assert budget.status == SceneStatus.COMMITTED

 def test_commit_saves_scene_data(self, base_state):
 """Ti Jiao Hou Bao Cun scene data"""
 result = commit_scene_node(base_state)

 assert 1 in result["committed_scenes"]
 committed = result["committed_scenes"][1]
 assert committed["scene_number"] == 1
 assert committed["target_duration_seconds"] == 60
 assert committed["actual_duration_seconds"] == 55
 assert committed["deviation_seconds"] == -5
 assert committed["attempt_count"] == 1

 def test_commit_moves_to_next_scene(self, base_state):
 """Ti Jiao Hou Yi Dong to Xia Yi Ge scene"""
 result = commit_scene_node(base_state)

 assert result["current_scene_index"] == 1

 def test_commit_triggers_rebalance_when_over(self, base_state):
 """timeout Shi Chu Fa Zai Ping Heng"""
 # scene1actual70seconds, target60seconds, timeout10seconds
 base_state["scene_budgets"][0].actual_duration_seconds = 70

 result = commit_scene_node(base_state)

 # scene2De target Ying Gai Bei Tiao Zheng(Jian Shao5seconds, Yin Wei You1Ge Hou Xu scene)
 budget2 = result["scene_budgets"][1]
 assert budget2.target_duration_seconds == 50 # 60 - 10

 def test_commit_triggers_rebalance_when_under(self, base_state):
 """Qian Shi Shi Chu Fa Zai Ping Heng"""
 # scene1actual40seconds, target60seconds, Qian Shi20seconds
 base_state["scene_budgets"][0].actual_duration_seconds = 40

 result = commit_scene_node(base_state)

 # scene2De target Ying Gai Bei Tiao Zheng(increase20seconds)
 budget2 = result["scene_budgets"][1]
 assert budget2.target_duration_seconds == 80 # 60 + 20

 def test_commit_no_rebalance_for_last_scene(self, base_state):
 """final Yi Ge scene Bu Chu Fa Zai Ping Heng"""
 base_state["current_scene_index"] = 1
 base_state["scene_budgets"][1].actual_duration_seconds = 70

 result = commit_scene_node(base_state)

 # Mei You Hou Xu scene, Bu Xu Yao Zai Ping Heng
 assert result["current_scene_index"] == 2

 def test_commit_updates_reasoning(self, base_state):
 """Ti Jiao Hou update Tui Li Ri Zhi"""
 result = commit_scene_node(base_state)

 assert len(result["reasoning"]) > 0
 assert "Yi Ti Jiao" in result["reasoning"][0]

 def test_commit_index_out_of_bounds(self, base_state):
 """Suo Yin Yue Jie Shi return Kong"""
 base_state["current_scene_index"] = 99

 result = commit_scene_node(base_state)

 assert result == {}


class TestShouldContinueOrAssemble:
 """test Lu You Han Shu"""

 def test_continue_when_pending_scenes(self):
 """Hai You Dai Chu Li scene Shi continue"""
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
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 status=SceneStatus.PENDING,
),
 ],
 "current_scene_index": 1,
 }

 result = should_continue_or_assemble(state)

 assert result == "continue"

 def test_assemble_when_all_committed(self):
 """Suo You scene Yi Ti Jiao Shi Jin Ru Zu Zhuang"""
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
 SceneBudget(
 scene_number=2,
 scene_index=1,
 target_duration_seconds=60,
 target_word_count=135,
 min_duration_seconds=51,
 max_duration_seconds=69,
 status=SceneStatus.COMMITTED,
),
 ],
 "current_scene_index": 2,
 }

 result = should_continue_or_assemble(state)

 assert result == "assemble"

 def test_assemble_when_index_exceeds(self):
 """Suo Yin Chao Chu Shi Jin Ru Zu Zhuang"""
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
 "current_scene_index": 5,
 }

 result = should_continue_or_assemble(state)

 assert result == "assemble"
