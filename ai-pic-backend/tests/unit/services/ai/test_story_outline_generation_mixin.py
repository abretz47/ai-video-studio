from __future__ import annotations

import logging
from typing import Any

import app.services.ai.story_outline as story_outline_module
import pytest
from app.services.ai.story_outline import StoryOutlineMixin


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_story_outline_direct_production_prompt_requires_contract(
 monkeypatch,
) -> None:
 captured: dict[str, Any] = {}

 async def _fake_generate_with_repair(**kwargs: Any) -> dict[str, Any]:
 captured["base_prompt"] = kwargs["base_prompt"]
 return {
 "content": '{"premise":"p"}',
 "normalized": {
 "premise": "HeroZai press conference discover evidence Bei Qiang, Bi Xu Dang Chang counterattack.",
 "synopsis": "HeroWei Rao evidence Qiang Duo He public Xiu Ru counterattack, Qian San Ji Li Zhu He Xin conflict.",
 "structured_story_contract": {
 "target_audience": "urban Fu Chou user",
 "core_emotional_pain": "Zun Yan Bei public Nian Ya",
 "big_expectation": "HeroDuo Hui evidence Bing Cha Chu mastermind",
 "small_expectation_ladder": ["Qian San Ji Na recording", "Di Shi Ji Bi Chu ledger"],
 "protagonist_goal": "Qiang Hui press conference Xian Hai evidence",
 "structural_conflict": "HeroBi Xu Jie Dui Shou Zi Yuan Fan Cha Dui Shou",
 "information_gap": "audience Zhi Dao recording exists, Dui Shou Bu Zhi Dao Yi Ru Jing",
 "first_three_episode_spine": "identity, evidence, mastermind Qian San Ji Li Zhu",
 "stage_highs": ["press conference counterattack", "Dong Shi Hui Fan Pan"],
 "shootability": "Fa Bu Hui Ting, Zou Lang, office Ke Pai",
 "compliance_risks": [],
 "traffic_hooks": ["Da Ping Gong Kai", "Shou Ji Lu Yin"],
 },
 },
 "validation_errors": [],
 "repair_attempts": [],
 "first_attempt": {
 "provider_used": "mock-provider",
 "model_used": "mock-model",
 "usage": {},
 },
 }

 monkeypatch.setattr(
 story_outline_module, "generate_with_repair", _fake_generate_with_repair
)

 class _Svc(StoryOutlineMixin):
 def __init__(self) -> None:
 self.story_agent = None
 self.ai_manager = object()
 self.logger = logging.getLogger(__name__)

 service = _Svc()
 result = await service.generate_story_outline(
 title="T",
 genre="drama",
 characters=[{"name": "Hero", "description": "lead"}],
 story_format="short_drama",
 generation_mode="production",
)

 assert result is not None
 assert result["generation_mode"] == "production"
 assert result["production_mode"] is True
 prompt = captured["base_prompt"]
 assert "structured_story_contract" in prompt
 assert "Da Qi Dai" in prompt
 assert "Xiao Qi Dai Jie Ti" in prompt
 assert "information Cha She Ji" in prompt
 assert "Qian San Ji Li Zhu Xian" in prompt
