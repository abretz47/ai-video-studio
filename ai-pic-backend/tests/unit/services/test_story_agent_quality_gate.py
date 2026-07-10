from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest


def _weak_outline() -> dict:
    return {
        "premise": "Jin Rong Jing Ying Jian Wang Luo Xiao Shuo Jia Wen Wen Zao Yu Gou Xue Shi Jian。",
        "synopsis": "Wen Wen Shang Ban，Lin Wan Chu Xian，A-Fei Bang Zhu Ta，final Shi Qing Jie Shu。",
        "main_conflict": "Wen Wen Yu Dao Yi Xie Ma Fan。",
        "resolution": "Wen Wen Jie Jue Wen Ti。",
        "main_characters": [
            {"name": "Wen Wen", "description": "Jin Rong Bai Ling"},
            {"name": "Lin Wan", "description": "workplace Dui Shou"},
            {"name": "A-Fei", "description": "Hun Hun"},
        ],
        "plot_structure": {
            "act1": "Pu Tong start。",
            "act2": "Pu Tong Fa Zhan。",
            "act3": "Pu Tong Jie Shu。",
        },
        "hook_plan": {"opening_hook": "Pu Tong Yi Tian start。", "key_reversals": []},
        "selling_points": ["urban story"],
        "cliffhanger_plan": ["Xia Ji continue"],
        "ad_snippets": [
            {
                "duration_seconds": 15,
                "hook": "continue Guan Kan",
                "visual_summary": "character Liao Tian",
                "call_to_action": "continue Kan",
            }
        ],
    }


def _strong_outline() -> dict:
    return {
        "premise": "Wen Wen in company Nian Hui Tu Ran discover betrayal video be public，Bi Xu Dang Chang counterattack。",
        "synopsis": (
            "Tu Ran，Wen Wen in Nian Hui Xian Chang discover Tou Pai video be public，crisis and conflict Li Ke Bao Fa。"
            "Ta Ding Zhu Ya Li Fan Cha Zheng Ju，tense Dui Kang Bu Duan escalate，Zhong Duan reveal Lin Wan_Shuang Ju test_01300519Cai is real mastermind。"
            "Zui Zhong climax Dui Jue in truth Bao Guang，Wen Wen complete counterattack and Shou Shu Jie Ju。"
        ),
        "main_conflict": "Wen Wen Bi Xu in public Xiu Ru and workplace Xian Hai in Zhao Chu truth。",
        "resolution": "Wen Wen reveal truth，Jie Jue crisis and complete Ni Xi。",
        "main_characters": [
            {"name": "Wen Wen", "description": "Jin Rong Bai Ling"},
            {"name": "Lin Wan_Shuang Ju test_01300519", "description": "workplace Dui Shou"},
            {"name": "A-Fei", "description": "Hun Hun"},
        ],
        "plot_structure": {
            "act1": "Tu Ran Bao Chu Xiu Ru video，Wen Wen Bei Po Dang Chang counterattack。",
            "act2": "crisis escalate，Wen Wen and Lin Wan_Shuang Ju test_01300519Wei Rao Zheng Ju tense Dui Kang。",
            "act3": "climax reveal truth，Wen Wen Jie Jue crisis complete Ni Xi Jie Ju。",
        },
        "hook_plan": {
            "opening_hook": "Tu Ran，Wen Wen Tui Men discover betrayal video Zheng Zai Bo Fang。",
            "escalation_plan": "conflict Mei Yi Chang Dou escalate。",
            "payoff_plan": "Zui Zhong truth reveal and complete counterattack。",
            "key_reversals": [
                {
                    "beat_type": "hook",
                    "description": "Tou Pai video public",
                    "timing": "opening",
                    "intensity": "high",
                }
            ],
        },
        "selling_points": [
            "opening public Xiu Ru",
            "Gao Ya counterattack",
            "truth reveal",
            "workplace Ni Xi",
            "Qiang Ka Dian",
        ],
        "cliffhanger_plan": ["Dan Shi Ta discover Mu Hou mastermind Ling You Qi Ren"],
        "ad_snippets": [
            {
                "duration_seconds": 15,
                "hook": "betrayal video public",
                "visual_summary": "Nian Hui Da Ping public Zheng Ju",
                "call_to_action": "Kan Ta Ru He counterattack",
            }
        ],
    }


@pytest.mark.asyncio
async def test_story_agent_repairs_when_outline_fails_quality_or_character_gate():
    from app.services.story_agent import LANGGRAPH_AVAILABLE, StoryLangGraphAgent

    if not LANGGRAPH_AVAILABLE:
        pytest.skip("langgraph not available")

    calls: list[str] = []
    responses = [_weak_outline(), _strong_outline()]

    async def _generate_text(**kwargs: object):
        schema = kwargs.get("json_schema")
        name = schema.get("name") if isinstance(schema, dict) else ""
        calls.append(str(name))
        return SimpleNamespace(
            success=True,
            data=responses[len(calls) - 1],
            provider="deepseek",
            model="deepseek-v4-flash",
            usage={"total_tokens": 1},
        )

    service = SimpleNamespace(ai_manager=SimpleNamespace(generate_text=_generate_text))
    agent = StoryLangGraphAgent(service)

    with patch(
        "app.services.story_agent.prompt_manager.render_prompt", return_value="prompt"
    ):
        result = await agent.generate(
            title="Wo Sheng Huo be Gou Xue Bao Wei",
            story_format="short_drama",
            genre="drama",
            characters=[
                {"name": "Wen Wen", "description": "Jin Rong Bai Ling"},
                {"name": "Lin Wan_Shuang Ju test_01300519", "description": "workplace Dui Shou"},
                {"name": "A-Fei", "description": "Hun Hun"},
            ],
            market_region="KRJP",
            micro_genre="Xiao Yuan Ni Xi",
            pacing_template="twist-heavy",
            hook_plan={"opening_hook": "opening Zhi Jie Gei Chu conflict Jie Guo"},
            twist_density="2+/Ji",
            cliffhanger_plan=["Yong Wei Jie Kai Mi Mi Zuo Wei Xia Yi Ji Yin Zi"],
            ad_snippets=[],
            theme="Gou Xue",
            target_audience="Cheng Ren",
            duration_minutes=51,
            setting_time="modern",
            setting_location="Bei Jing",
            world_building=None,
            additional_requirements=None,
            style_preferences=[],
            content_restrictions=[],
            model="deepseek-v4-flash",
            prefer_provider="deepseek",
            temperature=0.7,
        )

    assert result is not None
    assert calls == ["story_outline", "story_outline_repair"]
    assert (
        result["normalized"]["main_characters"][1]["name"] == "Lin Wan_Shuang Ju test_01300519"
    )
    assert result["character_validation_passed"] is True
    assert result["story_quality_passed"] is True
    assert result["reasoning"] == [
        "draft_ok",
        "repair_attempt_1",
        "validated_attempt_1",
    ]
