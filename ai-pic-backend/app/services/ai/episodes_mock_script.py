from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from app.services.ai.script_text import build_script_text


class EpisodeMockScriptMixin:
    def _extract_dialogues_from_summary(
        self,
        summary: str,
        scene_number: int,
        fallback_characters: List[str],
    ) -> List[Dict[str, Any]]:
        """Cong scene summary in extract character dialogue.

 support Liang Zhong dialogue format: 
 1. directly format: Lao Guai: 'Cheng Zhu, Wo Men Kuai Dao.'
 2. Xu Shu format: A Gai Er Qing Sheng Shuo: "Ta Xiang Huo, I Bian Yu Ta Yi Dian angry."

 Ru Guo unable to extract to dialogue, return Kong list.
        """
        from app.services.script_missing_parts import (
            extract_dialogues_from_scene_summary,
        )

        return extract_dialogues_from_scene_summary(
            summary,
            scene_number,
            character_names=fallback_characters,
        )

    async def _generate_mock_script(
        self,
        episode: Dict[str, Any],
        story: Dict[str, Any],
        format_type: str,
        language: str,
        dialogue_style: str,
        scene_detail_level: str,
        template_style: str = "commercial_vertical_drama",
        target_chars_per_episode: int = 1300,
        quality_threshold: float = 9.0,
        additional_requirements: Optional[str] = None,
        style_preferences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Sheng Cheng mock script content, Bao Zheng none Wai Bu model when fallback Ti Yan.

 Zhu Yi: Ci Fang Fa will Chang Shi Cong scene summary in extract Zhen Shi dialogue, 
 Er Bu Shi Sheng Cheng Jia Miao Shu Xing dialogue.Ru Guo unable to extract, return Kong dialogue list.
        """
        await asyncio.sleep(1)

        # priority Shi Yong Sheng Cheng scene, keep and episode Yi Zhi; Fou Ze Tui Hui plot_points
        base_scenes = episode.get("scenes") or []
        plot_points = episode.get("plot_points") or []
        if not base_scenes and not plot_points:
            summary = (
                episode.get("summary")
                or story.get("synopsis")
                or "character in Ben Ji Zhong advance plot."
            )
            plot_points = [{"description": summary, "timing": "Zhong Duan"}]

        focus_characters: List[str] = []
        for char in story.get("main_characters") or []:
            name = char.get("name")
            if name and name not in focus_characters:
                focus_characters.append(name)
        focus_characters = focus_characters[:3]

        scenes: List[Dict[str, Any]] = []
        dialogues: List[Dict[str, Any]] = []
        stage_directions: List[Dict[str, Any]] = []
        script_sections: List[str] = [f"# {episode.get('title', 'Wei Ming Ming episode')}"]

        default_locations = ["Jiao Shi", "Xiao Yuan Hua Yuan", "Tu Shu Guan", "Cao Chang"]
        default_times = ["DAY", "EVENING", "NIGHT"]

        # Ruo You Zhen Shi scene, An scene Sheng Cheng; Fou Ze Shi Yong Qing Jie Dian Sheng Cheng
        if base_scenes:
            iterable = list(base_scenes)
        else:
            iterable = plot_points

        for idx, item in enumerate(iterable, start=1):
            if base_scenes:
                location = (
                    item.get("location")
                    or item.get("place")
                    or default_locations[(idx - 1) % len(default_locations)]
                )
                time_of_day = (
                    item.get("time_of_day")
                    or item.get("time")
                    or default_times[(idx - 1) % len(default_times)]
                )
                slug_line = item.get("slug_line") or f"INT. {location} - {time_of_day}"
                description = (
                    item.get("summary") or item.get("description") or f"场景 {idx}"
                )
                story_beat = item.get("story_beat") or item.get("timing") or "beat"
            else:
                location = default_locations[(idx - 1) % len(default_locations)]
                time_of_day = default_times[(idx - 1) % len(default_times)]
                slug_line = f"INT. {location.upper()} - {time_of_day}"
                description = item.get("description") or f"故事在第{idx}个阶段推进。"
                story_beat = item.get("timing") or "beat"

            scenes.append(
                {
                    "scene_number": idx,
                    "slug_line": slug_line,
                    "summary": description,
                    "description": description,
                    "focus_characters": focus_characters,
                    "story_beat": story_beat,
                    "location": location,
                    "time_of_day": time_of_day,
                }
            )

            # Cong scene summary in extract Zhen Shi dialogue, Er Bu Shi Sheng Cheng Jia Miao Shu Xing dialogue
            extracted_dialogues = self._extract_dialogues_from_summary(
                description, idx, focus_characters
            )
            dialogues.extend(extracted_dialogues)

            stage_directions.append(
                {
                    "scene_number": idx,
                    "content": f"镜头捕捉角色与场景，突出：{description}",
                    "camera_suggestion": "medium shot",
                    "lighting": "Zi Ran Guang",
                }
            )

            section_lines = [
                f"场景 {idx}: {location} - {time_of_day}",
                description,
                "",
            ]
            for dialog in [d for d in dialogues if d["scene_number"] == idx]:
                line_text = dialog.get("content") or dialog.get("line") or ""
                section_lines.append(f"{dialog.get('character', 'narration')}: {line_text}")
            script_sections.append("\n".join(section_lines))

        if additional_requirements:
            script_sections.append(f"\n【制作要求】{additional_requirements}")

        if template_style == "commercial_vertical_drama":
            script_text = build_script_text(
                scenes,
                dialogues,
                stage_directions,
                format_type=format_type,
                language=language,
                episode_number=episode.get("episode_number"),
                template_style=template_style,
                target_chars_per_episode=target_chars_per_episode,
                title=episode.get("title"),
            )
        else:
            script_text = "\n\n".join(script_sections)

        return {
            "content": {
                "content": script_text,
                "scenes": scenes,
                "dialogues": dialogues,
                "stage_directions": stage_directions,
                "metadata": {
                    "story_title": story.get("title"),
                    "episode_title": episode.get("title"),
                    "generator": "mock_script",
                    "language": language,
                    "format_type": format_type,
                    "scene_detail_level": scene_detail_level,
                    "template_style": template_style,
                    "target_chars_per_episode": target_chars_per_episode,
                    "quality_threshold": quality_threshold,
                    "style_preferences": style_preferences or [],
                },
            },
            "prompt": "mock scriptGeneration prompt",
            "generation_method": "mock_service",
            "template_used": "mock_script_template",
            "provider_used": "mock",
            "model_used": "mock_script_model",
            "usage": {},
        }
