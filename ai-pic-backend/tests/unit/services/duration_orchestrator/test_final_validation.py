"""
final_validation Jie Dian Dan Yuan Ce Shi

test final Shi length validate function.
"""

import pytest
from app.services.duration_orchestrator.constants import (
 DURATION_TOLERANCE_EPISODE_HIGH,
 DURATION_TOLERANCE_EPISODE_LOW,
)
from app.services.duration_orchestrator.nodes.final_validation import (
 final_validation_node,
 should_pass_or_fail,
)


class TestFinalValidationNode:
 """test final_validation_node"""

 @pytest.fixture
 def base_state(self):
 """Ji Chu Zhuang Tai"""
 return {
 "episode_id": 1,
 "total_duration_minutes": 3, # 180seconds
 "statistics": {
 "total_actual_duration_seconds": 180.0,
 },
 "reasoning": [],
 "errors": [],
 }

 def test_validation_passes_exact_match(self, base_state):
 """test Jing Que Pi Pei Shi validate pass"""
 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is True
 assert result["success"] is True
 assert result["final_validation_result"]["duration_ratio"] == 1.0
 assert result["final_validation_result"]["deviation_percent"] == 0.0

 def test_validation_passes_within_tolerance(self, base_state):
 """test Zai Rong Cha Fan Wei INT validate pass"""
 # set actual duration Wei target De 95%(Zai ±10% Rong Cha Nei)
 base_state["statistics"]["total_actual_duration_seconds"] = 171.0 # 95%

 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is True
 assert result["success"] is True

 def test_validation_fails_too_short(self, base_state):
 """test duration Guo Duan Shi validate failed"""
 # set actual duration Wei target De 85%(Chao Chu ±10% Rong Cha)
 base_state["statistics"]["total_actual_duration_seconds"] = 153.0 # 85%

 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is False
 assert result["success"] is False
 assert len(result["errors"]) > 0
 assert "Guo Duan" in result["errors"][0]

 def test_validation_fails_too_long(self, base_state):
 """test Shi length Guo Chang Shi validate failed"""
 # set actual duration Wei target De 115%(Chao Chu ±10% Rong Cha)
 base_state["statistics"]["total_actual_duration_seconds"] = 207.0 # 115%

 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is False
 assert result["success"] is False
 assert len(result["errors"]) > 0
 assert "Guo Chang" in result["errors"][0]

 def test_validation_boundary_lower(self, base_state):
 """test Xia Bian Jie(Gang Hao Zai Rong Cha INT)"""
 # 90% = 162seconds
 base_state["statistics"]["total_actual_duration_seconds"] = 162.0

 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is True

 def test_validation_boundary_upper(self, base_state):
 """test Shang Bian Jie(Gang Hao Zai Rong Cha INT)"""
 # 110% = 198seconds
 base_state["statistics"]["total_actual_duration_seconds"] = 198.0

 result = final_validation_node(base_state)

 assert result["final_validation_result"]["passed"] is True

 def test_validation_result_structure(self, base_state):
 """testValidation resultstructure"""
 result = final_validation_node(base_state)

 validation = result["final_validation_result"]
 assert "passed" in validation
 assert "total_actual_duration_seconds" in validation
 assert "total_target_duration_seconds" in validation
 assert "duration_ratio" in validation
 assert "deviation_seconds" in validation
 assert "deviation_percent" in validation
 assert "tolerance_percent" in validation
 assert "tolerance_range" in validation

 def test_validation_tolerance_range(self, base_state):
 """test Rong Cha Fan Wei Ji Suan"""
 result = final_validation_node(base_state)

 tolerance_range = result["final_validation_result"]["tolerance_range"]
 target = 180 # 3minutes

 # validate Rong Cha Fan Wei (use pytest.approx handle Fu Dian Jing Du)
 expected_min = target * DURATION_TOLERANCE_EPISODE_LOW
 expected_max = target * DURATION_TOLERANCE_EPISODE_HIGH

 assert tolerance_range["min_seconds"] == pytest.approx(expected_min)
 assert tolerance_range["max_seconds"] == pytest.approx(expected_max)

 def test_validation_updates_reasoning_pass(self, base_state):
 """Ce Shi Tong Guo Shi update Tui Li Ri Zhi"""
 result = final_validation_node(base_state)

 assert len(result["reasoning"]) > 0
 assert "pass" in result["reasoning"][-1]

 def test_validation_updates_reasoning_fail(self, base_state):
 """test failed Shi update Tui Li Ri Zhi"""
 base_state["statistics"]["total_actual_duration_seconds"] = 150.0

 result = final_validation_node(base_state)

 assert len(result["reasoning"]) > 0
 assert "failed" in result["reasoning"][-1]

 def test_validation_sets_phase(self, base_state):
 """test set Jie Duan status"""
 result = final_validation_node(base_state)

 assert result["phase"] == "validated"

 def test_validation_zero_target(self):
 """test Ling target Shi length"""
 state = {
 "episode_id": 1,
 "total_duration_minutes": 0,
 "statistics": {"total_actual_duration_seconds": 0},
 "reasoning": [],
 "errors": [],
 }

 result = final_validation_node(state)

 # Ying Gai handle Ling Chu error
 assert "final_validation_result" in result
 assert result["final_validation_result"]["duration_ratio"] == 0


class TestShouldPassOrFail:
 """test should_pass_or_fail Lu You Han Shu"""

 def test_returns_pass_when_passed(self):
 """Ce Shi Tong Guo Shi return pass"""
 state = {"final_validation_result": {"passed": True}}
 assert should_pass_or_fail(state) == "pass"

 def test_returns_fail_when_failed(self):
 """test failed Shi return fail"""
 state = {"final_validation_result": {"passed": False}}
 assert should_pass_or_fail(state) == "fail"

 def test_returns_fail_when_no_result(self):
 """test none Jie Guo Shi return fail"""
 state = {}
 assert should_pass_or_fail(state) == "fail"

 def test_returns_fail_when_empty_result(self):
 """test Kong Jie Guo Shi return fail"""
 state = {"final_validation_result": {}}
 assert should_pass_or_fail(state) == "fail"
