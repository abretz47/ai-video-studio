import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "ai-pic-backend"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(BACKEND_ROOT))

from tests.scripts.provider_chain_fixtures import provider_payload  # noqa: E402

from scripts.harness.production_quality_script import (  # noqa: E402
    provider_chain_script_text,
    structured_script_score,
)


def test_structured_score_rejects_resolved_provider_final_cliffhanger() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    final_scene = script["scenes"][-1]
    final_beat = final_scene["beats"][-1]
    final_scene["turn"] = "Xiaolan Na Hui Quan Bu bonus after，Kong Zhi Tai display Ren Wu complete。"
    final_beat["beat_type"] = "cliffhanger"
    final_beat["visible_event"] = "Xiaolan Na Hui Quan Bu bonus，system display Ren Wu complete"
    final_beat["action"] = ["Xiaolan Ju Qi to Zhang screen，Jing Bao Deng Quan Bu Xi Mie"]
    final_beat["dialogue"][0]["line"] = "bonus Quan Na Hui"
    final_beat["cliffhanger_tag"] = "case_closed"
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert result["passed"] is False
    assert "cliffhanger_unresolved_threat" in result["failed_checks"]


def test_provider_chain_screenplay_uses_final_cliffhanger_beat() -> None:
    payload = provider_payload()

    screenplay = provider_chain_script_text(payload)

    assert "【Xuan Nian】Hei Ying delete final Ri Zhi" in screenplay
    assert "【Xuan Nian】Xiaolan discover truth，final Yi Miao Fan Zhuan。" not in screenplay


def test_structured_score_rejects_terminal_failure_as_cliffhanger() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    final_beat = script["scenes"][-1]["beats"][-1]
    final_beat["beat_type"] = "cliffhanger"
    final_beat["visible_event"] = "Jin Du Tiao to100%，screen Bian Hong"
    final_beat["action"] = ["Xiao Lan Shou Ting in Jian Pan on，LEDYan Jing Bian An"]
    final_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "Lai Bu Ji"}]
    final_beat["cliffhanger_tag"] = "data Diu Shi"
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert result["passed"] is False
    assert "cliffhanger_unresolved_threat" in result["failed_checks"]


def test_structured_score_rejects_executed_delete_command_as_cliffhanger() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    final_beat = script["scenes"][-1]["beats"][-1]
    final_beat["beat_type"] = "cliffhanger"
    final_beat["visible_event"] = "screen Dan Chu red Jing Gao：Yuan Cheng delete Ming Ling already Zhi Xing"
    final_beat["action"] = ["Xiaolan Hou Tui Yi Bu，Kong Zhi Tai file list Quan Bu Bian Hui"]
    final_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "delete Ming Ling already Zhi Xing"}]
    final_beat["cliffhanger_tag"] = "Yuan Cheng delete"
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert result["passed"] is False
    assert "cliffhanger_unresolved_threat" in result["failed_checks"]
