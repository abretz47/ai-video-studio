import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "ai-pic-backend"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(BACKEND_ROOT))

from tests.scripts.provider_chain_fixtures import provider_payload  # noqa: E402

from scripts.harness.production_quality_script import (  # noqa: E402
    structured_script_score,
)


def test_structured_score_rejects_slow_provider_opening_hook() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    for beat, duration in zip(script["scenes"][0]["beats"], [5, 5, 5], strict=True):
        beat["duration_seconds"] = duration
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert result["passed"] is False
    assert "opening_hook_duration" in result["failed_checks"]


def test_structured_score_rejects_provider_opening_hook_without_immediate_threat() -> (
    None
):
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    first_beat = script["scenes"][0]["beats"][0]
    first_beat["visible_event"] = "Xiaolan Tui Kai Bo Li Men，Deng Dai Yi Ci Liang Qi"
    first_beat["action"] = ["Xiaolan Bei Bao Fang Dao Zhuo Mian，Zheng Li Wei Jin"]
    first_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "Wo to"}]
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert result["passed"] is False
    assert "opening_hook_substance" in result["failed_checks"]


def test_structured_score_accepts_opening_warning_as_immediate_threat() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    first_beat = script["scenes"][0]["beats"][0]
    first_beat["visible_event"] = "Xiaolan Ding screen，system Dan Chu none hook Jing Gao"
    first_beat["action"] = ["Xiaolan An Zhu red Ti Shi Kuang，Diao Chu Jian Ji Mian Ban"]
    first_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "Jing Gao Lai"}]
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert "opening_hook_substance" not in result["failed_checks"]


def test_structured_score_accepts_reference_reuse_as_visual_anomaly_hook() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    first_beat = script["scenes"][0]["beats"][0]
    first_beat["visible_event"] = "time Xian Suo You camera Suo Lve Tu Dou Fu Yong Tong Yi Zhang Can Kao image"
    first_beat["action"] = ["Xiaolan Kuai Su Hua Guo Shi Ge camera，frame Quan Bu Xiang Tong"]
    first_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "Zen Me Quan Tong Yi Zhang？"}]
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert "opening_hook_substance" not in result["failed_checks"]


def test_structured_score_accepts_missing_character_as_visual_anomaly_hook() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    first_beat = script["scenes"][0]["beats"][0]
    first_beat["visible_event"] = "Yu Lan screen Zhi You Kong Bai scene，Mei You character Chu Xian"
    first_beat["action"] = ["Xiaolan Tuo Dong Bo Fang Tiao，Di Er Duan Reng Ran Que Shao character"]
    first_beat["dialogue"] = [{"speaker": "Xiaolan", "line": "character Ne"}]
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert "opening_hook_substance" not in result["failed_checks"]


def test_structured_score_accepts_no_payment_as_opening_stakes_hook() -> None:
    payload = provider_payload()
    script = json.loads(payload["key_artifacts"]["script"]["raw_content"])
    first_beat = script["scenes"][0]["beats"][0]
    first_beat["visible_event"] = "client Dai Biao close Bo Fang Qi，screen Bian Hei"
    first_beat["action"] = ["client Dai Biao Zhuan Shen Yao Zou，Wei Kuan status Bian Cheng Dai Ju Fu"]
    first_beat["dialogue"] = [{"speaker": "client Dai Biao", "line": "Mei hook not Fu Kuan"}]
    payload["key_artifacts"]["script"]["raw_content"] = json.dumps(
        script, ensure_ascii=False
    )

    result = structured_script_score(payload)

    assert "opening_hook_substance" not in result["failed_checks"]
