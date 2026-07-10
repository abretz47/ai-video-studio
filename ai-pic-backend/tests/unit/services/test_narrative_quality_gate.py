from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from app.services.narrative_quality_gate import (
 NarrativeQualityGateError,
 attach_quality_gate_failure_to_task,
 build_quality_gate_report,
 enforce_episode_quality_gate_with_repair,
 enforce_script_quality_gate_with_repair,
 evaluate_episode_quality_gate,
 evaluate_script_quality_gate,
 make_quality_check,
)
from app.services.quality_gate_core import QUALITY_GATE_ERROR_CODE


def _episode(number: int = 1, *, character_name: str | None = None) -> dict[str, Any]:
 payload: dict[str, Any] = {
 "episode_number": number,
 "title": f"Di{number}Ji",
 "summary": "Lin Xue discover ledger Li De Mi Mi, Wei Ji Sheng Ji.",
 "plot_points": [{"description": "Lin Xue Duo to ledger, Chen Mo Zhui Shang Lai."}],
 "conflicts": [{"description": "Lin Xue He Chen Mo Zheng Duo ledger", "intensity": "high"}],
 "scene_count": 1,
 "scenes": [
 {
 "scene_number": 1,
 "slug_line": "Scene 1",
 "summary": "Lin Xue Duo to ledger.",
 }
 ],
 }
 if character_name:
 payload["characters"] = [{"name": character_name}]
 return payload


def _script_content(text: str | None = None) -> dict[str, Any]:
 return {
 "content": text or _passing_script_text(),
 "scenes": [
 {
 "scene_number": 1,
 "description": "Lin Xue Zai living room press Chen Mo.",
 }
 ],
 "dialogues": [
 {
 "scene_number": 1,
 "character": "Lin Xue",
 "content": "don't move!ledger Shang why You you De name?",
 },
 {
 "scene_number": 1,
 "character": "Chen Mo",
 "content": "Bu Shi Wo, N...someone altered it.",
 },
 ],
 "stage_directions": [
 {
 "scene_number": 1,
 "content": "Lin Xue Zhua Zhu ledger, Jing Bao Sheng Bi Jin.",
 }
 ],
 "metadata": {},
 }


def _passing_script_text() -> str:
 return "\n".join(
 [
 "【sound effect】Bang! The door is forced open.",
 "Scene 1 living room - night",
 "【fast】【emotion goal: Bi Chu Zhen Xiang】Lin Xue Zhua Zhu ledger, camera Tui Jin Ta Fa Dou De Shou.",
 "【sound effect】Jing Bao Sheng from Chuang Wai Bi Jin.",
 "Lin Xue: don't move!ledger Shang why You you De name?",
 "Chen Mo: Bu Shi Wo, N...someone altered it.",
 "(action)Chen Mo Hou Tui Ban Bu, Bei Zi Luo Di.",
 "Scene 2 Tian Tai - night",
 "【slow】【emotion goal: Zhi Zao Fan Zhuan】Lin Xue Ba ledger Ju Dao Deng Xia, red signature Lu Chu.",
 "Chen Mo: you Kan final Yi Ye.",
 "Lin Xue: Na real signed De Ren Shi Shui?",
 ]
)


class _RepairManager:
 def __init__(
 self,
 payloads: list[dict[str, Any]],
 *,
 cliffhanger_passes: list[bool] | None = None,
) -> None:
 self.payloads = list(payloads)
 self.cliffhanger_passes = list(cliffhanger_passes or [])
 self.calls = 0
 self.cliffhanger_calls = 0

 async def generate_text(self, **kwargs: Any) -> Any:
 schema = kwargs.get("json_schema") or {}
 if schema.get("name") == "script_cliffhanger_judgement":
 self.cliffhanger_calls += 1
 passed = (
 self.cliffhanger_passes.pop(0)
 if self.cliffhanger_passes
 else True
)
 return SimpleNamespace(
 success=True,
 provider=kwargs.get("prefer_provider") or "fake",
 model=kwargs.get("model") or "fake-model",
 data={
 "passed": passed,
 "score": 1.0 if passed else 0.0,
 "reason": "ok" if passed else "weak ending",
 "evidence": "tail",
 "suggestion": "Bu Qiang Jie Wei cliffhanger",
 },
)
 self.calls += 1
 payload = self.payloads.pop(0) if self.payloads else {}
 return SimpleNamespace(success=True, data=payload)


