import pytest

from app.services.script.beat_contract_auto_repair import (
    auto_repair_script_beat_contract,
)
from app.services.script.beat_contract_normalizer import normalize_script_beat_contract
from app.services.script.beat_contract_quality import evaluate_beat_contract_quality
from tests.unit.services.script.test_beat_contract_auto_repair import _valid_contract


@pytest.mark.unit
def test_auto_repair_dedupes_screen_dialogue_and_hardens_payoff():
    payload = _valid_contract()
    scene = payload["scenes"][0]
    scene["beats"][1]["visible_event"] = scene["beats"][0]["visible_event"]
    scene["beats"][1]["action_lines"] = list(scene["beats"][0]["action_lines"])
    scene["beats"][1]["dialogue_lines"][0]["content"] = "Zheng Ju in this。"
    scene["beats"][1]["beat_type"] = "payoff"
    scene["beats"][1]["payoff_tag"] = "client Xin Ren"
    scene["beats"][1]["visible_event"] = "Cuan Gai Zhe Beng Kui Cheng Ren，client Xin RenAPreturn"
    scene["beats"][1]["action_lines"] = [{"content": "Cuan Gai Zhe Beng Kui，client Lian Se Huan He"}]
    scene["beats"][2]["dialogue_lines"][0]["content"] = "Zheng Ju in this。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "beat_progression_repetition" not in failed
    assert "dialogue_progression_repetition" not in failed
    assert "beat_visible_event_specificity" not in failed
    assert "payoff_specificity" not in failed


@pytest.mark.unit
def test_auto_repair_shortens_dialogue_lines_for_short_drama_gate():
    payload = _valid_contract()
    long_lines = [
        "Chen Zong，Yuan Shi file in Wo Shou Shang，data Cha Yi Wo Hui Cha Qing。",
        "Wo Ji De Yuan Shi Shu Ju is875Wan，Dui Ma？",
        "Yun Duan data is875Wan，Tou Ying on is920Wan。",
        "Zuo Bian is Yun Duan Yuan Shi Shu Ju，You Bian is Tou Ying data。",
        "Ni Qian Guo Zi confirm data Wu Wu，Xian Zai Zen Me Shuo？",
    ]
    first_scene = payload["scenes"][0]
    for idx, text in enumerate(long_lines):
        beat = first_scene["beats"][idx % len(first_scene["beats"])]
        beat.setdefault("dialogue_lines", [])
        beat["dialogue_lines"][0]["content"] = text

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    repaired_text = repaired["content"]
    assert "dialogue_line_length" not in failed
    assert "Chen Zong，Yuan Shi file in Wo Shou Shang，data Cha Yi Wo Hui Cha Qing。" not in repaired_text
    for scene in contract.scenes:
        for beat in scene.beats:
            for line in beat.dialogue_lines:
                assert len("".join(ch for ch in line.content if not ch.isspace())) <= 15


@pytest.mark.unit
def test_auto_repair_shortens_dialogue_to_complete_short_sentences():
    payload = _valid_contract()
    first_scene = payload["scenes"][0]
    lines = [
        "Chen Zong，Ke Neng is Ban Ben Tong Bu issue。Wo Rang Zhu Li Diao Qu Yuan Shi Bei Fen。",
        "this is Ni Qian Hui Yi Ji Yao，Tong Yi data Wu Wu。",
        "AP，Bao Qian Gang Cai Wu Hui。Ni Men Nei Bu Yao continue Cha。",
    ]
    for idx, text in enumerate(lines):
        beat = first_scene["beats"][idx % len(first_scene["beats"])]
        beat["dialogue_lines"][0]["content"] = text

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    repaired_text = repaired["content"]

    assert "Wo Rang Zhu Li Diao Qu" not in repaired_text
    assert "Tong Yi data none" not in repaired_text
    assert "Ni Men Nei Bu" not in repaired_text
    assert "Ke Neng is Tong Bu issue。" in repaired_text
    assert "Ji Yao have Ni sign。" in repaired_text
    assert "Gang Cai Wu Hui。" in repaired_text


@pytest.mark.unit
def test_auto_repair_replaces_vague_stakes_and_purpose():
    payload = _valid_contract()
    scene = payload["scenes"][0]
    scene["conflict"]["stakes"] = "Ruo not Cheng Qing，He Tong Zuo Fei，team Xin Ren Beng Kui。"
    scene["conflict"]["turn"] = "APTou Ping Yuan Shi Shu Ju and recording，Chen Mo Dang Chang Beng Kui。"
    scene["beats"][0]["dramatic_purpose"] = "Yin Ru conflict，Ji Fa Jin Zhang Gan。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_specificity" not in failed
    assert "scene_conflict_turn" not in failed
    assert "beat_dramatic_purpose_specificity" not in failed
    assert "300Wan project He Tong" in contract.scenes[0].conflict.stakes


@pytest.mark.unit
def test_auto_repair_replaces_prompt_style_opening_purpose():
    payload = _valid_contract()
    scene = payload["scenes"][0]
    scene["beats"][0]["dramatic_purpose"] = "3seconds INT Zhi Zao conflict：client Pai Zhuo Zhi Wen，data exception。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "beat_dramatic_purpose_specificity" not in failed
    assert "Zhi Zao conflict" not in contract.scenes[0].beats[0].dramatic_purpose


@pytest.mark.unit
def test_auto_repair_replaces_generic_scene_turn_key_line():
    payload = _valid_contract()
    payload["scenes"][0]["conflict"]["turn"] = "discover key Xian Suo"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    failed = {item["check_id"] for item in report["failed_checks"]}
    assert "scene_conflict_turn" not in failed
    assert contract.scenes[0].conflict.turn != "discover key Xian Suo"
    assert "Yuan Shi file" in contract.scenes[0].conflict.turn


@pytest.mark.unit
def test_auto_repair_replaces_vague_visual_language_in_actions():
    payload = _valid_contract()
    scene = payload["scenes"][0]
    scene["beats"][0]["visible_event"] = "conference room Qi Fen tense，Suo You Ren Zhu ShiAP。"
    scene["beats"][1]["action_lines"][0][
        "content"
    ] = "Dian Hua on display countdown，tense Qi Fen Zai Du escalate。"

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": payload},
        target_chars_per_episode=500,
    )
    repaired_text = repaired["content"]

    assert "Qi Fen" not in repaired_text
    assert "Yun Duan Ri Zhi time Chuo" in repaired_text


@pytest.mark.unit
def test_auto_repair_coerces_malformed_embedded_contract_without_top_level_scenes():
    malformed_contract = {
        "contract_version": "script-beat-v1",
        "scenes": [
            {
                "scene_number": 1,
                "estimated_duration_seconds": 15,
                "beats": [
                    {"order_index": 1, "beat_type": "hook", "duration_seconds": 3},
                    {"order_index": 2, "beat_type": "conflict", "duration_seconds": 6},
                    {"order_index": 3, "beat_type": "reveal", "duration_seconds": 6},
                ],
            }
        ],
    }

    repaired = auto_repair_script_beat_contract(
        {"structured_script_contract": malformed_contract},
        target_chars_per_episode=500,
    )
    contract = normalize_script_beat_contract(repaired)
    report = evaluate_beat_contract_quality(contract)

    assert contract.scenes[0].slug_line == "INT. conference room - day"
    assert contract.scenes[0].beats[0].visible_event
    assert report["passed"] is True, report
