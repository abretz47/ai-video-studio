import pytest
from app.schemas.generation import ScriptModel
from app.schemas.script_beat_contract import StructuredScriptContract
from app.services.script.beat_contract_normalizer import (
    flatten_contract_to_script_payload,
    normalize_script_beat_contract,
)
from app.services.script.content_normalization import normalize_script_content
from pydantic import ValidationError


def _valid_contract():
    return {
        "contract_version": "script-beat-v1",
        "title": "countdown Mi Ying",
        "logline": "robot discover bonus reset to zero，Bi Xu Zhao Chu who Gai Shi Jian Zhou。",
        "scenes": [
            {
                "scene_number": 1,
                "slug_line": "INT. control room - night",
                "location": "control room",
                "time_of_day": "night",
                "estimated_duration_seconds": 15,
                "dramatic_role": "hook",
                "conflict": {
                    "question": "who Qing Kong bonus？",
                    "stakes": "60seconds INT Zhao Bu Dao Jiu Yong Jiu Diu Shi bonus。",
                    "opposition": "be Cuan Gai Shi Jian Zhou system。",
                    "turn": "countdown Tu Ran Qi Dong。",
                },
                "beats": [
                    {
                        "order_index": 1,
                        "beat_type": "hook",
                        "dramatic_purpose": "Zhi Jie Pao Chu Sun Shi and time Ya Li。",
                        "visible_event": "Ping Mu Xian Shi bonus Gui Ling，Jing Bao Liang Qi。",
                        "action_lines": [
                            {"content": "Xiao Ji Chong Dao Kong Zhi Tai，red countdown start Tiao Dong。"}
                        ],
                        "dialogue_lines": [
                            {
                                "character": "Xiao Ji",
                                "content": "bonus reset to zero？",
                                "emotion": "Jing Huang",
                            }
                        ],
                        "duration_seconds": 3,
                        "hook_tag": "countdown_loss",
                    },
                    {
                        "order_index": 2,
                        "beat_type": "reveal",
                        "dramatic_purpose": "Zheng Ming Xiao Ji Zhao Dao Di Yi Duan Zheng Ju。",
                        "visible_event": "Xiu Gai Ri Zhi Jie Suo，bonus record Hui Fu Yi Ban。",
                        "action_lines": [
                            {"content": "Xiao Ji Tuo Chu Yin Cang Ri Zhi，screen Dan Chu Cao Zuo Zhe Bian Hao。"}
                        ],
                        "dialogue_lines": [
                            {"character": "Xiao Ji", "content": "Zheng Ju Chu Lai。"}
                        ],
                        "duration_seconds": 6,
                        "payoff_tag": "partial_proof",
                    },
                    {
                        "order_index": 3,
                        "beat_type": "cliffhanger",
                        "dramatic_purpose": "Liu Xia Wei Jie Wei Xie。",
                        "visible_event": "Hei Ying from Ri Zhi Li delete final Yi Tiao record。",
                        "action_lines": [{"content": "Ri Zhi Mo Xing be Hei Se Guang Biao Tun Diao。"}],
                        "dialogue_lines": [
                            {"character": "Xiao Ji", "content": "who Hai Zai Xian？"}
                        ],
                        "duration_seconds": 6,
                        "cliffhanger_tag": "hidden_operator",
                    },
                ],
            }
        ],
    }


@pytest.mark.unit
def test_structured_script_contract_accepts_valid_payload():
    contract = StructuredScriptContract.model_validate(_valid_contract())

    assert contract.contract_version == "script-beat-v1"
    assert contract.scenes[0].beats[0].beat_type == "hook"
    assert contract.scenes[0].beats[-1].cliffhanger_tag == "hidden_operator"


@pytest.mark.unit
def test_structured_script_contract_rejects_unknown_role():
    payload = _valid_contract()
    payload["scenes"][0]["dramatic_role"] = "vibes"

    with pytest.raises(ValidationError):
        StructuredScriptContract.model_validate(payload)


