from __future__ import annotations

import pytest
from app.services.narrative_quality_gate import NarrativeQualityGateError
from app.services.script.production_pipeline import (
    annotate_storyboard_frames_with_hooks,
    build_hook_schedule,
    run_production_script_generation,
    score_passes,
)


def _scoring(
    verdict: str,
    overall: float,
    guidance: list[str] | None = None,
    dimensions: dict[str, float] | None = None,
    asset_count: int = 1,
) -> dict:
    dimension_scores = dimensions or {
        "conflict_intensity": overall,
        "character_recognizability": overall,
        "cultural_fit": overall,
        "clip_ability": overall,
        "logic_coherence": overall,
    }
    return {
        "script_score": {
            "overall_score": overall,
            "verdict": verdict,
            "dimension_scores": dimension_scores,
            "rewrite_guidance": guidance or [],
        },
        "traffic_sheet": {
            "assets": [
                {
                    "duration_seconds": 15,
                    "hook_type": "reveal",
                    "key_line": "Ta Zheng Ju Ju Dao camera before",
                    "visual_hook": "protagonist Dang Zhong Ju Zheng",
                    "cliff_or_cta": "continue Kan Ta Ru He counterattack",
                }
            ]
        },
        "asset_tags": {"asset_count": asset_count, "hook_types": ["reveal"]},
    }


