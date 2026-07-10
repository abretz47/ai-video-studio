from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from app.services.narrative_quality_gate import evaluate_script_quality_gate


class _PassingCliffhangerManager:
 async def generate_text(self, **kwargs: Any) -> Any:
 return SimpleNamespace(
 success=True,
 data={
 "passed": True,
 "score": 1.0,
 "reason": "ok",
 "evidence": "tail",
 "suggestion": "",
 },
 provider=kwargs.get("prefer_provider") or "fake",
 model=kwargs.get("model") or "fake-model",
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_blocks_fallback_dialogue_content() -> None:
 content = {
 "content": "\n".join(
 [
 "【sound effect】Bang! The door is forced open.",
 "Scene 1 living room - night",
 "【fast】【emotion goal: Bi Chu Zhen Xiang】Lin Xue Zhua Zhu ledger.",
 "Lin Xue: Na real signed De Ren Shi Shui?",
 ]
),
 "scenes": [{"scene_number": 1, "description": "Lin Xue Zai living room press Chen Mo."}],
 "dialogues": [
 {
 "scene_number": 1,
 "character": "voiceover",
 "content": "Lin Xue Zai living room press Chen Mo.",
 "fallback": True,
 "fallback_reason": "missing_dialogues",
 }
 ],
 "stage_directions": [{"scene_number": 1, "content": "Lin Xue Zhua Zhu ledger."}],
 "metadata": {},
 }

 gate = await evaluate_script_quality_gate(
 content=content,
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
 result={},
 ai_manager=_PassingCliffhangerManager(),
)

 blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
 assert "script_dialogue_fallback" in blocking_ids
