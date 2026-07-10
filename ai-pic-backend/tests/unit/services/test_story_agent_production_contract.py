from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest


def _strong_outline() -> dict:
 return {
 "premise": "Wen Wen Zai company Nian Hui suddenly discover betrayal video Bei public, Bi Xu Dang Chang counterattack.",
 "synopsis": (
 "suddenly, Wen Wen Zai Nian Hui Xian Chang discover Tou Pai video Bei public, crisis He conflict Li Ke Bao Fa."
 "Ta Ding Zhu Ya Li Fan Cha evidence, tense Dui Kang Bu Duan escalate, Zhong Duan reveal Lin Wan_Shuang Ju Ce Shi_01300519Cai Shi real mastermind."
 "final climax Dui Jue Zhong truth Bao Guang, Wen Wen complete counterattack Bing Shou Shu Jie Ju."
),
 "main_conflict": "Wen Wen Bi Xu Zai public Xiu Ru He Zhi Chang Xian Hai Zhong Zhao Chu truth.",
 "resolution": "Wen Wen reveal truth, Jie Jue crisis Bing complete Ni Xi.",
 "main_characters": [
 {"name": "Wen Wen", "description": "Jin Rong Bai Ling"},
 {"name": "Lin Wan_Shuang Ju Ce Shi_01300519", "description": "Zhi Chang Dui Shou"},
 {"name": "A-Fei", "description": "Hun Hun"},
 ],
 "plot_structure": {
 "act1": "suddenly Bao Chu Xiu Ru video, Wen Wen Bei Po Dang Chang counterattack.",
 "act2": "Wei Ji Sheng Ji, Wen Wen Yu Lin Wan_Shuang Ju Ce Shi_01300519Wei Rao evidence tense Dui Kang.",
 "act3": "climax reveal truth, Wen Wen Jie Jue crisis complete Ni Xi Jie Ju.",
 },
 "hook_plan": {
 "opening_hook": "suddenly, Wen Wen Tui Men discover betrayal video Zheng Zai Bo Fang.",
 "escalation_plan": "conflict Mei Yi Chang Dou escalate.",
 "payoff_plan": "final truth reveal Bing complete counterattack.",
 "key_reversals": [
 {
 "beat_type": "hook",
 "description": "Tou Pai video public",
 "timing": "opening",
 "intensity": "high",
 }
 ],
 },
 "selling_points": ["opening public Xiu Ru", "Gao Ya Fan Ji", "Zhen Xiang Jie Shi", "Zhi Chang Ni Xi", "Qiang Ka Dian"],
 "cliffhanger_plan": ["Dan Shi Ta discover Mu Hou mastermind Ling You Qi Ren"],
 "ad_snippets": [
 {
 "duration_seconds": 15,
 "hook": "betrayal video public",
 "visual_summary": "Nian Hui Da Ping public evidence",
 "call_to_action": "Kan Ta Ru He counterattack",
 }
 ],
 }


def _strong_outline_with_contract() -> dict:
 outline = _strong_outline()
 outline["structured_story_contract"] = {
 "target_audience": "urban Zhi Chang Ni Xi user",
 "core_emotional_pain": "professional Neng Li Bei public Zhi Yi, Xin Ren Bei Nei Bu Ren betrayal",
 "big_expectation": "Wen Wen Cha Qing data Cuan Gai truth Bing Duo Hui project Zhu Dao Quan",
 "small_expectation_ladder": [
 "Qian San Ji Na Dao Hui Yi recording",
 "Di8-12Ji Bi Chu Cuan Gai data De Ren",
 "Di20-30Ji public Mu Hou Jiao Yi evidence",
 ],
 "protagonist_goal": "San Tian INT Zhao Chu Cuan Gai data De Nei Bu Ren",
 "structural_conflict": "Wen Wen Bi Xu Jie Yong Zhi Yi Ta De team Zi Yuan Fan Cha team Nei Bu mastermind",
 "information_gap": "audience Zhi Dao recording exists, Dui Shou Bu Zhi Dao key camera Yi Bei Pai Xia",
 "first_three_episode_spine": "identity, evidence, He Xin conflict Qian San Ji Li Zhu",
 "stage_highs": ["conference room counterattack", "Zou Lang Qiang phone", "Dong Shi Hui Fan Pan"],
 "shootability": "conference room, office, Zou Lang San Lei Di Cheng Ben Ke Pai scene",
 "compliance_risks": [],
 "traffic_hooks": ["Da Ping public Cuan Gai data", "phone recording counterattack"],
 }
 return outline


