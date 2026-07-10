import pytest
from app.services.script.beat_contract_normalizer import normalize_script_beat_contract
from app.services.script.beat_contract_quality import evaluate_beat_contract_quality
from tests.unit.services.script.test_beat_contract_normalizer import _valid_contract


@pytest.mark.unit
def test_quality_gate_rejects_resolved_final_cliffhanger():
    payload = _valid_contract()
    final_beat = payload["scenes"][-1]["beats"][-1]
    final_beat["beat_type"] = "cliffhanger"
    final_beat["visible_event"] = "Xiao Ji Cheng Gong Na Hui Quan Bu bonus，Kong Zhi Tai display Ren Wu complete。"
    final_beat["action_lines"] = [{"content": "Xiao Ji Ju Qi bonus to Zhang page，Jing Bao Deng Quan Bu Xi Mie。"}]
    final_beat["dialogue_lines"] = [{"character": "Xiao Ji", "content": "bonus Quan Na Hui。"}]
    final_beat["cliffhanger_tag"] = "case_closed"
    contract = normalize_script_beat_contract(payload)

    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert report["passed"] is False
    assert "cliffhanger_unresolved_threat" in failed