@pytest.mark.unit
def test_quality_gate_report_blocks_error_checks() -> None:
 gate = build_quality_gate_report(
 kind="script",
 checks=[
 make_quality_check("ok", True, "ok"),
 make_quality_check("bad", False, "blocking"),
 make_quality_check("warn", False, "warning", severity="warning"),
 ],
)

 assert gate["passed"] is False
 assert gate["score"] < 10
 assert [issue["id"] for issue in gate["blocking_issues"]] == ["bad"]
 assert [warning["id"] for warning in gate["warnings"]] == ["warn"]


@pytest.mark.unit
def test_episode_gate_blocks_unknown_character() -> None:
 gate = evaluate_episode_quality_gate(
 episodes=[_episode(character_name="Stranger")],
 story={"characters": [{"name": "Lin Xue"}]},
 episode_count=1,
)

 assert gate["passed"] is False
 assert any(issue["id"] == "episode_characters" for issue in gate["blocking_issues"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_episode_gate_repairs_for_two_rounds_then_passes() -> None:
 manager = _RepairManager(
 [
 {"episodes": []},
 {"episodes": [_episode()]},
 ]
)

 result = await enforce_episode_quality_gate_with_repair(
 ai_manager=manager,
 result={"normalized": {"episodes": []}},
 story={"characters": [{"name": "Lin Xue"}]},
 episode_count=1,
)

 assert result["quality_gate"]["passed"] is True
 assert manager.calls == 2
 assert len(result["quality_gate"]["repair_attempts"]) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_blocks_low_lint_score_and_unknown_speaker() -> None:
 content = _script_content("Pu Tong Wen Ben, Mei You Sheng Chan Biao Ji, Ye Mei You Xuan Nian Jie Wei.")
 content["dialogues"][0]["character"] = "Stranger"
 gate = await evaluate_script_quality_gate(
 content=content,
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
 result={},
 ai_manager=_RepairManager([], cliffhanger_passes=[False]),
)

 blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
 assert "script_lint" in blocking_ids
 assert "script_characters" in blocking_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_repairs_for_two_rounds_then_passes() -> None:
 manager = _RepairManager(
 [
 _script_content("Reng Ran Mei You hook He Xuan Nian."),
 _script_content(),
 ]
)

 result, content, gate = await enforce_script_quality_gate_with_repair(
 ai_manager=manager,
 result={},
 content=_script_content("Bad text."),
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
)

 assert gate["passed"] is True
 assert result["quality_gate"]["passed"] is True
 assert content["content"] == _passing_script_text()
 assert manager.calls == 2
 assert len(gate["repair_attempts"]) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_quality_gate_raises_after_repair_budget_exhausted() -> None:
 manager = _RepairManager([_script_content("Bad text."), _script_content("Reng Ran Huai.")])

 with pytest.raises(NarrativeQualityGateError) as exc_info:
 await enforce_script_quality_gate_with_repair(
 ai_manager=manager,
 result={},
 content=_script_content("Bad text."),
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
)

 assert exc_info.value.quality_gate["passed"] is False
 assert len(exc_info.value.quality_gate["repair_attempts"]) == 2


@pytest.mark.unit
def test_attach_quality_gate_failure_to_task_records_error_code() -> None:
 task = SimpleNamespace(parameters='{"agent_run":{"existing":true}}')
 gate = build_quality_gate_report(
 kind="episode",
 checks=[make_quality_check("bad", False, "blocking")],
)

 attach_quality_gate_failure_to_task(task, gate)

 assert QUALITY_GATE_ERROR_CODE in task.parameters
 assert '"existing": true' in task.parameters
 assert '"quality_gate"' in task.parameters
