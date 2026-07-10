import re
from typing import Any, Dict

from app.utils.json_utils import extract_json_block

CHINESE_KEY_MAP = {
    "story Qian Ti": "premise",
    "Qian Ti": "premise",
    "detailed outline": "synopsis",
    "story outline": "synopsis",
    "Geng Gai": "synopsis",
    "Main conflict": "main_conflict",
    "conflict": "main_conflict",
    "Jie Jue Fang An": "resolution",
    "Jie Ju": "resolution",
    "character relationship": "character_relationships",
    "Zhu Jue Xin Xi": "main_characters",
    "Main character": "main_characters",
}

_OUTLINE_KEYS = {
    "premise",
    "synopsis",
    "main_conflict",
    "resolution",
    "character_relationships",
    "main_characters",
}


def normalize_story_json_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
 Bao Han Zhong Wen Jian Ming story Gai NianJSONYing She to Biao Zhun Jian: 
    premise, synopsis, main_conflict, resolution, character_relationships, main_characters
 Qi Ta Jian Bao Liu Yuan Yang, Bian Yu Cun Ru extra_metadata.
    """
    if not isinstance(data, dict):
        return {}

    normalized: Dict[str, Any] = dict(data)

    # Ying She Zhong Wen Jian
    for zh_key, std_key in CHINESE_KEY_MAP.items():
        if zh_key in data and std_key not in normalized:
            normalized[std_key] = data.get(zh_key)

    return normalized


def extract_story_outline_payload(data: Any) -> Dict[str, Any]:
    """
 Cong Ren Yi JSON structure in Jin Liang Chou Qu Bao Han story outline Zi Duan dict.

 Bu Fen model/Dai Li Ke Neng will Jie Guo Bao Guo in `data`/`story_outline`/`result` Deng character Duan Li, 
 directly Yong Ding Ceng dict write comfortably will Dao Zhi premise/synopsis Deng character Duan as Kong.
    """
    if isinstance(data, dict):
        if _OUTLINE_KEYS.intersection(data.keys()) or set(CHINESE_KEY_MAP).intersection(
            data.keys()
        ):
            return normalize_story_json_keys(data)

        # Chang Jian Bao Guo: Zhi You a key Qie Zhi as dict/list
        if len(data) == 1:
            only_value = next(iter(data.values()))
            extracted = extract_story_outline_payload(only_value)
            if extracted:
                return extracted

        # Di Gui in Zi Jie Gou in Xun Zhao Di Yi Fen available payload
        for value in data.values():
            extracted = extract_story_outline_payload(value)
            if extracted:
                return extracted
        return {}

    if isinstance(data, list):
        for item in data:
            extracted = extract_story_outline_payload(item)
            if extracted:
                return extracted
        return {}

    return {}


def extract_outline_from_text(text: str) -> Dict[str, Any]:
    """
 Cong Zi You text in Chou Qu story outline Guan Jian Zi Duan(Qi Fa Shi).
 support Shi Bie Lei Si: 
 "story Qian Ti:...", "detailed outline:...", "Main conflict:...", "Jie Jue Fang An:...", "character relationship:..." Deng Duan Luo.
    """
    fields = {
        "premise": None,
        "synopsis": None,
        "main_conflict": None,
        "resolution": None,
        "character_relationships": None,
        "main_characters": None,
    }

    # Yi Chang Jian title Zuo Fen Duan
    sections = {
        "premise": [r"story Qian Ti", r"Qian Ti"],
        "synopsis": [r"detailed outline", r"story outline", r"Geng Gai"],
        "main_conflict": [r"Main conflict", r"conflict"],
        "resolution": [r"Jie Jue Fang An", r"Jie Ju"],
        "character_relationships": [r"character relationship"],
        "main_characters": [r"Zhu Jue Xin Xi", r"Main character"],
    }

    # Gou Zao Zheng Ze, Zhao Chu Mei Ge Duan Luo
    for key, titles in sections.items():
        pattern = re.compile(
            r"(?:^|\n)\s*(?:"
            + "|".join(titles)
            + r")[：:]\s*(.+?)(?=\n\s*(?:"
            + "|".join(sum(sections.values(), []))
            + r")[：:]|\Z)",
            re.S,
        )
        m = pattern.search(text)
        if m:
            fields[key] = m.group(1).strip()

    # if synopsis Reng Wei Kong, Yong Quan Wen fallback
    if not fields["synopsis"]:
        fields["synopsis"] = text.strip()

    return fields
