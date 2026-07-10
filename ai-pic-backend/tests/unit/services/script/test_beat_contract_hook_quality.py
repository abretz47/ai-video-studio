import pytest
from app.services.script.beat_contract_normalizer import normalize_script_beat_contract
from app.services.script.beat_contract_quality import evaluate_beat_contract_quality
from tests.unit.services.script.test_beat_contract_normalizer import _valid_contract


@pytest.mark.unit
def test_quality_gate_rejects_slow_opening_hook():
 payload = _valid_contract()
 for beat, duration in zip(payload["scenes"][0]["beats"], [5, 5, 5], strict=True):
 beat["duration_seconds"] = duration
 contract = normalize_script_beat_contract(payload)

 report = evaluate_beat_contract_quality(contract)

 failed = {item["check_id"] for item in report["failed_checks"]}
 assert report["passed"] is False
 assert "opening_hook_duration" in failed


@pytest.mark.unit
def test_quality_gate_rejects_opening_hook_without_immediate_threat():
 payload = _valid_contract()
 first_beat = payload["scenes"][0]["beats"][0]
 first_beat["visible_event"] = "Xiao Ji Tui Kai Bo Li Men, Deng Dai Yi Ci Liang Qi."
 first_beat["action_lines"] = [{"content": "Xiao Ji Ba Bei Bao Fang Dao Zhuo Mian, Zheng Li Xiu Kou."}]
 first_beat["dialogue_lines"] = [{"character": "Xiao Ji", "content": "I'm here."}]
 contract = normalize_script_beat_contract(payload)

 report = evaluate_beat_contract_quality(contract)

 failed = {item["check_id"] for item in report["failed_checks"]}
 assert report["passed"] is False
 assert "opening_hook_substance" in failed
