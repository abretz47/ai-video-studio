from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional


class EpisodeMockMixin:
    async def _generate_mock_episodes(
        self, story: Dict[str, Any], episode_count: int, episode_duration: Optional[int]
    ) -> Dict[str, Any]:
        """生成模拟剧集内容"""
        await asyncio.sleep(1)  # 模拟处理时间

        episodes = []
        story_title = story.get("title", "Untitled Story")

        for i in range(episode_count):
            episode_num = i + 1
            episodes.append(
                {
                    "episode_number": episode_num,
                    "title": f"Episode {episode_num}" if episode_num > 1 else "Opening Chapter",
                    "summary": f"This is the episode summary for {story_title} Episode {episode_num}. This episode continues to advance the story and showcase character development.",
                    "plot_points": [
                        {"description": f"Episode {episode_num} opening plot", "timing": "opening"},
                        {"description": f"Episode {episode_num} development plot", "timing": "midpoint"},
                        {"description": f"Episode {episode_num} closing plot", "timing": "ending"},
                    ],
                    "character_arcs": {"protagonist": f"Episode {episode_num} character development"},
                    "conflicts": [
                        {
                            "description": f"Episode {episode_num} main conflict",
                            "intensity": "medium",
                        }
                    ],
                    "scene_count": 4 + (episode_num % 3),  # 4-6 scenes
                    "scenes": [
                        {
                            "scene_number": 1,
                            "slug_line": f"INT. MAIN LOCATION {episode_num} - DAY",
                            "location": "main location",
                            "time_of_day": "day",
                            "summary": "Opening setup, presenting the episode conflict or goal",
                        },
                        {
                            "scene_number": 2,
                            "slug_line": f"EXT. DEVELOPMENT SCENE {episode_num} - DUSK",
                            "location": "secondary location",
                            "time_of_day": "dusk",
                            "summary": "Advancing conflicts or relationships, deepening character motivations",
                        },
                    ],
                }
            )

        content = json.dumps({"episodes": episodes}, ensure_ascii=False, indent=2)

        return {
            "content": content,
            "prompt": "Mock episode generation prompt",
            "generation_method": "mock_service",
            "template_used": "mock_template",
            "provider_used": "mock",
            "model_used": "mock_model",
            "usage": {},
        }
