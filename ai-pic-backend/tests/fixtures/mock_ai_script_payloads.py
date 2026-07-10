"""Script payloads for the mock AI service fixture."""

from __future__ import annotations

from typing import Any


def mock_passing_script_payload(protagonist_name: str = "Hero") -> dict[str, Any]:
    from app.schemas.script_beat_contract import StructuredScriptContract
    from app.services.script.beat_contract_normalizer import (
        flatten_contract_to_script_payload,
    )

    contract = StructuredScriptContract.model_validate(
        {
            "contract_version": "script-beat-v1",
            "title": "Zheng Ju back view signature",
            "logline": "HeroBi Xu in press conference after Qiang Hui Zheng Ju，Que discover signature Zhi Xiang Geng Gao Ceng mastermind。",
            "scenes": [
                {
                    "scene_number": 1,
                    "slug_line": "INT. press conference Hou Tai - day",
                    "location": "press conference Hou Tai",
                    "time_of_day": "day",
                    "estimated_duration_seconds": 15,
                    "dramatic_role": "hook",
                    "conflict": {
                        "question": "HeroNeng Fou in Zheng Ju be Suo Jin Bao Xian Xiang before Qiang Hui phone？",
                        "stakes": "30seconds INT failed，public video Zheng Ju Jiang be Yong Jiu delete。",
                        "opposition": "Dui Shou and Suo Zhu Bao Xian Xiang Dang inHeroMian Qian。",
                        "turn": "Bao Xian Xiang screen Tu Ran display delete countdown。",
                    },
                    "beats": [
                        {
                            "order_index": 1,
                            "beat_type": "hook",
                            "dramatic_purpose": "San Miao INT Pao Chu Zheng Ju be Qiang Sun Shi。",
                            "visible_event": "Bao Xian Xiang Liang Qi delete countdown，HeroChong Jin Hou Tai。",
                            "action_lines": [
                                {"content": "HeroZhuang Kai Men，Shou Zhi Si Si Kou Zhu Bao Xian Xiang Bian Yuan。"}
                            ],
                            "dialogue_lines": [
                                {
                                    "character": "Hero",
                                    "content": "Zheng Ju Bie Shan。",
                                    "emotion": "Ya Zhu Nu Huo",
                                }
                            ],
                            "duration_seconds": 3,
                            "hook_tag": "evidence_countdown",
                        },
                        {
                            "order_index": 2,
                            "beat_type": "reveal",
                            "dramatic_purpose": "Yong Wai Bu action Gei Chu counterattack Chou Ma。",
                            "visible_event": "HeroJu Qi recording phone，Dui Shou Shou Ting in Mi Ma Jian Shang。",
                            "action_lines": [
                                {"content": "Herophone screen Tie to camera before，recording Bo Xing Tiao Dong。"}
                            ],
                            "dialogue_lines": [
                                {
                                    "character": "Hero",
                                    "content": "Ni Yi Ru Jing。",
                                    "emotion": "calm",
                                }
                            ],
                            "duration_seconds": 6,
                            "payoff_tag": "recording_proof",
                        },
                        {
                            "order_index": 3,
                            "beat_type": "cliffhanger",
                            "dramatic_purpose": "Liu Xia Geng Gao Ceng mastermind Wei Jie Wei Xie。",
                            "visible_event": "Zheng Ju back view Lu Chu Mo Sheng Xin signature，Dui Shou Tu Ran Bian Lian。",
                            "action_lines": [
                                {"content": "HeroFan Guo Zheng Ju，Zhi Jian Ting in Mo Sheng signature on。"}
                            ],
                            "dialogue_lines": [
                                {
                                    "character": "Hero",
                                    "content": "this is who？",
                                    "emotion": "Ya Di Sheng",
                                }
                            ],
                            "duration_seconds": 6,
                            "cliffhanger_tag": "unknown_signature",
                        },
                    ],
                }
            ],
        }
    )
    payload = flatten_contract_to_script_payload(
        contract,
        format_type="screenplay",
        language="zh-CN",
        episode_number=1,
        template_style="commercial_vertical_drama",
        target_chars_per_episode=1300,
        title="Zheng Ju back view signature",
    )
    if protagonist_name and protagonist_name != "Hero":
        return _replace_text(payload, "Hero", protagonist_name)
    return payload


def _replace_text(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_text(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace_text(item, old, new) for key, item in value.items()}
    return value
