"""Character Background Generator.

Uses AI to generate personality, background, and appearance descriptions
for temporary characters based on their dialogues and script context.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.script.temporary_character_extractor import TemporaryCharacterInfo


async def generate_character_background(
    *,
    character_info: TemporaryCharacterInfo,
    scene_context: Dict[str, Any],
    ai_service: Optional[Any] = None,
) -> Dict[str, str]:
    """Generate character background using AI analysis of dialogues and context.

    Args:
        character_info: Extracted character information from script
        scene_context: Scene context (e.g., setting, time, location)
        ai_service: Optional AI service instance for generation (if None, uses heuristics)

    Returns:
        Dictionary with:
        - personality: Character personality traits
        - background: Character background story
        - appearance_override: Physical appearance description
    """
    # Build AI prompt from character info
    prompt = _build_generation_prompt(character_info, scene_context)

    # Use AI service if available, otherwise fall back to heuristics
    if ai_service:
        result = await _generate_with_ai(prompt, ai_service)
    else:
        result = _generate_with_heuristics(character_info)

    return result


def _build_generation_prompt(
    character_info: TemporaryCharacterInfo,
    scene_context: Dict[str, Any],
) -> str:
    """Build AI prompt for character background generation.

    Args:
        character_info: Character information
        scene_context: Scene context

    Returns:
        Prompt string for AI generation
    """
    # Format dialogues
    dialogues_text = "\n".join(
        [f'"{dlg}"' for dlg in character_info.dialogues[:5]]  # Limit to first 5
    )

    # Format appearance hints
    appearance_hints_text = ", ".join(character_info.appearance_hints)

    # Format scene context
    setting = scene_context.get("setting_location", "")
    time_period = scene_context.get("setting_time", "")

    prompt = f"""Qing Gen Ju Yi Xia Xin Xi generate Lin Shi character De Xiang Xi Bei Jing Zi Liao：

character name Cheng：{character_info.character_name}

Chu Chang scene：Di{character_info.first_appearance_scene}scene Dao Di{character_info.last_appearance_scene}scene
dialogue Zong Shu：{character_info.dialogue_count}Ju

character dialogue Shi Li：
{dialogues_text}

Wai Guan Xian Suo：{appearance_hints_text or "none"}

scene She Ding：
- Di Dian：{setting}
- Shi Dai：{time_period}

Qing generate Yi Xia San Ge Fang Mian De Miao Shu：

1. Xing Ge Te Dian（personality）：
   - Ji Yu dialogue Fen Xi character De Xing Ge Te Zheng
   - 2-3Ge Guan Jian Ci，Yong Dou Hao Fen Ge
   - Shi Li："Re Qing、Zhuan Ye、Ren Zhen Fu Ze"

2. character Bei Jing（background）：
   - 1-2Ju Hua Miao Shu character De Shen Fen He Bei Jing
   - Jie He scene She Ding He character name Cheng
   - Shi Li："Kuai Di Gong Si Yuan Gong，Fu Ze Ben Xiao Qu De Pei Song Gong Zuo，Dui She Qu Huan Jing Hen Shu Xi"

3. Wai Guan Miao Shu（appearance_override）：
   - 1-2Ju Hua Miao Shu character De Wai Guan Te Zheng
   - Jie He Wai Guan Xian Suo He Zhi Ye Te Dian
   - Shi Li："Chuan Zhe Kuai Di Zhi Fu，Bei Zhe Kuai Di Bao，Kan Qi Lai Nian Qing You Huo Li"

