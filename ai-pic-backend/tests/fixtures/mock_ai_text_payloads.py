"""Shared text-generation payloads for the mock AI service fixture."""

from __future__ import annotations

from typing import Any

from tests.fixtures.mock_ai_script_payloads import mock_passing_script_payload


def mock_generate_text_payload(prompt: str, json_schema: Any) -> dict[str, Any]:
 schema_name = json_schema.get("name") if isinstance(json_schema, dict) else ""
 if schema_name == "script_cliffhanger_judgement":
 return {
 "passed": True,
 "score": 0.95,
 "reason": "mock script ends on an unresolved question",
 "evidence": "Which door does the key open?",
 "suggestion": "",
 }
 if "The generated script JSON failed strict quality gate validation" in prompt:
 return _script_repair_payload()
 if "Tou Liu Biao" in prompt or "Traffic Sheet" in prompt:
 return _traffic_sheet_payload()
 return _script_score_payload()


def mock_passing_story_outline_payload() -> dict[str, Any]:
 return {
 "premise": "suddenly, HeroZai press conference discover betrayal evidence public, Bi Xu Dang Chang counterattack.",
 "synopsis": (
 "suddenly, HeroZai press conference Xian Chang discover betrayal video Bei public, crisis He conflict Li Ke Bao Fa."
 "HeroDing Zhu Ya Li Fan Cha evidence, tense Dui Kang Bu Duan escalate, Zhong Duan Jie ShiGuideZhang Wo key Xian Suo."
 "final climax Dui Jue Zhong truth reveal, HeroJie Jue crisis Bing complete Jie Duan Xing Ni Xi."
),
 "main_conflict": "HeroBi Xu Zai public Xiu Ru He evidence Zheng Duo Zhong Zhao Chu truth.",
 "resolution": "HeroNa Dao Zheng Ju, Jie Jue Di Yi Lun crisis Bing Bi Chu Xia Yi Ceng mastermind.",
 "main_characters": [
 {"name": "Hero", "role": "protagonist"},
 {"name": "Guide", "role": "mentor"},
 ],
 "character_relationships": {"Hero": {"Guide": "mentor"}},
 "plot_structure": {
 "act1": "suddenly public evidence, HeroDang Chang Fan Ji.",
 "act2": "Wei Ji Sheng Ji, HeroWei Rao evidence Yu Dui Shou tense Dui Kang.",
 "act3": "climax reveal truth, Herocomplete Ni Xi Bing Jie Jue Jie Duan crisis.",
 },
 "hook_plan": {
 "opening_hook": "suddenly, press conference Da Ping Bo FangHeroBei Xian Hai De video.",
 "escalation_plan": "evidence Zheng Duo Bu Duan escalate.",
 "payoff_plan": "HeroYong recording counterattack Bing Na Hui Zhu Dong Quan.",
 },
 "cliffhanger_plan": ["evidence back view Chu Xian new signature"],
 "ad_snippets": [
 {
 "duration_seconds": 15,
 "hook": "press conference evidence public",
 "visual_summary": "Da Ping video HeHeroWo Jin phone De Shou",
 "call_to_action": "KanHeroRu He Fan Ji",
 }
 ],
 "structured_story_contract": {
 "target_audience": "urban Fu Chou user",
 "core_emotional_pain": "Zun Yan Bei public Nian Ya",
 "big_expectation": "HeroCha Qing Xian Hai truth Bing Duo Hui Zhu Dong Quan",
 "small_expectation_ladder": ["Qian San Ji Na Dao recording", "Di Shi Ji Bi Chu ledger"],
 "protagonist_goal": "Na Dao press conference Xian Hai evidence",
 "structural_conflict": "HeroBi Xu JieGuideDe Zi Yuan ChaGuideYin Man De Xian Suo",
 "information_gap": "audience Zhi Dao evidence Zai phone Li, Dui Shou Bu Zhi Dao Yi Bei recording",
 "first_three_episode_spine": "identity, Jiu An, He Xin conflict Qian San Ji Li Zhu",
 "stage_highs": ["press conference counterattack", "Zheng Ju Zheng Duo", "Dong Shi Hui Fan Pan"],
 "shootability": "Fa Bu Hui Ting, Zou Lang, office Di Cheng Ben Ke Pai",
 "compliance_risks": [],
 "traffic_hooks": ["Da Ping Gong Kai", "phone recording counterattack"],
 },
 }