@pytest.mark.unit
def test_flatten_contract_to_legacy_script_payload():
    contract = normalize_script_beat_contract(_valid_contract())

    flattened = flatten_contract_to_script_payload(
        contract,
        format_type="screenplay",
        language="zh-CN",
        episode_number=1,
        template_style="commercial_vertical_drama",
        target_chars_per_episode=500,
        title="countdown Mi Ying",
    )

    assert flattened["scenes"][0]["beats"][0]["beat_type"] == "hook"
    assert flattened["dialogues"][0]["scene_number"] == 1
    assert flattened["dialogues"][0]["character"] == "Xiao Ji"
    assert flattened["stage_directions"][0]["scene_number"] == 1
    assert flattened["stage_directions"][0]["type"] == "visible_event"
    assert "Ping Mu Xian Shi bonus Gui Ling" in flattened["content"]
    assert flattened["content"].index("Ping Mu Xian Shi bonus Gui Ling") < flattened[
        "content"
    ].index("bonus reset to zero？")
    assert "Xiao Ji" in flattened["content"]
    assert flattened["metadata"]["structured_contract_version"] == "script-beat-v1"


@pytest.mark.unit
def test_legacy_script_conversion_marks_fallback_evidence():
    legacy = {
        "title": "Jiu structure",
        "scenes": [
            {
                "scene_number": 1,
                "slug_line": "INT. control room - night",
                "summary": "Xiao Ji discover bonus reset to zero。",
            }
        ],
        "dialogues": [
            {
                "scene_number": 1,
                "character": "voiceover",
                "content": "Xiao Ji discover bonus reset to zero。",
                "fallback": True,
            }
        ],
        "stage_directions": [
            {
                "scene_number": 1,
                "content": "Xiao Ji discover bonus reset to zero。",
                "type": "action",
                "fallback": True,
            }
        ],
    }

    contract = normalize_script_beat_contract(legacy)

    assert contract.scenes[0].beats[0].beat_type == "setup"
    assert contract.scenes[0].beats[0].visible_event == "Xiao Ji discover bonus reset to zero。"
    assert contract.model_extra["fallback_detected"] is True


@pytest.mark.unit
def test_content_normalization_preserves_scene_beats():
    payload = _valid_contract()
    normalized = normalize_script_content(
        payload,
        format_type="screenplay",
        language="zh-CN",
        episode_number=1,
        template_style="commercial_vertical_drama",
        target_chars_per_episode=500,
        title="countdown Mi Ying",
    )

    assert normalized["scenes"][0]["beats"][0]["beat_type"] == "hook"
    assert normalized["scenes"][0]["summary"] == "who Qing Kong bonus？"


@pytest.mark.unit
def test_content_normalization_coerces_numeric_estimated_duration_metadata():
    payload = {
        "content": "Di1Chang\nXiao Ji：Zheng Ju Chu Lai。\n▲Ri Zhi Mo Xing be Hei Se Guang Biao Tun Diao。",
        "scenes": [
            {
                "scene_number": 1,
                "description": "Xiao Ji discover bonus reset to zero。",
            }
        ],
        "dialogues": [
            {
                "scene_number": 1,
                "character": "Xiao Ji",
                "content": "Zheng Ju Chu Lai。",
            }
        ],
        "stage_directions": [
            {
                "scene_number": 1,
                "content": "Ri Zhi Mo Xing be Hei Se Guang Biao Tun Diao。",
            }
        ],
        "metadata": {"estimated_duration": 60},
    }

    normalized = normalize_script_content(
        payload,
        format_type="screenplay",
        language="zh-CN",
        episode_number=1,
        template_style="commercial_vertical_drama",
        target_chars_per_episode=500,
        title="countdown Mi Ying",
    )

    assert normalized["metadata"]["estimated_duration"] == "60"
    ScriptModel.model_validate(normalized)