@pytest.mark.unit
def test_build_hook_schedule_uses_marketing_and_episode_beats():
    schedule = build_hook_schedule(
        {"title": "T", "main_conflict": "identity be Qiang"},
        {
            "summary": "heroine be Dang Zhong Xiu Ru",
            "plot_points": [{"description": "heroine Na Chu recording", "timing": "Zhong Duan"}],
        },
        {
            "hook_plan": {
                "opening_hook": "Hun Li Xian Chang betrayal",
                "payoff_plan": "Nv Zhu Bo Fang Zheng Ju counterattack",
            },
            "cliffhanger_plan": ["Fan Pai Liang Chu Qin Zi Jian Ding"],
            "ad_snippets": [
                {
                    "duration_seconds": 15,
                    "hook": "Ta Bu Shi Ti Shen",
                    "visual_summary": "heroine Si Diao Jia He Tong",
                }
            ],
        },
    )

    assert schedule["opening_hook"] == "Hun Li Xian Chang betrayal"
    assert schedule["payoff"] == "Nv Zhu Bo Fang Zheng Ju counterattack"
    assert schedule["cliffhanger"] == "Fan Pai Liang Chu Qin Zi Jian Ding"
    assert schedule["conflict_ladder"][0]["description"] == "heroine Na Chu recording"
    assert schedule["ad_candidate_beats"][0]["hook"] == "Ta Bu Shi Ti Shen"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_production_generation_skips_rewrite_when_score_passes():
    generated_requirements: list[str] = []

    async def generate_attempt(attempt_no: int, requirements: str) -> dict:
        generated_requirements.append(requirements)
        return {
            "attempt": attempt_no,
            "result": {"generation_method": "fake"},
            "ai_content": {"content": "ok"},
            "script_content": "ok",
            "scenes": [],
            "dialogues": [],
            "stage_directions": [],
        }

    async def score_attempt(_generated: dict) -> dict:
        return _scoring("pass", 4.6)

    result = await run_production_script_generation(
        story={"title": "T"},
        episode={"summary": "S"},
        marketing_overrides={},
        base_additional_requirements=None,
        generate_attempt=generate_attempt,
        score_attempt=score_attempt,
    )

    assert len(result.attempts) == 1
    assert result.selected_attempt == 1
    assert result.review_required is False
    assert "hook_schedule" in generated_requirements[0]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_production_generation_rewrites_and_selects_pass():
    generated_requirements: list[str] = []
    scores = [_scoring("rewrite", 2.5, ["Bu Qiang opening conflict"]), _scoring("pass", 4.6)]

    async def generate_attempt(attempt_no: int, requirements: str) -> dict:
        generated_requirements.append(requirements)
        return {
            "attempt": attempt_no,
            "result": {"generation_method": f"fake-{attempt_no}"},
            "ai_content": {"content": f"draft {attempt_no}"},
            "script_content": f"draft {attempt_no}",
            "scenes": [],
            "dialogues": [],
            "stage_directions": [],
        }

    async def score_attempt(_generated: dict) -> dict:
        return scores.pop(0)

    result = await run_production_script_generation(
        story={"title": "T"},
        episode={"summary": "S"},
        marketing_overrides={},
        base_additional_requirements="keep Di Cheng Ben",
        generate_attempt=generate_attempt,
        score_attempt=score_attempt,
    )

    assert len(result.attempts) == 2
    assert result.selected_attempt == 2
    assert result.review_required is False
    assert "Bu Qiang opening conflict" in generated_requirements[1]
    assert result.metadata()["selected_attempt"] == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_production_generation_raises_after_six_low_quality_attempts():
    calls: list[int] = []
    scores = [
        _scoring("rewrite", 2.1, ["Zhong Xie before3seconds hook"]),
        _scoring("rewrite", 3.2, ["Ya Suo Zhong Duan Jie Shi"]),
        _scoring("review", 4.3, ["Bu Qiang Ren Wu Ke Bian Shi Du"]),
        _scoring("pass", 4.4, ["Reng Wei Da Dao Jing Pin Xian"]),
        _scoring("review", 4.1, ["Bu Qiang Di Er Chang Guang Gao hook"]),
        _scoring("review", 4.2, ["Bu Qiang Fan Pai Dong Ji"]),
    ]

    async def generate_attempt(attempt_no: int, _requirements: str) -> dict:
        calls.append(attempt_no)
        return {
            "attempt": attempt_no,
            "result": {"generation_method": f"fake-{attempt_no}"},
            "ai_content": {"content": f"draft {attempt_no}"},
            "script_content": f"draft {attempt_no}",
            "scenes": [],
            "dialogues": [],
            "stage_directions": [],
        }

    async def score_attempt(_generated: dict) -> dict:
        return scores.pop(0)

    with pytest.raises(NarrativeQualityGateError) as exc_info:
        await run_production_script_generation(
            story={"title": "T"},
            episode={"summary": "S"},
            marketing_overrides={},
            base_additional_requirements=None,
            generate_attempt=generate_attempt,
            score_attempt=score_attempt,
        )

    assert calls == [1, 2, 3, 4, 5, 6]
    gate = exc_info.value.quality_gate
    assert gate["passed"] is False
    blocking_ids = {issue["id"] for issue in gate["blocking_issues"]}
    assert "production_script_score" in blocking_ids
    details = gate["blocking_issues"][0]["details"]
    assert details["thresholds"] == {"overall": 4.5, "dimension": 4.2}
    assert details["selected_attempt"] == 4
    assert len(details["attempts"]) == 6
    assert details["attempts"][-1]["overall_score"] == 4.2
    assert details["rewrite_guidance"][0] == "Reng Wei Da Dao Jing Pin Xian"
    assert "Zheng Ti ScriptScore Bi Xu Ti Sheng to 4.5+" in details["rewrite_guidance"][1]


@pytest.mark.unit
def test_score_pass_requires_thresholds_even_when_verdict_is_pass():
    scoring = _scoring("pass", 4.4)

    assert score_passes(scoring) is False


@pytest.mark.unit
def test_annotate_storyboard_frames_with_hooks_uses_traffic_sheet():
    frames = [
        {"description": "Nv Zhu Chong Jin conference room", "beat_type": "action"},
        {"description": "heroine Ju Qi Zheng Ju complete counterattack", "beat_type": "dialogue"},
        {"description": "Men Wai Tu Ran Chu Xian Hei Yi Ren", "beat_type": "action"},
    ]

    changed = annotate_storyboard_frames_with_hooks(
        frames,
        hook_schedule={"opening_hook": "conflict opening"},
        scoring=_scoring("pass", 4.5),
    )

    assert changed >= 2
    assert frames[0]["hook_tag"] == "opening_hook"
    assert frames[0]["ad_snippet"]["hook"] == "Ta Zheng Ju Ju Dao camera before"
    assert frames[1]["hook_tag"] == "payoff"
    assert frames[2]["hook_tag"] == "cliffhanger"
