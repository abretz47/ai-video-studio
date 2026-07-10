import pytest

from app.services.script.beat_contract_auto_repair import (
    auto_repair_script_beat_contract,
)
from app.services.script.beat_contract_normalizer import normalize_script_beat_contract
from app.services.script.beat_contract_quality import evaluate_beat_contract_quality
from tests.unit.services.script.test_beat_contract_normalizer import _valid_contract


@pytest.mark.unit
def test_auto_repair_preserves_three_second_opening_hook_with_many_beats():
    payload = _valid_contract()
    first_scene = payload["scenes"][0]
    first_scene["beats"][0]["visible_event"] = "Tou Ying Mu Bu Liang Qi，display Bing Gou Jin Diao data。"
    first_scene["beats"][0]["action_lines"] = [
        {"content": "Quan Chang Mu Guang Ju JiaoAP。"},
    ]
    first_scene["beats"].insert(
        1,
        {
            "order_index": 2,
            "beat_type": "reversal",
            "dramatic_purpose": "APdiscover Yuan Shi file and Tou Ying Shu Zi conflict。",
            "visible_event": "APFan Kai Yuan Shi file，Shou Zhi Ting in be Gai Dong Shu Zi on。",
            "action_lines": [{"content": "APfile Tui to client Mian Qian。"}],
            "dialogue_lines": [{"character": "Xiao Ji", "content": "Zhe Li be Gai。"}],
            "duration_seconds": 4,
        },
    )

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    first_beat = contract.scenes[0].beats[0]
    failed = {item["check_id"] for item in report["failed_checks"]}
    assert first_beat.duration_seconds <= 3
    assert "opening_hook_duration" not in failed
    assert "opening_hook_substance" not in failed


@pytest.mark.unit
def test_auto_repair_falls_back_to_top_level_contract_when_embedded_contract_invalid():
    payload = _valid_contract()
    bad_embedded_contract = {
        "contract_version": "script-beat-v1",
        "title": payload["title"],
        "scenes": [
            {
                "scene_number": 1,
                "beats": payload["scenes"][0]["beats"],
            }
        ],
    }

    repaired = auto_repair_script_beat_contract(
        {
            **payload,
            "metadata": {"structured_script_contract": bad_embedded_contract},
            "structured_script_contract": bad_embedded_contract,
        },
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)

    assert contract.scenes[0].slug_line == "INT. control room - night"
    assert repaired["structured_script_contract"]["scenes"][0]["slug_line"] == (
        "INT. control room - night"
    )


@pytest.mark.unit
def test_auto_repair_replaces_abstract_opposition_with_concrete_source():
    payload = _valid_contract()
    payload["scenes"][0]["conflict"]["opposition"] = "Ni Ming Duan Xin Tou Lu Mu Hou mastermind"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_opposition" not in failed
    assert "file" in contract.scenes[0].conflict.opposition


@pytest.mark.unit
def test_auto_repair_replaces_thin_opposition_value():
    payload = _valid_contract()
    payload["scenes"][0]["conflict"]["opposition"] = "Cuan Gai Zhe"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_specificity" not in failed
    assert contract.scenes[0].conflict.opposition != "Cuan Gai Zhe"
    assert "30seconds countdown" in contract.scenes[0].conflict.opposition


