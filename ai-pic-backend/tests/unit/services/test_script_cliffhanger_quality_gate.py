from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from app.services.narrative_quality_gate import (
    NarrativeQualityGateError,
    enforce_script_quality_gate_with_repair,
)


def _passing_script_text() -> str:
    return "\n".join(
        [
            "【sound effect】Bang! The door is forced open.",
            "Scene 1 living room - night",
            "【fast】【emotion goal：Bi Chu truth】Lin Xue Zhua Zhu ledger，camera Tui Jin Ta Fa Dou Shou。",
            "【sound effect】Jing Bao Sheng from Chuang Wai Bi Jin。",
            "Lin Xue：don't move！ledger on why have Ni name？",
            "Chen Mo：Bu Shi Wo，N...someone altered it。",
            "（action）Chen Mo Hou Tui Ban Bu，Bei Zi Luo Di。",
            "Scene 2 Tian Tai - night",
            "【slow】【emotion goal：Zhi Zao Fan Zhuan】Lin Xue ledger Ju Dao Deng Xia，red signature Lu Chu。",
            "Chen Mo：Ni Kan final Yi Ye。",
            "Lin Xue：Na real sign Ren is who？",
        ]
    )


def _script_content(text: str | None = None) -> dict[str, Any]:
    return {
        "content": text or _passing_script_text(),
        "scenes": [{"scene_number": 1, "description": "Lin Xue in living room press Chen Mo。"}],
        "dialogues": [
            {"scene_number": 1, "character": "Lin Xue", "content": "don't move！ledger on why have Ni name？"},
            {"scene_number": 1, "character": "Chen Mo", "content": "Bu Shi Wo，N...someone altered it。"},
        ],
        "stage_directions": [{"scene_number": 1, "content": "Lin Xue Zhua Zhu ledger，Jing Bao Sheng Bi Jin。"}],
        "metadata": {},
    }


class _RepairManager:
    def __init__(
        self,
        payloads: list[dict[str, Any]],
        *,
        cliffhanger_passes: list[bool],
    ) -> None:
        self.payloads = list(payloads)
        self.cliffhanger_passes = list(cliffhanger_passes)
        self.calls = 0
        self.cliffhanger_calls = 0

    async def generate_text(self, **kwargs: Any) -> Any:
        schema = kwargs.get("json_schema") or {}
        if schema.get("name") == "script_cliffhanger_judgement":
            self.cliffhanger_calls += 1
            passed = self.cliffhanger_passes.pop(0)
            return SimpleNamespace(
                success=True,
                provider=kwargs.get("prefer_provider") or "fake",
                model=kwargs.get("model") or "fake-model",
                data={
                    "passed": passed,
                    "score": 1.0 if passed else 0.8,
                    "reason": "ok" if passed else "weak ending",
                    "evidence": "tail",
                    "suggestion": "Bu Qiang Jie Wei cliffhanger",
                },
            )
        self.calls += 1
        payload = self.payloads.pop(0) if self.payloads else {}
        return SimpleNamespace(success=True, data=payload)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_repairs_when_cliffhanger_prompt_fails() -> None:
    manager = _RepairManager([_script_content()], cliffhanger_passes=[False, True])

    result, _content, gate = await enforce_script_quality_gate_with_repair(
        ai_manager=manager,
        result={},
        content=_script_content(),
        story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
        model="deepseek:deepseek-v4-flash",
        prefer_provider="deepseek",
    )

    assert gate["passed"] is True
    assert result["quality_gate"]["passed"] is True
    assert manager.calls == 1
    assert manager.cliffhanger_calls == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_blocks_when_cliffhanger_llm_unavailable() -> None:
    with pytest.raises(NarrativeQualityGateError) as exc_info:
        await enforce_script_quality_gate_with_repair(
            ai_manager=None,
            result={},
            content=_script_content(),
            story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
            max_repairs=0,
        )

    lint_issue = next(
        issue
        for issue in exc_info.value.quality_gate["blocking_issues"]
        if issue["id"] == "script_lint"
    )
    cliffhanger_rule = next(
        rule
        for rule in lint_issue["details"]["rules"]
        if rule["rule_id"] == "cliffhanger"
    )
    assert cliffhanger_rule["details"]["error"] == "cliffhanger_llm_unavailable"
