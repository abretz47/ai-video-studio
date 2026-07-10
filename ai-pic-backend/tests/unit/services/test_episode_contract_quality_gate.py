from __future__ import annotations

import pytest
from app.services.narrative_quality_gate import evaluate_episode_quality_gate


def _episode() -> dict:
    return {
        "episode_number": 1,
        "title": "Di1Ji",
        "summary": "Lin Xue discover ledger Li Mi Mi，crisis escalate。",
        "plot_points": [{"description": "Lin Xue Duo to ledger，Chen Mo Zhui Shang Lai。"}],
        "conflicts": [{"description": "Lin Xue and Chen Mo Zheng Duo ledger", "intensity": "high"}],
        "scene_count": 1,
        "scenes": [
            {
                "scene_number": 1,
                "slug_line": "Scene 1",
                "summary": "Lin Xue Duo to ledger。",
            }
        ],
    }


@pytest.mark.unit
def test_episode_gate_requires_structured_contract_in_production() -> None:
    gate = evaluate_episode_quality_gate(
        episodes=[_episode()],
        story={"characters": [{"name": "Lin Xue"}]},
        episode_count=1,
        require_episode_contract=True,
    )

    assert gate["passed"] is False
    assert any(
        issue["id"] == "structured_episode_contract_required"
        for issue in gate["blocking_issues"]
    )


@pytest.mark.unit
def test_episode_gate_accepts_structured_contract_when_required() -> None:
    episode = _episode()
    episode["payoff"] = "Lin Xue Dang Zhong Na Dao ledger，Bi Chen Mo Jiao Chu Yao Shi。"
    episode["cliffhanger"] = "ledger final Yi Ye Lu Chu Lin Xue Fu Qin signature。"
    episode["structured_episode_contract"] = {
        "episode_goal": "Lin Xue Duo to ledger",
        "ignition_0_3s": "Lin Xue Zhuang Kai Men，ledger be Chen Mo Sai Jin Bao Xian Xiang。",
        "first_30s_reason": "audience Li Ke Zhi Dao ledger Jue Ding Lin Xue Neng Fou Fan An。",
        "midpoint_jolt": "Chen Mo Liang Chu Di Er Ba Yao Shi，Fan Yao Lin Xue Tou Qie。",
        "payoff": "Lin Xue Yong phone recording counterattack，Na Dao ledger。",
        "final_button_cliffhanger": "ledger final Yi Ye Chu Xian Fu Qin signature。",
        "visual_anchor": "phone recording Jie Mian close-up、Lin Xue Zuan Jin ledger Shou。",
        "information_delta": "audience De Zhi Fu Qin Ke Neng Can Yu Jiu An。",
        "dialogue_functions": ["reveal", "counterattack", "payoff"],
    }

    gate = evaluate_episode_quality_gate(
        episodes=[episode],
        story={"characters": [{"name": "Lin Xue"}]},
        episode_count=1,
        require_episode_contract=True,
    )

    blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
    assert "structured_episode_contract_required" not in blocking_ids
