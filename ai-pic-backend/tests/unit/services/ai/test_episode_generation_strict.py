from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import app.services.ai.episode_direct_generation as episode_direct_generation
import app.services.ai.episodes as episodes_module
import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_call_ai_manager_episode_repairs_episode_count_mismatch(
 monkeypatch,
) -> None:
 calls: List[Dict[str, Any]] = []

 class _MockAIManager:
 def __init__(self) -> None:
 self._idx = 0

 async def generate_text(self, prompt: str, **kwargs: Any) -> Any:
 calls.append(kwargs)
 self._idx += 1
 if self._idx == 1:
 return SimpleNamespace(
 success=True,
 data='{"episodes":[{"episode_number":1,"title":"t1","summary":"s1"}]}',
 provider="mock1",
 model="m1",
 usage={"total_tokens": 1},
)
 return SimpleNamespace(
 success=True,
 data='{"episodes":[{"episode_number":1,"title":"t1","summary":"s1"},{"episode_number":2,"title":"t2","summary":"s2"}]}',
 provider="mock2",
 model="m2",
 usage={"total_tokens": 2},
)

 async def _fake_postprocess_episode_plan_list(**kwargs: Any):
 return kwargs["episodes"], {"ok": True}, "REWRITTEN"

 monkeypatch.setattr(
 episode_direct_generation,
 "postprocess_episode_plan_list",
 _fake_postprocess_episode_plan_list,
)

 class _Svc(episodes_module.EpisodeGenerationMixin):
 def __init__(self, ai_manager: Any) -> None:
 self.ai_manager = ai_manager

 service = _Svc(_MockAIManager())
 result = await service._call_ai_manager_episode(
 story={"title": "x"},
 episode_count=2,
 episode_duration=None,
 focus_characters=None,
 plot_complexity="medium",
 pacing="medium",
 additional_requirements=None,
 style_preferences=None,
 model=None,
 prefer_provider=None,
 temperature=0.7,
)

 assert isinstance(result, dict)
 assert result["normalized"]["episodes"]
 assert len(result["normalized"]["episodes"]) == 2
 assert result["content"] == "REWRITTEN"
 assert result["provider_used"] == "mock2"
 assert result["model_used"] == "m2"
 assert result["generation_method"] == "ai_mock2"
 assert len(result.get("repair_attempts") or []) == 1
 assert len(calls) == 2

 schema = calls[0]["json_schema"]["schema"]
 assert schema["properties"]["episodes"]["minItems"] == 2
 assert schema["properties"]["episodes"]["maxItems"] == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_call_ai_manager_episode_production_prompt_requires_contract(
 monkeypatch,
) -> None:
 captured_prompts: List[str] = []

 class _MockAIManager:
 async def generate_text(self, prompt: str, **_: Any) -> Any:
 captured_prompts.append(prompt)
 return SimpleNamespace(
 success=True,
 data=(
 '{"episodes":[{"episode_number":1,"title":"t1","summary":"s1",'
 '"conflicts":[{"description":"Hero faces a locked evidence box",'
 '"intensity":"high"}],"scenes":[{"scene_number":1,'
 '"summary":"Kai Chang Gou Zi: HeroZhuang Kai Men discover evidence Bei Suo.",'
 '"visual_anchor":"HeroShou Zhi An Zhu Bao Xian Xiang",'
 '"action_obstacle_cost":"HeroZhuang Men/Bao Xian Xiang Zu Dang/Bao Lu Lu Yin/Xuan Ze public evidence/Qian Ming Chu Xian",'
 '"dialogue_function":"reveal"}],'
 '"structured_episode_contract":{"episode_goal":"Qiang Hui Zheng Ju",'
 '"ignition_0_3s":"HeroZhuang Kai Men",'
 '"first_30s_reason":"evidence Ji Jiang delete",'
 '"midpoint_jolt":"Dui Shou Fan Suo Bao Xian Xiang",'
 '"payoff":"HeroBo Fang Lu Yin",'
 '"final_button_cliffhanger":"evidence back view Chu Xian new signature",'
 '"visual_anchor":"phone recording He Shou Bu close-up",'
 '"information_delta":"new signature Zhi Xiang mastermind",'
 '"dialogue_functions":["reveal","counterattack","payoff"]}}]}'
),
 provider="mock",
 model="m",
 usage={},
)

 async def _fake_postprocess_episode_plan_list(**kwargs: Any):
 return kwargs["episodes"], {"ok": True}, "REWRITTEN"

 monkeypatch.setattr(
 episode_direct_generation,
 "postprocess_episode_plan_list",
 _fake_postprocess_episode_plan_list,
)

 class _Svc(episodes_module.EpisodeGenerationMixin):
 def __init__(self, ai_manager: Any) -> None:
 self.ai_manager = ai_manager

 service = _Svc(_MockAIManager())
 result = await service._call_ai_manager_episode(
 story={"title": "x", "story_format": "short_drama"},
 episode_count=1,
 episode_duration=None,
 focus_characters=None,
 plot_complexity="medium",
 pacing="medium",
 additional_requirements=None,
 style_preferences=None,
 model=None,
 prefer_provider=None,
 temperature=0.7,
 generation_mode="production",
)

 assert result is not None
 assert result["generation_mode"] == "production"
 assert result["production_mode"] is True
 assert "structured_episode_contract" in captured_prompts[0]
 assert "0-3 seconds ignition" in captured_prompts[0]
 assert "dialogue_function" in captured_prompts[0]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_call_ai_manager_episode_returns_none_when_repairs_fail() -> None:
 class _MockAIManager:
 async def generate_text(self, prompt: str, **_: Any) -> Any:
 return SimpleNamespace(
 success=True,
 data='{"episodes":[{"episode_number":1,"title":"t1","summary":"s1"}]}',
 provider="mock",
 model="m",
 usage={},
)

 class _Svc(episodes_module.EpisodeGenerationMixin):
 def __init__(self, ai_manager: Any) -> None:
 self.ai_manager = ai_manager

 service = _Svc(_MockAIManager())
 result = await service._call_ai_manager_episode(
 story={"title": "x"},
 episode_count=2,
 episode_duration=None,
 focus_characters=None,
 plot_complexity="medium",
 pacing="medium",
 additional_requirements=None,
 style_preferences=None,
 model=None,
 prefer_provider=None,
 temperature=0.7,
)

 assert result is None
