from __future__ import annotations

from typing import Any, Dict, List

from app.services.script_score_thresholds import (
    PASS_DIMENSION_THRESHOLD,
    PASS_OVERALL_THRESHOLD,
)

_DIMENSION_REWRITE_GUIDANCE = {
    "conflict_intensity": (
        "conflict Qiang Du need reach Jing Pin Xian: Mei Chang all Jia Ru Xin Wai Bu Dai Jia or Zu Li, "
        "Kai Chang3seconds Bao Dian, Zhong Duan Fan Sha, Jie Wei crisis escalate Bi Xu can Pai."
    ),
    "character_recognizability": (
        "character Bian Shi Du need reach Jing Pin Xian: Zhu Jue Mei Chang Zhi Shao has a Wen Ding Xing Wei tag, "
        "Yi Ju can Shi Bie Duan dialogue, Fan Pai/Pei Jue Bi Xu has Qing Chu Dong Ji."
    ),
    "cultural_fit": (
        "Wen Hua Shi Pei need reach Jing Pin Xian: Jian Shao Han Hun or He Gui Feng Xian Biao Da, "
        "Yong Zhi Chang contract, customer, evidence, permission and Ze Ren Lian drive conflict."
    ),
    "clip_ability": (
        "Su Cai can Jian Xing need reach Jing Pin Xian: Mei60seconds Zhi Shao Liang Ge line+frame Shuang Gou Zi, "
        "clear15s/30s/60sKe Jian Pian Duan first frame action, key line and cliffhanger."
    ),
    "logic_coherence": (
        "Luo Ji Yi Zhi Xing need reach Jing Pin Xian: Bu Qi evidence Lai Yuan, recording/Ji Yao/log Qu De path, "
        "character Shou Ci Huo Zhi Xin Xi frame Yi Ju, Yi Ji customer Tai Du Zhuan Bian Ke Jian evidence."
    ),
}


def extract_rewrite_guidance(scoring: Dict[str, Any]) -> List[str]:
    script_score = _safe_dict(scoring.get("script_score"))
    guidance = script_score.get("rewrite_guidance")
    items = (
        [str(item).strip() for item in guidance if str(item).strip()]
        if isinstance(guidance, list)
        else []
    )

    overall = _score_overall(scoring)
    if overall and overall < PASS_OVERALL_THRESHOLD:
        items.append(
            f"Zheng Ti ScriptScore Bi Xu Ti Sheng Dao {PASS_OVERALL_THRESHOLD:.1f}+；"
            "Bu Yao only Wei Diao Yu Qi, need increase can Pai twist, clear Shou Huo and Geng Qiang Ka Dian."
        )

    dims = _safe_dict(script_score.get("dimension_scores"))
    for key, guidance_text in _DIMENSION_REWRITE_GUIDANCE.items():
        value = dims.get(key)
        if not _below_dimension_threshold(value):
            continue
        score_text = _format_score(value)
        items.append(
            f"{guidance_text} Dang Qian {key}={score_text}，Xu >= {PASS_DIMENSION_THRESHOLD:.1f}。"
        )

    _append_risk_guidance(items, script_score)
    _append_asset_guidance(items, scoring)
    return _dedupe_strings(items)


def _append_risk_guidance(items: List[str], script_score: Dict[str, Any]) -> None:
    risks = script_score.get("risks")
    if not isinstance(risks, list):
        return
    for risk in risks[:3]:
        text = str(risk).strip()
        if text:
            items.append(f"Xiu Fu Ping Fen Feng Xian：{text}")


def _append_asset_guidance(items: List[str], scoring: Dict[str, Any]) -> None:
    asset_tags = _safe_dict(scoring.get("asset_tags"))
    asset_count = asset_tags.get("asset_count")
    durations = asset_tags.get("durations")
    if not isinstance(asset_count, (int, float)) or asset_count < 3:
        items.append("Tou Liu Su Cai insufficient: Bi Xu Nei Zhi Zhi Shao 15s, 30s, 60s San Lei Ke Jian Gao Neng Duan Luo.")
    elif isinstance(durations, list) and not {15, 30, 60}.issubset(
        {int(item) for item in durations if _looks_numeric(item)}
    ):
        items.append("Tou Liu duration Fu Gai insufficient: Bu Qi 15s, 30s, 60s Gou Zi, Fan Sha and cliffhanger Pian Duan.")


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _score_overall(scoring: Dict[str, Any]) -> float:
    value = _safe_dict(scoring.get("script_score")).get("overall_score")
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _below_dimension_threshold(value: Any) -> bool:
    try:
        return float(value) < PASS_DIMENSION_THRESHOLD
    except (TypeError, ValueError):
        return True


def _format_score(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "Que Shi"


def _looks_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _dedupe_strings(items: List[str]) -> List[str]:
    result: List[str] = []
    seen: set[str] = set()
    for item in items:
        text = item.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result
