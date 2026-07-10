from __future__ import annotations

from typing import Any

from app.services.script.beat_contract_auto_repair_common import compact, has_any

_CONCRETE_OPPOSITION = (
    "system",
    "customer",
    "log",
    "countdown",
    "Suo",
    "delete",
    "Cuan Gai",
    "screen",
    "file",
    "API",
    "bill",
    "Lao Ban",
    "Shen Pian Yuan",
    "interior Gui",
)
_VAGUE = (
    "Yi Shi to",
    "understand",
    "Nei Xin",
    "Beng Kui",
    "discoverKey clue",
    "Key clue",
    "conflict eruption",
    "data not Yi Zhi discover",
    "Chu Xian Zhuan Zhe",
    "Fa Sheng twist",
    "Xin Ren Beng Kui",
    "Jin Zhang Gan",
    "Qian Zai crisis",
    "Zhi Zao conflict",
    "Zhi Zao Xuan Nian",
    "Liu Xia suspense",
    "drive conflict",
    "escalate conflict",
    "advance plot",
)
_ABSTRACT_OPPOSITION = ("Mu Hou Hei Shou", "Shen Mi Li Liang", "unknown Shi Li", "Shen Mi Ren", "Ni Ming threat", "Beng Kui")
_THIN_OPPOSITION = {"Cuan Gai Zhe", "Nei Bu Cuan Gai Zhe", "interior Gui", "Tong Shi", "Tuan Dui Cheng Yuan"}


def repair_scene_conflict(scene: dict[str, Any]) -> None:
    conflict = scene.setdefault("conflict", {})
    if not isinstance(conflict, dict):
        conflict = {}
        scene["conflict"] = conflict
    conflict.setdefault("question", scene.get("summary") or "APRu He He Shi data Cuan Gai?")
    stakes = str(conflict.get("stakes") or "")
    if has_any(stakes, _VAGUE) or not has_any(
        stakes, ("seconds", "contract", "customer", "evidence", "file", "Pei Chang")
    ):
        conflict["stakes"] = "if not Cheng Qing, 300Wan Xiang Mu contract Dang Chang Zuo Fei, customer Zhong Zhi Qian Zi Yan Shou."
    opposition = str(conflict.get("opposition") or "")
    if (
        compact(opposition) in _THIN_OPPOSITION
        or has_any(opposition, _ABSTRACT_OPPOSITION)
        or not has_any(opposition, _CONCRETE_OPPOSITION)
    ):
        conflict["opposition"] = (
            "Li Ming phone Dan Chu Jie Gu text message, APphone Xian Shi30 secondscountdown, Original filedelete threat Zu Zhi He Shi."
        )
    turn = str(conflict.get("turn") or "")
    if not turn or has_any(turn, _VAGUE):
        conflict["turn"] = "APTou Ying Shu Zi, Original fileand Tuan Dui Fan Ying Dui Qi, lock Cuan Gai Lai Yuan."
