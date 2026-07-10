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
                    "title": f"Di{episode_num}Ji" if episode_num > 1 else "Chu Shi Pian Zhang",
                    "summary": f"Zhe Shi{story_title}Di{episode_num}Ji De Nei Rong Gai Yao。Ben Ji Jiang Ji Xu Tui Jin story Fa Zhan，Zhan Xian character Cheng Zhang。",
                    "plot_points": [
                        {"description": f"Di{episode_num}Ji Kai Chang Qing Jie", "timing": "Kai Chang"},
                        {"description": f"Di{episode_num}Ji Fa Zhan Qing Jie", "timing": "Zhong Duan"},
                        {"description": f"Di{episode_num}Ji Jie Wei Qing Jie", "timing": "Jie Wei"},
                    ],
                    "character_arcs": {"protagonist": f"Di{episode_num}Ji De character Fa Zhan"},
                    "conflicts": [
                        {
                            "description": f"Di{episode_num}Ji De Zhu Yao Chong Tu",
                            "intensity": "medium",
                        }
                    ],
                    "scene_count": 4 + (episode_num % 3),  # 4-6Ge scene
                    "scenes": [
                        {
                            "scene_number": 1,
                            "slug_line": f"INT. Zhu Yao scene {episode_num} - DAY",
                            "location": "Zhu Yao Di Dian",
                            "time_of_day": "day",
                            "summary": "Kai ChangForeshadowing, Cheng Xian Ben Ji conflict or target",
                        },
                        {
                            "scene_number": 2,
                            "slug_line": f"EXT. Fa Zhan scene {episode_num} - DUSK",
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
