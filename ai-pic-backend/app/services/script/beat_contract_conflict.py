from __future__ import annotations

from typing import Any

from app.services.script.beat_contract_specificity import is_specific_text

_STAKES_MARKERS = (
    "seconds",
    "minutes",
    "Xiao Shi",
    "countdown",
    "Qing Ling",
    "Gui Ling",
    "Diu Shi",
    "delete",
    "Yong Jiu",
    "Jiang Jin",
    "contract",
    "customer",
    "Yan Shou",
    "Fa Bu",
    "Shang Xian",
    "evidence",
    "file",
    "log",
    "permission",
    "Zi Chan",
    "video",
    "audio",
    "Ding Dan",
    "bill",
    "Kou Kuan",
    "Pei Chang",
    "Yu E",
    "Bao Jing",
    "alarm",
    "Ting Ji",
    "Feng Jin",
    "lock",
)

_OPPOSITION_MARKERS = (
    "system",
    "permission",
    "shadow",
    "customer",
    "Dui You",
    "Gong Ying Shang",
    "background",
    "Shen He",
    "log",
    "Kong Zhi Tai",
    "countdown",
    "alarm",
    "Suo",
    "Ju Jue",
    "delete",
    "Cuan Gai",
    "Feng Jin",
    "screen",
    "file",
    "API",
    "Hui Diao",
    "bill",
    "model",
    "Zi Chan",
    "Lao Ban",
    "Shen Pian Yuan",
    "interior Gui",
)


def conflict_issues(scene: Any) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    conflict = scene.conflict

    if not conflict.question.strip() or not is_specific_text(conflict.question):
        issues.append(
            {
                "check_id": "scene_conflict_question",
                "message": "scene conflict must name a concrete dramatic question",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {"question": conflict.question},
            }
        )

    if not conflict.stakes.strip() or not conflict.opposition.strip():
        issues.append(
            {
                "check_id": "scene_conflict",
                "message": "scene conflict must name stakes and opposition",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {
                    "stakes": conflict.stakes,
                    "opposition": conflict.opposition,
                },
            }
        )
    elif not is_specific_text(conflict.stakes) or not is_specific_text(
        conflict.opposition
    ):
        issues.append(
            {
                "check_id": "scene_conflict_specificity",
                "message": "scene conflict must include concrete stakes and opposition",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {
                    "stakes": conflict.stakes,
                    "opposition": conflict.opposition,
                },
            }
        )

    if conflict.stakes.strip() and not _has_marker(conflict.stakes, _STAKES_MARKERS):
        issues.append(
            {
                "check_id": "scene_conflict_stakes",
                "message": "scene stakes must name a concrete loss or deadline",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {"stakes": conflict.stakes},
            }
        )
    if conflict.opposition.strip() and not _has_marker(
        conflict.opposition, _OPPOSITION_MARKERS
    ):
        issues.append(
            {
                "check_id": "scene_conflict_opposition",
                "message": "scene opposition must name a concrete blocking source",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {"opposition": conflict.opposition},
            }
        )

    turn = conflict.turn or ""
    if not turn.strip() or not is_specific_text(turn):
        issues.append(
            {
                "check_id": "scene_conflict_turn",
                "message": "scene conflict must name a concrete turn",
                "scene_number": scene.scene_number,
                "beat_order_index": None,
                "evidence": {"turn": conflict.turn},
            }
        )

    return issues


def _has_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)
