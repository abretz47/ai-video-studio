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
 "title": "evidence back view De signature",
 "logline": "HeroBi Xu Zai press conference Hou Qiang Hui evidence, Que discover signature Zhi Xiang Geng Gao Ceng mastermind.",
 "scenes": [
 {
 "scene_number": 1,
 "slug_line": "INT. press conference Hou Tai - day",
 "location": "press conference Hou Tai",
 "time_of_day": "day",
 "estimated_duration_seconds": 15,
 "dramatic_role": "hook",
 "conflict": {
 "question": "HeroNeng Fou Zai evidence Bei Suo Jin Bao Xian Xiang Qian Qiang Hui phone?",
 "stakes": "30Miao Nei Shi Bai, public video evidence Jiang Bei Yong Jiu delete.",
 "opposition": "Dui Shou He Suo Zhu De Bao Xian Xiang Dang ZaiHeroMian Qian.",
 "turn": "Bao Xian Xiang screen suddenly display delete countdown.",
 },
 "beats": [
 {
 "order_index": 1,
 "beat_type": "hook",
 "dramatic_purpose": "San Miao INT Pao Chu evidence Bei Qiang De Sun Shi.",
 "visible_event": "Bao Xian Xiang Liang Qi delete countdown, HeroChong Jin Hou Tai.",
 "action_lines": [
 {"content": "HeroZhuang Kai Men, Shou Zhi Si Si Kou Zhu Bao Xian Xiang Bian Yuan."}
 ],
 "dialogue_lines": [
 {
 "character": "Hero",
 "content": "Zheng Ju Bie Shan.",
 "emotion": "Ya Zhu Nu Huo",
 }
 ],
 "duration_seconds": 3,
 "hook_tag": "evidence_countdown",
 },
 {
 "order_index": 2,
 "beat_type": "reveal",
 "dramatic_purpose": "Yong Wai Bu action Gei Chu counterattack Chou Ma.",
 "visible_event": "HeroJu Qi recording phone, Dui Shou Shou Ting Zai Mi Ma Jian Shang.",
 "action_lines": [
 {"content": "HeroBa phone screen Tie to camera Qian, recording Bo Xing Tiao Dong."}
 ],
 "dialogue_lines": [
 {
 "character": "Hero",
 "content": "Ni Yi Ru Jing.",
 "emotion": "calm",
 }
 ],
 "duration_seconds": 6,
 "payoff_tag": "recording_proof",
 },
 {
 "order_index": 3,
 "beat_type": "cliffhanger",
 "dramatic_purpose": "Liu Xia Geng Gao Ceng mastermind De Wei Jie Wei Xie.",
 "visible_event": "evidence back view Lu Chu Mo Sheng new signature, Dui Shou suddenly Bian Lian.",
 "action_lines": [
 {"content": "HeroFan Guo Zheng Ju, Zhi Jian Ting Zai Mo Sheng signature Shang."}
 ],
 "dialogue_lines": [
 {
 "character": "Hero",
 "content": "Zhe Shi Shui?",
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
 title="evidence back view De signature",
)
 if protagonist_name and protagonist_name!= "Hero":
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
