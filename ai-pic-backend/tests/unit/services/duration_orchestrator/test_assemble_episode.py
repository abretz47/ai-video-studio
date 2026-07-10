"""
assemble_episode Jie Dian Dan Yuan Ce Shi

test episode Zu Zhuang function.
"""

import pytest
from app.services.duration_orchestrator.constants import (
 DIALOGUE_DENSITY_FACTOR,
 WORDS_PER_SECOND,
)
from app.services.duration_orchestrator.nodes.assemble_episode import (
 assemble_episode_node,
)
from app.services.duration_orchestrator.state import SceneBudget, SceneStatus


def create_budget(
 scene_number: int,
 target_duration: int = 60,
 scene_index: int = 0,
) -> SceneBudget:
 """Fu Zhu Han Shu: create SceneBudget"""
 return SceneBudget(
 scene_number=scene_number,
 scene_index=scene_index,
 target_duration_seconds=target_duration,
 target_word_count=int(
 target_duration * DIALOGUE_DENSITY_FACTOR * WORDS_PER_SECOND
),
 min_duration_seconds=int(target_duration * 0.85),
 max_duration_seconds=int(target_duration * 1.15),
)


class TestAssembleEpisodeNode:
 """test assemble_episode_node"""

 @pytest.fixture
 def base_state(self):
 """Ji Chu Zhuang Tai"""
 return {
 "episode_id": 1,
 "script_id": 1,
 "total_duration_minutes": 3,
 "scene_budgets": [],
 "committed_scenes": {},
 "generated_dialogues": {},
 "reasoning": [],
 "errors": [],
 }

 def test_assemble_with_committed_scenes(self, base_state):
 """test Zu Zhuang Yi Ti Jiao De scene"""
 # create Liang Ge Yi Ti Jiao De scene Yu Suan
 budget1 = create_budget(scene_number=1, target_duration=60, scene_index=0)
 budget1.status = SceneStatus.COMMITTED
 budget1.actual_duration_seconds = 58.5
 budget1.attempt_count = 1

 budget2 = create_budget(scene_number=2, target_duration=60, scene_index=1)
 budget2.status = SceneStatus.COMMITTED
 budget2.actual_duration_seconds = 62.3
 budget2.attempt_count = 2

 base_state["scene_budgets"] = [budget1, budget2]
 base_state["committed_scenes"] = {
 1: {
 "scene_number": 1,
 "dialogues": [{"character": "A", "content": "scene1dialogue"}],
 "actual_duration_seconds": 58.5,
 },
 2: {
 "scene_number": 2,
 "dialogues": [{"character": "B", "content": "scene2dialogue"}],
 "actual_duration_seconds": 62.3,
 },
 }

 result = assemble_episode_node(base_state)

 # validate Zu Zhuang Jie Guo
 assert "assembled_episode" in result
 assembled = result["assembled_episode"]
 assert assembled["episode_id"] == 1
 assert assembled["script_id"] == 1
 assert len(assembled["dialogues"]) == 2
 assert len(assembled["scene_results"]) == 2

 def test_assemble_statistics_calculation(self, base_state):
 """test statistics information Ji Suan"""
 budget1 = create_budget(scene_number=1, target_duration=60, scene_index=0)
 budget1.status = SceneStatus.COMMITTED
 budget1.actual_duration_seconds = 55.0
 budget1.attempt_count = 1

 budget2 = create_budget(scene_number=2, target_duration=60, scene_index=1)
 budget2.status = SceneStatus.COMMITTED
 budget2.actual_duration_seconds = 65.0
 budget2.attempt_count = 3

 base_state["scene_budgets"] = [budget1, budget2]
 base_state["committed_scenes"] = {1: {}, 2: {}}

 result = assemble_episode_node(base_state)

 # validate statistics information
 assert "statistics" in result
 stats = result["statistics"]
 assert stats["total_target_duration_seconds"] == 180 # 3 * 60
 assert stats["total_actual_duration_seconds"] == 120.0 # 55 + 65
 assert stats["scene_count"] == 2
 assert stats["committed_count"] == 2
 assert stats["total_retries"] == 2 # (1-1) + (3-1) = 0 + 2

 def test_assemble_duration_ratio(self, base_state):
 """test Shi length Bi Li Ji Suan"""
 budget = create_budget(scene_number=1, target_duration=90, scene_index=0)
 budget.status = SceneStatus.COMMITTED
 budget.actual_duration_seconds = 90.0 # Zheng Hao Zai target Shang
 budget.attempt_count = 1

 base_state["total_duration_minutes"] = 2 # 120Miao Mu Biao
 base_state["scene_budgets"] = [budget]
 base_state["committed_scenes"] = {1: {}}

 result = assemble_episode_node(base_state)

 stats = result["statistics"]
 # 90 / 120 = 0.75
 assert stats["duration_ratio"] == 0.75

 def test_assemble_dialogues_order(self, base_state):
 """test dialogue An scene Shun Xu Pai Lie"""
 base_state["committed_scenes"] = {
 3: {"dialogues": [{"content": "scene3"}]},
 1: {"dialogues": [{"content": "scene1"}]},
 2: {"dialogues": [{"content": "scene2"}]},
 }
 base_state["scene_budgets"] = []

 result = assemble_episode_node(base_state)

 dialogues = result["assembled_episode"]["dialogues"]
 # Ying Gai An scene Bian Hao Shun Xu Pai Lie
 assert len(dialogues) == 3
 assert dialogues[0]["content"] == "scene1"
 assert dialogues[1]["content"] == "scene2"
 assert dialogues[2]["content"] == "scene3"

 def test_assemble_adds_scene_number_to_dialogues(self, base_state):
 """test Wei dialogue Tian Jia scene Bian Hao"""
 base_state["committed_scenes"] = {
 1: {"dialogues": [{"character": "A", "content": "dialogue content"}]},
 }
 base_state["scene_budgets"] = []

 result = assemble_episode_node(base_state)

 dialogues = result["assembled_episode"]["dialogues"]
 assert dialogues[0]["scene_number"] == 1

 def test_assemble_empty_scenes(self, base_state):
 """test Kong scene list"""
 result = assemble_episode_node(base_state)

 assert result["assembled_episode"]["dialogues"] == []
 assert result["statistics"]["scene_count"] == 0
 assert result["statistics"]["committed_count"] == 0

 def test_assemble_updates_reasoning(self, base_state):
 """test update Tui Li Ri Zhi"""
 budget = create_budget(scene_number=1, target_duration=60, scene_index=0)
 budget.status = SceneStatus.COMMITTED
 budget.actual_duration_seconds = 60.0
 budget.attempt_count = 1

 base_state["scene_budgets"] = [budget]
 base_state["committed_scenes"] = {1: {}}

 result = assemble_episode_node(base_state)

 assert len(result["reasoning"]) > 0
 assert "Zu Zhuang Wan Cheng" in result["reasoning"][-1]

 def test_assemble_counts_failed_scenes(self, base_state):
 """test statistics failed scene"""
 budget1 = create_budget(scene_number=1, target_duration=60, scene_index=0)
 budget1.status = SceneStatus.COMMITTED
 budget1.actual_duration_seconds = 60.0
 budget1.attempt_count = 1

 budget2 = create_budget(scene_number=2, target_duration=60, scene_index=1)
 budget2.status = SceneStatus.FAILED
 budget2.attempt_count = 3

 base_state["scene_budgets"] = [budget1, budget2]
 base_state["committed_scenes"] = {1: {}}

 result = assemble_episode_node(base_state)

 stats = result["statistics"]
 assert stats["committed_count"] == 1
 assert stats["failed_count"] == 1

 def test_assemble_sets_phase(self, base_state):
 """test set Jie Duan status"""
 result = assemble_episode_node(base_state)

 assert result["phase"] == "assembled"
