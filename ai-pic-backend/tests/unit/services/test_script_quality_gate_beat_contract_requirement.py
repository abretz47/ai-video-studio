from __future__ import annotations

from typing import Any

import pytest

from app.services.narrative_quality_gate import evaluate_script_quality_gate


def _script_content() -> dict[str, Any]:
    return {
        "content": "\n".join(
            [
                "【sound effect】Bang! The door is forced open.",
                "Scene 1 living room - night",
                "Lin Xue Zhua Zhu ledger，Jing Bao Sheng Bi Jin。",
                "Lin Xue：don't move！ledger on why have Ni name？",
                "Chen Mo：Bu Shi Wo，someone altered it。",
            ]
        ),
        "scenes": [{"scene_number": 1, "description": "Lin Xue in living room press Chen Mo。"}],
        "dialogues": [
            {
                "scene_number": 1,
                "character": "Lin Xue",
                "content": "don't move！ledger on why have Ni name？",
            },
            {"scene_number": 1, "character": "Chen Mo", "content": "someone altered it。"},
        ],
        "stage_directions": [
            {"scene_number": 1, "content": "Lin Xue Zhua Zhu ledger，Jing Bao Sheng Bi Jin。"}
        ],
        "metadata": {},
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_requires_beat_contract_when_requested() -> None:
    gate = await evaluate_script_quality_gate(
        content=_script_content(),
        story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
        result={},
        require_beat_contract=True,
    )

    blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
    assert "script_beat_contract_required" in blocking_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_does_not_require_beat_contract_by_default() -> None:
    gate = await evaluate_script_quality_gate(
        content=_script_content(),
        story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
        result={},
    )

    all_check_ids = {check["id"] for check in gate["checks"]}
    assert "script_beat_contract_required" not in all_check_ids
