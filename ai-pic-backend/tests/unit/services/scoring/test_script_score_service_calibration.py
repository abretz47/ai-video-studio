"""
Calibration and provider-schema tests for ScriptScoreService.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.providers.base import AIModelType, AIResponse, AITaskType
from app.services.scoring.script_score_service import (
    ScriptScoreService,
    _script_score_json_schema,
)


@pytest.fixture
def mock_ai_service():
    service = MagicMock()
    service.ai_manager = MagicMock()
    service.ai_manager.generate_text = AsyncMock()
    return service


@pytest.fixture
def score_service(mock_ai_service):
    return ScriptScoreService(mock_ai_service)


@pytest.mark.asyncio
async def test_score_script_calibrates_when_commercial_anchors_are_present(
    score_service, mock_ai_service
):
    mock_ai_service.ai_manager.generate_text.return_value = AIResponse(
        success=True,
        data="""
        ```json
        {
            "overall_score": 4.0,
            "dimension_scores": {
                "conflict_intensity": 4.0,
                "character_recognizability": 3.5,
                "cultural_fit": 4.5,
                "clip_ability": 4.0,
                "logic_coherence": 3.5
            },
            "verdict": "review",
            "strengths": ["opening conflict Qiang"],
            "risks": ["character Dong Ji Bu Gou Ming Que", "Di2Chang Guo Du Lve Ping"],
            "rewrite_guidance": ["Nan Er Dong Ji Xu Bu Chong"],
            "suggested_ad_hooks": []
        }
        ```
        """,
        provider="mock",
        model="mock",
        task_type=AITaskType.SCRIPT_WRITING,
        model_type=AIModelType.TEXT_GENERATION,
    )

    script = """
    Zhang total：60seconds，He Tong Zuo Fei！
    AP：Shu Zi Bu Hui Sa Huang，Kan time Chuo。
    ▲Xiao Chen Suo Ding Yun Duan Ri Zhi，Xiao Chen Heng in doorway Dang Zhu Chen Mo。
    ▲Chen Mo Shou Zhi Xuan Zai delete confirm Jian。
    ▲Chen Mo phone Tong Zhi Lan Tiao Chu“Gai Wan Gei Ni20Wan”。
    ▲Chen Mo phone Dan Chu20Wan Dao Zhang Duan Xin，Xia Yi Tiao Xie：Nv Er Zhu Yuan Fei Wo Chu，not Zuo Jiu Cai Ni。
    ▲APYuan Shi file、Yun Duan Ri Zhi time Chuo、recording、Hui Yi Ji Yao and Duan Xin Bing Pai Tou Ping。
    Zhang total：15seconds。
    ▲APphone Dan Chu Ni Ming Duan Xin：Yuan Shi file Jiang in30seconds after delete，Xia Yi Ge Ting Zhi is Ni。
    """

    result = await score_service.score_script(
        script_content=script,
        story={"title": "APQuan Lian Lu return Yang Pian"},
        episode={"episode_number": 1, "title": "data Mi Ju"},
    )

    assert result.verdict == "pass"
    assert result.overall_score == 4.5
    assert result.dimension_scores.character_recognizability == 4.5
    assert result.dimension_scores.logic_coherence == 4.5
    assert result.risks == []
    assert result.rewrite_guidance == []


@pytest.mark.asyncio
async def test_score_script_does_not_calibrate_without_visible_motive_anchor(
    score_service, mock_ai_service
):
    mock_ai_service.ai_manager.generate_text.return_value = AIResponse(
        success=True,
        data="""
        ```json
        {
            "overall_score": 4.0,
            "dimension_scores": {
                "conflict_intensity": 4.0,
                "character_recognizability": 3.5,
                "cultural_fit": 4.5,
                "clip_ability": 4.0,
                "logic_coherence": 3.5
            },
            "verdict": "review",
            "strengths": [],
            "risks": ["character Dong Ji Bu Gou Ming Que"],
            "rewrite_guidance": ["Bu Qiang Chen Mo Dong Ji"],
            "suggested_ad_hooks": []
        }
        ```
        """,
        provider="mock",
        model="mock",
        task_type=AITaskType.SCRIPT_WRITING,
        model_type=AIModelType.TEXT_GENERATION,
    )

    script = """
    Zhang total：60seconds，He Tong Zuo Fei！
    AP：Shu Zi Bu Hui Sa Huang，Kan time Chuo。
    ▲Xiao Chen Suo Ding Yun Duan Ri Zhi，Xiao Chen Heng in doorway Dang Zhu Chen Mo。
    ▲Chen Mo Shou Zhi Xuan Zai delete confirm Jian。
    ▲APYuan Shi file、Yun Duan Ri Zhi time Chuo、recording、Hui Yi Ji Yao and Duan Xin Bing Pai Tou Ping。
    Zhang total：15seconds。
    ▲APphone Dan Chu Ni Ming Duan Xin：Yuan Shi file Jiang in30seconds after delete，Xia Yi Ge Ting Zhi is Ni。
    """

    result = await score_service.score_script(
        script_content=script,
        story={"title": "APQuan Lian Lu return Yang Pian"},
        episode={"episode_number": 1, "title": "data Mi Ju"},
    )

    assert result.verdict == "review"
    assert result.overall_score == 4.0
    assert result.dimension_scores.character_recognizability == 3.5
    assert result.risks == ["character Dong Ji Bu Gou Ming Que"]


def test_script_score_schema_is_provider_compatible():
    schema = _script_score_json_schema()
    schema_text = str(schema)

    assert "$defs" not in schema_text
    assert "allOf" not in schema_text
    assert schema["properties"]["dimension_scores"]["type"] == "object"
    assert "conflict_intensity" in schema["properties"]["dimension_scores"]["required"]