@pytest.mark.unit
def test_auto_repair_injects_workplace_data_commercial_anchors():
    payload = _valid_contract()
    payload["title"] = "data Mi Ju"
    payload["logline"] = "APin Bing Gou Jin Diao Hui Shang discover client He Tong data be Cuan Gai。"
    payload["scenes"] = [
        {
            "scene_number": 1,
            "slug_line": "INT. conference room - day",
            "location": "conference room",
            "time_of_day": "day",
            "estimated_duration_seconds": 45,
            "dramatic_role": "hook",
            "conflict": {
                "question": "APRu He Wen Zhu client Zhi Yi？",
                "stakes": "client He Tong Ke Neng Qu Xiao。",
                "opposition": "Cuan Gai Zhe",
                "turn": "APdiscover data be Cuan Gai。",
            },
            "beats": [
                {
                    "order_index": 1,
                    "beat_type": "hook",
                    "dramatic_purpose": "Yin Ru conflict。",
                    "visible_event": "client Zhi Yi data。",
                    "action_lines": [{"content": "Zhang total Pai Zhuo。"}],
                    "dialogue_lines": [{"character": "AP", "content": "Wo Cha。"}],
                    "duration_seconds": 3,
                }
            ],
        },
        {
            "scene_number": 2,
            "slug_line": "INT. conference room - day",
            "location": "conference room",
            "time_of_day": "day",
            "estimated_duration_seconds": 75,
            "dramatic_role": "escalation",
            "conflict": {
                "question": "APRu He Jie Lu Cuan Gai Zhe？",
                "stakes": "client He Tong Ke Neng Qu Xiao。",
                "opposition": "Cuan Gai Zhe",
                "turn": "Chen Mo Shi Tu delete file。",
            },
            "beats": [],
        },
        {
            "scene_number": 3,
            "slug_line": "INT. conference room - day",
            "location": "conference room",
            "time_of_day": "day",
            "estimated_duration_seconds": 60,
            "dramatic_role": "cliffhanger",
            "conflict": {
                "question": "Mu Hou Zhu Shi is who？",
                "stakes": "Zheng Ju Ke Neng be delete。",
                "opposition": "Ni Ming Wei Xie",
                "turn": "Xin Wei Xie Chu Xian。",
            },
            "beats": [],
        },
    ]

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=1300,
    )
    text = repaired["content"]
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    assert report["passed"] is True
    assert "60seconds，He Tong Zuo Fei" in text
    assert "Ri Zhi Yi Suo" in text
    assert "Gai Wan Gei Ni20Wan" in text
    assert "this Zhi Shi Di Yi Ceng" in text
    assert "Zhang total phone countdown from60seconds Tiao to59seconds" in text
    assert text.index("Chen Mo Tu Ran QiangAPphone") < text.index("phone Gei Wo")


@pytest.mark.unit
def test_auto_repair_replaces_vague_cliffhanger_opposition():
    payload = _valid_contract()
    final_scene = payload["scenes"][-1]
    final_scene["conflict"]["stakes"] = "APKe Neng be Mu Hou Zhu Shi Bao Fu，project Reng exists Feng Xian。"
    final_scene["conflict"][
        "opposition"
    ] = "Cuan Gai Zhe Leo Beng Kui，Dan phone Shou Dao mysterious Duan Xin，APYe Shou Dao Ni Ming Wei Xie。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_specificity" not in failed
    assert "Beng Kui" not in contract.scenes[-1].conflict.opposition
    assert "30seconds countdown" in contract.scenes[-1].conflict.opposition


@pytest.mark.unit
def test_auto_repair_makes_turn_purpose_and_protagonist_screen_action_specific():
    payload = _valid_contract()
    scene = payload["scenes"][0]
    scene["conflict"]["turn"] = "APdiscover data be Cuan Gai，and Yi Shi to Nei Bu someone Dong Shou Jiao。"
    for beat in scene["beats"]:
        for line in beat["dialogue_lines"]:
            line["character"] = "APreturn character-20260618T164912"
        beat["visible_event"] = beat["visible_event"].replace("Xiao Ji", "AP")
        for action in beat["action_lines"]:
            action["content"] = action["content"].replace("Xiao Ji", "AP")
    scene["beats"][-1]["dramatic_purpose"] = "Xin Wei Xie Fu Xian，Liu Xia Xuan Nian。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_turn" not in failed
    assert "scene_protagonist_screen_presence" not in failed
    assert "beat_dramatic_purpose_specificity" not in failed
    assert "APreturn character-20260618T164912" in (
        contract.scenes[0].beats[0].action_lines[0].content
    )