def mock_passing_episode_plan_payload(episode_count: int = 1) -> dict[str, Any]:
 return {
 "episodes": [
 {
 "episode_number": idx + 1,
 "title": f"Mock Episode {idx + 1}",
 "summary": (
 "HeroZhuang Kai conference room discover evidence Bei Qiang, Li Ke Yong phone recording counterattack, "
 "Bi Dui Shou Jiao Chu Yao Shi, Que Zai evidence back view Kan Dao new signature."
),
 "plot_points": [
 {
 "order": 1,
 "description": "Kai Chang Gou Zi: HeroZhuang Kai Men, evidence Zheng Bei Sai Jin Bao Xian Xiang.",
 },
 {
 "order": 2,
 "description": "Shuang Dian Luo Dian: HeroBo Fang Lu Yin, Bi Dui Shou Jiao Chu Yao Shi.",
 },
 {"order": 3, "description": "Jie Wei Ka Dian: evidence back view Chu Xian new signature."},
 ],
 "character_arcs": {"Hero": "Learns trust"},
 "conflicts": [
 {
 "type": "mock",
 "description": "HeroHe Dui Shou Zheng Duo Xian Hai evidence",
 "intensity": "high",
 }
 ],
 "scene_count": 3,
 "payoff": "HeroBo Fang Lu Yin, Bi Dui Shou Jiao Chu Bao Xian Xiang Yao Shi.",
 "cliffhanger": "evidence back view Chu Xian new signature.",
 "hook_plan": {
 "opening_hook": "HeroZhuang Kai Men discover evidence Bei Qiang.",
 "escalation_plan": "Dui Shou Fan YaoHeroTou Qie.",
 "payoff_plan": "HeroYong recording counterattack.",
 },
 "cliffhanger_plan": ["evidence back view Chu Xian new signature", "GuideChen Mo Li Chang"],
 "ad_snippets": [
 {
 "duration_seconds": 15,
 "hook": "Ta Lu Xia Le Suo You Xian Hai",
 "visual_summary": "phone recording Jie Mian He Yao Shi close-up",
 "call_to_action": "Kan Ta Ru He Fan Pan",
 }
 ],
 "scenes": [
 {
 "scene_number": 1,
 "slug_line": "INT. conference room - day",
 "location": "conference room",
 "time_of_day": "day",
 "summary": "Kai Chang Gou Zi: HeroZhuang Kai Men, evidence Zheng Bei Sai Jin Bao Xian Xiang.",
 "visual_anchor": "HeroDing Zhu Bao Xian Xiang De Yan Shen close-up",
 "dialogue_function": "reveal",
 },
 {
 "scene_number": 2,
 "slug_line": "INT. conference room - day",
 "location": "conference room",
 "time_of_day": "day",
 "summary": "Shuang Dian: HeroBo Fang Lu Yin, Bi Dui Shou Jiao Chu Yao Shi.",
 "visual_anchor": "phone recording Jie Mian close-up",
 "dialogue_function": "counterattack",
 },
 {
 "scene_number": 3,
 "slug_line": "INT. Zou Lang - day",
 "location": "Zou Lang",
 "time_of_day": "day",
 "summary": "cliffhanger: evidence back view Chu Xian new signature.",
 "visual_anchor": "HeroZuan Jin evidence De Shou Bu close-up",
 "dialogue_function": "reveal",
 },
 ],
 "structured_episode_contract": {
 "episode_goal": "HeroNa Dao Xian Hai evidence",
 "ignition_0_3s": "HeroZhuang Kai Men, evidence Bei Sai Jin Bao Xian Xiang.",
 "first_30s_reason": "audience Zhi Dao evidence Jue DingHeroNeng Fou Fan An.",
 "midpoint_jolt": "Dui Shou Fan YaoHeroTou Qie.",
 "payoff": "HeroYong recording counterattack, Na Dao Yao Shi.",
 "final_button_cliffhanger": "evidence back view Lu Chu new signature.",
 "visual_anchor": "phone recording Jie Mian, HeroZuan Jin evidence De Shou.",
 "information_delta": "new signature Zhi Xiang Geng Gao Ceng mastermind.",
 "dialogue_functions": [
 "reveal",
 "threat",
 "counterattack",
 "payoff",
 ],
 },
 }
 for idx in range(episode_count or 1)
 ]
 }


def _script_repair_payload() -> dict[str, Any]:
 return mock_passing_script_payload()


def _traffic_sheet_payload() -> dict[str, Any]:
 return {
 "episode_id": 1,
 "script_id": 1,
 "market_region": "NA",
 "micro_genre": "test",
 "assets": [
 {
 "asset_id": "ep1_asset01_15s",
 "duration_seconds": 15,
 "market_region": "NA",
 "micro_genre": "test",
 "hook_type": "reveal",
 "source_episode": 1,
 "source_timecode_start": "00:00:00",
 "source_timecode_end": "00:00:15",
 "key_line": "mock line",
 "visual_hook": "mock visual",
 "shot_list": ["shot 1"],
 "cliff_or_cta": "mock cta",
 "music_reference": None,
 "compliance_flags": [],
 }
 ],
 }


def _script_score_payload() -> dict[str, Any]:
 return {
 "overall_score": 4.6,
 "dimension_scores": {
 "conflict_intensity": 4.6,
 "character_recognizability": 4.4,
 "cultural_fit": 4.5,
 "clip_ability": 4.6,
 "logic_coherence": 4.4,
 },
 "verdict": "pass",
 "strengths": ["mock strength"],
 "risks": [],
 "rewrite_guidance": [],
 "suggested_ad_hooks": ["mock hook"],
 }