Qing YiJSONformat Fan Hui：
{{
  "personality": "...",
  "background": "...",
  "appearance_override": "..."
}}
"""
    return prompt


async def _generate_with_ai(
    prompt: str,
    ai_service: Any,
) -> Dict[str, str]:
    """Generate character background using AI service.

    Args:
        prompt: Generation prompt
        ai_service: AI service instance

    Returns:
        Dictionary with personality, background, appearance_override
    """
    try:
        # Call AI service
        response = await ai_service.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500,
        )

        # Parse JSON response
        import json

        if hasattr(response, "content"):
            result = json.loads(response.content)
        elif isinstance(response, dict):
            result = response
        else:
            result = json.loads(str(response))

        # Validate required fields
        return {
            "personality": result.get("personality", ""),
            "background": result.get("background", ""),
            "appearance_override": result.get("appearance_override", ""),
        }

    except Exception as e:
        # Log error and fall back to heuristics
        import logging

        logging.warning(f"AI generation failed: {e}, falling back to heuristics")
        return _generate_with_heuristics_from_prompt(prompt)


def _generate_with_heuristics(
    character_info: TemporaryCharacterInfo,
) -> Dict[str, str]:
    """Generate character background using heuristic rules.

    Args:
        character_info: Character information

    Returns:
        Dictionary with personality, background, appearance_override
    """
    char_name = character_info.character_name

    # Infer role type from name
    role_hints = {
        "Kuai Di Yuan": {
            "personality": "Re Qing, responsible for, has Nai Xin",
            "background": "Kuai Di Gong Si Yuan Gong, responsible for Pei Song Gong Zuo",
            "appearance": "Chuan Zhe Kuai Di Zhi Fu, Bei Zhe Kuai Di Bao",
        },
        "Yi Sheng": {
            "personality": "professional, calm, Xi Xin",
            "background": "Yi Liao Gong Zuo Zhe, responsible for Zhen Liao Gong Zuo",
            "appearance": "Chuan Zhe Bai Da Gua, Dai Zhe Ting Zhen Qi",
        },
        "Hu Shi": {
            "personality": "Wen Rou, Ti Tie, Ren Zhen",
            "background": "Yi Liao Hu Li Gong Zuo Zhe, Xie Zhu Yi Sheng Gong Zuo",
            "appearance": "Chuan Zhe Hu Shi Zhi Fu, Dai Zhe Hu Shi Mao",
        },
        "Jing Cha": {
            "personality": "Yan Su, Zheng Yi, Guo Duan",
            "background": "Zhi Fa Ren Yuan, Wei Hu Zhi An Gong Zuo",
            "appearance": "Chuan Zhe Jing Fu, Pei Dai Jing Hui",
        },
        "Fu Wu Yuan": {
            "personality": "Re Qing, Li Mao, Zhou Dao",
            "background": "Fu Wu Hang Ye Cong Ye Zhe, responsible for Jie Dai Gong Zuo",
            "appearance": "Chuan Zhe Gong Zuo Fu, Mian Dai Wei Xiao",
        },
        "Si Ji": {
            "personality": "Wen Zhong, Shu Lian, responsible for",
            "background": "Jia Shi Gong Zuo Zhe, responsible for Yun Shu Gong Zuo",
            "appearance": "Chuan Zhe Gong Zuo Fu or Bian Zhuang",
        },
    }

    # Try exact match
    if char_name in role_hints:
        hints = role_hints[char_name]
        return {
            "personality": hints["personality"],
            "background": hints["background"],
            "appearance_override": hints["appearance"],
        }

    # Try partial match
    for key, hints in role_hints.items():
        if key in char_name or char_name in key:
            return {
                "personality": hints["personality"],
                "background": hints["background"],
                "appearance_override": hints["appearance"],
            }

    # Use appearance hints if available
    appearance = ", ".join(character_info.appearance_hints)
    if not appearance:
        appearance = f"{char_name}De Wai Guan Te Zheng"

    # Generic fallback
    return {
        "personality": "Pu Tong, You Hao, Li Mao",
        "background": f"{char_name}，Zai Ju Qing Zhong Ban Yan Lin Shi character",
        "appearance_override": appearance,
    }


def _generate_with_heuristics_from_prompt(prompt: str) -> Dict[str, str]:
    """Generate character background from prompt when AI fails.

    Args:
        prompt: Original generation prompt

    Returns:
        Dictionary with personality, background, appearance_override
    """
    # Extract character name from prompt
    import re

    name_match = re.search(r"character name: (.+)", prompt)
    char_name = name_match.group(1).strip() if name_match else "temporary character"

    # Extract appearance hints
    appearance_match = re.search(r"Wai Guan clue: (.+)", prompt)
    appearance = (
        appearance_match.group(1).strip()
        if appearance_match
        else f"{char_name}De Wai Guan Te Zheng"
    )

    # Generic fallback
    return {
        "personality": "You Hao, professional, Ren Zhen",
        "background": f"{char_name}，Zai Ju Qing Zhong Ban Yan Lin Shi character",
        "appearance_override": appearance,
    }
