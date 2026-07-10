"""
Helper utilities for Virtual IP AI generation.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def generate_template_content(name: str, basic_info: Optional[str]) -> Dict[str, Any]:
    """Sheng Cheng template content(DangAInot allowed Yong Shi Shi Yong)"""
    return {
        "description": (
            f"{name}拥有鲜明的个性与清晰的形象定位。"
            f"{basic_info or 'Wai Biao and Qi Zhi Zi Qia, Yan Xing You Ji Ke Xun, Shi He Fa Zhan as Chang Qi Xu Shi character.'}"
        ),
        "background_story": (
            f"在一个充满无限可能的世界里，{name}的故事开始了。\n\n"
            f"{basic_info or 'TaCheng Zhang Jing Li and key Xuan Ze, Su Zao Dang Xia Xing Ge and Chu Shi Fang Shi.'}\n\n"
            f"每一次出现，{name}都会为观众带来新的惊喜和感动。"
            "Zhe Bu Jin Jin Shi a character, Geng Shi a Chong Man Sheng Ming Li Xu Shi core."
        ),
        "biography": (
            f"**角色档案：{name}**\n\n"
            f"**外貌特征**：{name}拥有令人印象深刻的外貌，每一个细节都经过精心设计。\n\n"
            "**Xing Ge Te Dian**: Xing Ge Xian Ming, Ji You Qin He Li You has Du Te Ge Ren Mei Li.\n\n"
            "**Xing Qu Ai Hao**: Re Ai Sheng Huo, Dui Shi Jie Chong Man Hao Qi Xin.\n\n"
            "**Te Chang Ji Neng**: in Zi Ji Ling Yu You Zhe Chu Se Biao Xian.\n\n"
            f"**背景经历**：{basic_info or 'Yong You Feng Fu Ren Sheng Jing Li, Su Zao Xian Zai Ge Xing.'}\n\n"
            "Zhe Shi a Zhi De Shen Ru Liao Jie and Xi Ai character."
        ),
        "tags": [],
    }


def sanitize_character_text(text: str, *, name: str) -> str:
    """Jin Liang Yi Chu model output in not Fu He Yue Shu Yuan Xu Shu Ci(for example"Xu NiIP/Xu Ni character")."""
    if not text:
        return ""
    cleaned = str(text)
    for token in [
        "Xu NiIP",
        "Xu Ni character",
        "Xu Ni character",
        "Xu Ni Ren",
        "IPcharacter",
        "Xu Ni ip",
        "virtual ip",
        "virtual character",
    ]:
        cleaned = cleaned.replace(token, "")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = cleaned.replace(" ，", "，").replace(" 。", "。").replace(" ；", "；")
    return cleaned.strip()


def generate_template_style_prompt(
    name: str, description: str, image_category: str
) -> str:
    """Sheng Cheng template style prompt Ci(Zhong Wen)"""
    base_prompt = "High qualityEr Ci Yuan character"

    if "girl" in description.lower() or "Nv" in description:
        base_prompt = "High qualityEr Ci Yuan Nv Hai"
    elif "boy" in description.lower() or "Nan" in description:
        base_prompt = "High qualityEr Ci Yuan Nan Hai"

    category_modifiers = {
        "portrait": "Ban Shen Xiao Xiang, Mian Bu Xi Jie Qing Xi",
        "full_body": "Quan Shen Xiang, Zhan Zi complete",
        "scene": "character and scene Rong He, environment background",
        "action": "Dong Tai Zi Shi, action scene",
        "emotion": "Biao Qing Feng Fu, EmotionBiao Da",
    }

    modifier = category_modifiers.get(image_category, "Ban Shen Xiao Xiang, Xi Jie Qing Xi")

    return f"{base_prompt}，{modifier}，细节丰富，清晰聚焦"


def build_biography_from_profile(profile: Dict[str, Any]) -> str:
    """Gen Ju virtual_ip_creation Ge Zi Duan Pin Jie Cheng Yi Duan character Xiao Zhuan."""
    sections: List[str] = []
    mapping = [
        ("Xing Ge Te Zheng", "personality"),
        ("Ji Neng Te Chang", "skills"),
        ("Ren Ji Guan Xi", "relationships"),
        ("Sheng Huo Fang Shi", "lifestyle"),
        ("Biao Zhi Xing Te Zheng", "signature_traits"),
        ("Fa Zhan Qian Li", "development_potential"),
    ]
    for title, key in mapping:
        value = profile.get(key)
        if not value:
            continue
        sections.append(f"**{title}**：{value}")
    text = "\n\n".join(sections).strip()
    if not text:
        return ""
    return text


def build_content_from_profile(
    profile: Dict[str, Any], *, name: str, basic_info: Optional[str]
) -> Dict[str, Any]:
    """Map a generated profile into the virtual IP content fields."""
    description = (
        profile.get("detailed_description")
        or profile.get("description")
        or profile.get("summary")
    )
    background_story = profile.get("background_story")
    biography = build_biography_from_profile(profile)
    tags = normalize_suggested_tags(
        profile.get("suggested_tags") or profile.get("tags")
    )

    if not (description and background_story and biography):
        template = generate_template_content(name, basic_info)
        description = description or template["description"]
        background_story = background_story or template["background_story"]
        biography = biography or template["biography"]
        if not tags:
            tags = template.get("tags", [])

    return {
        "description": sanitize_character_text(description, name=name),
        "background_story": sanitize_character_text(background_story, name=name),
        "biography": sanitize_character_text(biography, name=name),
        "tags": tags,
    }


def normalize_suggested_tags(raw: Any) -> List[str]:
    """Normalize suggested tags from AI profile output."""
    if not raw:
        return []
    if isinstance(raw, str):
        items = re.split(r"[,，、;/\n]+", raw)
    elif isinstance(raw, (list, tuple)):
        items = []
        for item in raw:
            if isinstance(item, str):
                items.append(item)
    else:
        return []

    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        tag = item.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        result.append(tag)
        if len(result) >= 10:
            break
    return result
