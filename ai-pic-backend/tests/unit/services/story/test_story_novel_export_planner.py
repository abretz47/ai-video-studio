from unittest.mock import AsyncMock, patch

import pytest
from app.services.story.story_novel_export_planner import generate_zhihu_plan_compact


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_zhihu_plan_compact_falls_back_when_chapters_missing():
    story_payload = {
        "title": "Cheng Xu Yuan Zhi Wo Jia Diao Xia Lai Ge？Lin Mei？Qi Xian Nv？not！is Ge Guo Gai～～～～",
        "episodes": [
            {
                "episode_number": 1,
                "title": "Kai Duan",
                "summary": "protagonist in Jia Ban when Yu Dao Li Qi Shi Jian，Sheng Huo be Che Di Da Luan。",
                "plot_points": ["Guo Gai Cong Tian Er Jiang", "protagonist Jue Ding Zhui Cha Lai Yuan"],
            }
        ],
    }

    with patch(
        "app.services.story.story_novel_export_planner.generate_story_novel_text",
        new=AsyncMock(return_value="{}"),
    ):
        plan, chapters = await generate_zhihu_plan_compact(
            story_payload=story_payload,
            target_words=18000,
            chapter_total=3,
            model_id=None,
            prefer_provider=None,
            system_prompt="system",
        )

    assert isinstance(plan, dict)
    assert len(chapters) == 3
    assert [ch.get("chapter_number") for ch in chapters] == [1, 2, 3]
    assert all(ch.get("cliffhanger_hint") for ch in chapters)