def _production_generate_kwargs() -> dict:
 return {
 "title": "APQuan Lian Lu return Yang Pian",
 "story_format": "short_drama",
 "genre": "drama",
 "characters": [
 {"name": "Wen Wen", "description": "Shang Ye Zi Xun company project Fu Ze Ren"},
 {"name": "Lin Wan_Shuang Ju Ce Shi_01300519", "description": "Zhi Chang Dui Shou"},
 {"name": "A-Fei", "description": "Wai Bu Ya Li Lai Yuan"},
 ],
 "market_region": "CN",
 "micro_genre": "Zhi Chang Ni Xi",
 "pacing_template": "twist-heavy",
 "hook_plan": {"opening_hook": "opening Zhi Jie Gei Chu conflict Jie Guo"},
 "twist_density": "2+/Ji",
 "cliffhanger_plan": ["Yong not yet Jie Kai De Mi Mi Zuo Wei Xia Yi Ji Yin Zi"],
 "ad_snippets": [],
 "theme": "Shang Ye Zhi Chang",
 "target_audience": "Cheng Ren",
 "duration_minutes": 3,
 "setting_time": "modern",
 "setting_location": "Shang Ye Zi Xun company",
 "world_building": None,
 "additional_requirements": None,
 "style_preferences": [],
 "content_restrictions": [],
 "model": "deepseek-v4-flash",
 "prefer_provider": "deepseek",
 "temperature": 0.7,
 "generation_mode": "production",
 }


@pytest.mark.asyncio
async def test_story_agent_repairs_production_outline_until_contract_gate_passes():
 from app.prompts.templates import PromptTemplate
 from app.services.story_agent import LANGGRAPH_AVAILABLE, StoryLangGraphAgent

 if not LANGGRAPH_AVAILABLE:
 pytest.skip("langgraph not available")

 calls: list[str] = []
 repair_vars: dict = {}
 responses = [_strong_outline(), _strong_outline_with_contract()]

 async def _generate_text(**kwargs: object):
 schema = kwargs.get("json_schema")
 calls.append(str(schema.get("name") if isinstance(schema, dict) else ""))
 return SimpleNamespace(
 success=True,
 data=responses[len(calls) - 1],
 provider="deepseek",
 model="deepseek-v4-flash",
 usage={"total_tokens": 1},
)

 def _render_prompt(template_name: str, variables: dict) -> str:
 if template_name == PromptTemplate.STORY_OUTLINE_REPAIR.value:
 repair_vars.update(variables)
 return "repair prompt"
 return "prompt"

 service = SimpleNamespace(ai_manager=SimpleNamespace(generate_text=_generate_text))
 agent = StoryLangGraphAgent(service)

 with patch("app.services.story_agent.prompt_manager.render_prompt", _render_prompt):
 result = await agent.generate(**_production_generate_kwargs())

 assert calls == ["story_outline", "story_outline_repair"]
 assert result["quality_gate"]["passed"] is True
 assert result["normalized"]["structured_story_contract"]["compliance_risks"] == []
 assert repair_vars["production_mode"] is True
 assert "structured_story_contract_required" in repair_vars["quality_gate_issues"]


@pytest.mark.asyncio
async def test_story_agent_production_schema_requires_structured_contract():
 from app.services.story_agent import LANGGRAPH_AVAILABLE, StoryLangGraphAgent

 if not LANGGRAPH_AVAILABLE:
 pytest.skip("langgraph not available")

 captured_schema: dict = {}

 async def _generate_text(**kwargs: object):
 schema = kwargs.get("json_schema")
 if isinstance(schema, dict):
 captured_schema.update(schema.get("schema") or {})
 return SimpleNamespace(
 success=True,
 data=_strong_outline_with_contract(),
 provider="deepseek",
 model="deepseek-v4-flash",
 usage={"total_tokens": 1},
)

 service = SimpleNamespace(ai_manager=SimpleNamespace(generate_text=_generate_text))
 agent = StoryLangGraphAgent(service)

 with patch(
 "app.services.story_agent.prompt_manager.render_prompt", return_value="prompt"
):
 await agent.generate(**_production_generate_kwargs())

 assert "structured_story_contract" in captured_schema["required"]
 contract_schema = captured_schema["properties"]["structured_story_contract"]
 assert "target_audience" in contract_schema["required"]
 assert "traffic_hooks" in contract_schema["required"]
