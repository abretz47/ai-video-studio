from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional


class EpisodeMockMixin:
    async def _generate_mock_episodes(
        self, story: Dict[str, Any], episode_count: int, episode_duration: Optional[int]
    ) -> Dict[str, Any]:
        """Sheng Cheng mock episode content"""
        await asyncio.sleep(1)  # mock process time

        episodes = []
        story_title = story.get("title", "Wei Ming Ming story")

        for i in range(episode_count):
            episode_num = i + 1
            episodes.append(
                {
                    "episode_number": episode_num,
                    "title": f"第{episode_num}集" if episode_num > 1 else "Chu Shi Pian Zhang",
                    "summary": f"这是{story_title}第{episode_num}集的内容概要。本集将继续推进故事发展，展现角色成长。",
                    "plot_points": [
                        {"description": f"第{episode_num}集开场情节", "timing": "Kai Chang"},
                        {"description": f"第{episode_num}集发展情节", "timing": "Zhong Duan"},
                        {"description": f"第{episode_num}集结尾情节", "timing": "Jie Wei"},
                    ],
                    "character_arcs": {"protagonist": f"第{episode_num}集的角色发展"},
                    "conflicts": [
                        {
                            "description": f"第{episode_num}集的主要冲突",
                            "intensity": "medium",
                        }
                    ],
                    "scene_count": 4 + (episode_num % 3),  # 4-6Ge scene
                    "scenes": [
                        {
                            "scene_number": 1,
                            "slug_line": f"INT. 主要场景 {episode_num} - DAY",
                            "location": "Zhu Yao Di Dian",
                            "time_of_day": "day",
                            "summary": "Kai ChangForeshadowing, Cheng Xian Ben Ji conflict or target",
                        },
                        {
                            "scene_number": 2,
                            "slug_line": f"EXT. 发展场景 {episode_num} - DUSK",
                            "location": "Ci Yao Di Dian",
                            "time_of_day": "dusk",
                            "summary": "advanceConflictor relationship, Jia Shen character Dong Ji",
                        },
                    ],
                }
            )

        content = json.dumps({"episodes": episodes}, ensure_ascii=False, indent=2)

        return {
            "content": content,
            "prompt": "mock episodeGeneration prompt",
            "generation_method": "mock_service",
            "template_used": "mock_template",
            "provider_used": "mock",
            "model_used": "mock_model",
            "usage": {},
        }
