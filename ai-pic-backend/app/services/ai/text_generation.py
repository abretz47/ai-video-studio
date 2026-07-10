from __future__ import annotations

import asyncio
from typing import Optional

import httpx
from app.core.config import settings
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


class TextGenerationMixin:
    async def _call_text_generation_service(
        self, prompt: str, task_type: str, *, story_format: Optional[str] = None
    ) -> Optional[str]:
        """call text Sheng Cheng service"""

        # Chang Shi Bu TongAIservice
        services = [
            self._generate_with_openai_gpt,
            self._generate_with_custom_service,
            self._generate_with_mock_service,  # Tian Jia mock service Zuo Wei Hou Bei
        ]

        for service in services:
            try:
                result = await service(prompt, task_type, story_format=story_format)
                if result:
                    return result
            except Exception as exc:
                print(f"服务 {service.__name__} 失败: {exc}")
                continue

        return None

    async def _generate_with_openai_gpt(
        self, prompt: str, task_type: str, *, story_format: Optional[str] = None
    ) -> Optional[str]:
        """Shi YongOpenAI GPTSheng Cheng text"""
        if not self.openai_api_key:
            return None
        base_url = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"

        try:
            if task_type == "story_novel":
                system_message = prompt_manager.render_prompt(
                    "system_prompt_novel_zhihu", {}
                )
            else:
                if task_type == "story_outline":
                    system_template = PromptTemplate.SYSTEM_PROMPT_STORY
                elif task_type in {"episode_generation", "script_generation"}:
                    system_template = PromptTemplate.SYSTEM_PROMPT_SCRIPT
                else:
                    system_template = PromptTemplate.SYSTEM_PROMPT_STORY
                system_message = prompt_manager.render_prompt(
                    system_template.value,
                    {"story_format": story_format},
                )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_message,
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                    },
                    timeout=120.0,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"OpenAI GPT生成失败: {exc}")
            return None

    async def _generate_with_custom_service(
        self, prompt: str, task_type: str, *, story_format: Optional[str] = None
    ) -> Optional[str]:
        """Shi Yong Zi Ding Yi text Sheng Cheng service"""
        if not self.base_url or not self.api_key:
            return None

        payload = {
            "prompt": prompt,
            "task_type": task_type,
            "parameters": {"temperature": 0.7, "format": "json"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate-text",
                    json=payload,
                    headers=headers,
                    timeout=120.0,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("text")
        except Exception as exc:
            print(f"自定义文本生成服务失败: {exc}")
            return None

    async def _generate_with_mock_service(
        self, prompt: str, task_type: str, *, story_format: Optional[str] = None
    ) -> Optional[str]:
        """mockAIservice(Yong Yu Ce Shi and Yan Shi)"""
        await asyncio.sleep(1)  # mock process time

        if task_type == "story_outline":
            return """{
 "premise": "Zhe Shi a Guan Yu You Qing and Cheng Zhang Xian Dai Du Shi story.",
 "synopsis": "Zhu Ren Gong Men in Mian Lin Sheng Huo Tiao Zhan when, through Xiang Hu Zhi Chi and Li Jie, Zui Zhong Shi Xian Ge Ren Cheng Zhang and You Yi Sheng Hua.story through Ri Chang Sheng Huo in Xiao Shi Jian, Zhan Xian Xian Dai Nian Qing Ren Sheng Huo Tai Du and Jia Zhi Guan.",
 "main_conflict": "Zhu Ren Gong Mian Lin Zhi Ye Xuan Ze and Ren Ji Guan Xi Shuang Chong Kun Rao, need in Li Xiang and Xian Shi Zhi Jian Zhao Dao Ping Heng.",
 "resolution": "through Peng You Men Bang Zhu and Zi Wo Fan Si, Zhu Ren Gong Zhao Dao Shi He Zi Ji Dao Lu, Tong Shi Jia Shen and Peng You Men You Yi.",
                "character_relationships": {
 "protagonist_friend": "Shen Hou You Yi, Xiang Hu Zhi Chi",
 "group_dynamics": "Tuan Jie Hu Zhu You Hao Guan Xi"
                },
                "main_characters": [
                    {
 "name": "Zhu Ren GongA",
                        "role": "protagonist",
 "description": "Ji Ji Xiang Shang Nian Qing Ren"
                    },
                    {
 "name": "Zhu Ren GongB",
                        "role": "supporting",
 "description": "Zhi Hui Ke Kao Peng You"
                    }
                ]
            }"""
        if task_type == "episode_generation":
            return """{
                "episodes": [
                    {
                        "episode_number": 1,
 "title": "Xin Kai Shi",
 "summary": "Jie ShaoMain characterand background setting",
                        "plot_points": [
 {"description": "角色出场", "timing": "开场"},
 {"description": "背景介绍", "timing": "前10分钟"},
 {"description": "冲突铺垫", "timing": "中段"}
                        ],
 "character_arcs": {"protagonist": "初始状态展示"},
                        "conflicts": [
 {"description": "内心困扰的初步展现", "intensity": "low"}
                        ],
                        "scene_count": 5
                    }
                ]
            }"""
        if task_type == "script_generation":
            return """{
 "content": "FADE IN:\\n\\nINT. Ke Ting - day\\n\\nZhu Ren Gong Zuo Zai Sha Fa on, thoughtful Zhe Shen Me...\\n\\nZhu Ren Gong\\n(Zi Yan Zi Yu)\\nJin Tian You Shi Xin Yi Tian Ne.\\n\\nFADE OUT.",
                "scenes": [
 {"scene_number": 1, "location": "客厅", "time": "日", "description": "主人公独自思考"}
                ],
                "dialogues": [
 {"character": "主人公", "content": "今天又是新的一天呢.", "emotion": "thoughtful"}
                ],
 "stage_directions": ["Zhu Ren Gong Zuo Zai Sha Fa on, thoughtful Zhe Shen Me"]
            }"""

        return "Zhe Shi a mockAISheng Cheng content, Yong Yu Ce Shi and Yan Shi Mu Di."
