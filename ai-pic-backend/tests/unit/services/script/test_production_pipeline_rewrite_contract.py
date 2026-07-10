from __future__ import annotations

import pytest
from app.services.script.production_pipeline import (
 render_production_requirements,
 run_production_script_generation,
)


def _scoring(
 verdict: str,
 overall: float,
 *,
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
 "rewrite_guidance": [],
 },
 "traffic_sheet": {"assets": []},
 "asset_tags": {"asset_count": asset_count, "hook_types": ["reveal"]},
 }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_production_generation_derives_guidance_from_strict_score_gaps():
 generated_requirements: list[str] = []
 scores = [
 _scoring(
 "review",
 4.2,
 dimensions={
 "conflict_intensity": 4.5,
 "character_recognizability": 4.0,
 "cultural_fit": 4.5,
 "clip_ability": 4.0,
 "logic_coherence": 4.0,
 },
 asset_count=0,
),
 _scoring("pass", 4.6, asset_count=3),
 ]

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
 base_additional_requirements=None,
 generate_attempt=generate_attempt,
 score_attempt=score_attempt,
)

 assert result.selected_attempt == 2
 assert "Zheng Ti ScriptScore Bi Xu Ti Sheng to 4.5+" in generated_requirements[1]
 assert "character_recognizability=4.0" in generated_requirements[1]
 assert "clip_ability=4.0" in generated_requirements[1]
 assert "logic_coherence=4.0" in generated_requirements[1]
 assert "Zhi Shao 15s, 30s, 60s" in generated_requirements[1]


@pytest.mark.unit
def test_render_production_requirements_expands_commercial_rewrite_contract():
 requirements = render_production_requirements(
 base_additional_requirements=None,
 hook_schedule={"opening_hook": "customer Pai Zhuo Zhi Yi data"},
 rewrite_guidance=["character Bian Shi Du Bu Zu", "logic Yi Zhi Xing You Lou Dong"],
 attempt_no=2,
)

 assert "Shang Ye Ping Fen Ying Jiao Fu Qing Dan" in requirements
 assert "overall_score >= 4.5" in requirements
 assert "Mei Xiang >= 4.2" in requirements
 assert "15s, 30s, 60s San Lei Tou Liu Pian Duan" in requirements
 assert "Bu Neng Bei Protagonist Yi Wen Jiu Cheng Ren" in requirements
 assert "Zhu Li Bi Xu You Ju Ming action Biao Qian" in requirements
 assert "Si Xia Dui Zhi He Li Xing" in requirements
 assert "customer Zhang total Gei Chu60seconds Che Dan countdown" in requirements
 assert "Shu Zi Bu Hui Sa Huang, Kan Shi Jian Chuo" in requirements
 assert "Gai Wan Gei Ni20Wan, Bu Zuo Jiu Cai you" in requirements
 assert "Fan Xiu Luo Di Jiao Yan" in requirements
 assert "Zhen Dui「character Bian Shi Du Bu Zu」" in requirements
 assert "visible_event" in requirements
 assert "action_line" in requirements
