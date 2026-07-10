from __future__ import annotations

from typing import Any

LOW_VALUE_CHARACTERS = {"recording", "text message", "narration"}


def has_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def compact(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())


def visible_len(text: str) -> int:
    return len(compact(text))


def to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def scene_role(index: int, count: int) -> str:
    return "hook" if index == 1 else "cliffhanger" if index == count else "escalation"


def preferred_character(beats: list[dict[str, Any]]) -> str | None:
    counts: dict[str, int] = {}
    for beat in beats:
        for line in beat.get("dialogue_lines") or []:
            character = (
                str(line.get("character") or "").strip()
                if isinstance(line, dict)
                else ""
            )
            if character and character not in LOW_VALUE_CHARACTERS:
                counts[character] = counts.get(character, 0) + 1
    ap_name = next((name for name in counts if "AP" in name or "Hui Gui" in name), None)
    return ap_name or (max(counts, key=counts.get) if counts else None)


def progression_event(protagonist: str, order: int) -> str:
    return (
        f"{protagonist}将原始文件放到投影左侧，屏幕标红被改数字。",
        f"{protagonist}指向会议纪要时间戳，助理调出修改日志。",
        "customer in Tou Ying before Ting Zhu action, Cuan Gai Zhe Di Tou An Mie phone screen.",
        "phone recording Bo Xing Tiao Dong, Cuan Gai Zhe Di Sheng Cheng Ren Cong Yin Xiang Chuan Chu.",
    )[(order - 1) % 4]


def progression_action(protagonist: str, order: int) -> str:
    return (
        f"{protagonist}把两份数据页并排推到客户面前。",
        "Zhu Li Xiu Gai log Chuang Kou Tuo to Tou Ying Zhong Yang.",
        "customer Na Qi Bi in Wen Ti Shu Zi Pang Hua Quan.",
        "Cuan Gai Zhe Hou Tui Ban Bu, phone Tong Zhi Lan Lu Chu delete Ti Xing.",
    )[(order - 1) % 4]


def progression_dialogue(order: int) -> str:
    return ("Kan time Chuo.", "original Ye in Zhe.", "log Neng Dui on.", "Bie Shan file.")[
        (order - 1) % 4
    ]


def beat_screen_text(beat: dict[str, Any]) -> str:
    return "".join(
        str(action.get("content") or "")
        for action in beat.get("action_lines", [])
        if isinstance(action, dict)
    )


def beat_text(beat: dict[str, Any]) -> str:
    return compact(str(beat.get("visible_event") or "") + beat_screen_text(beat))


def scene_screen_text(beats: list[dict[str, Any]]) -> str:
    return compact(
        "".join(str(beat.get("visible_event") or "") + beat_screen_text(beat) for beat in beats)
    )
