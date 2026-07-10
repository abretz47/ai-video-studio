from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def build_hook_schedule(
    story: Dict[str, Any],
    episode: Dict[str, Any],
    marketing_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the production hook schedule contract for script generation."""

    marketing = _merge_non_empty(story, episode, marketing_overrides or {})
    hook_plan = _safe_dict(marketing.get("hook_plan"))
    opening_hook = (
        hook_plan.get("opening_hook")
        or _first_non_empty(episode.get("summary"), story.get("main_conflict"))
        or "Kai Chang directly Pao Chu Ben Ji core conflict or Shen Fen/evidence Bao Dian"
    )
    payoff = (
        hook_plan.get("payoff_plan")
        or _first_non_empty(episode.get("payoff"), story.get("resolution"))
        or "Zhu Jue Bi Xu Ying to a specific Shou Huo, Bing Yong can Pai action Dui Xian Shuang Dian"
    )
    cliffhanger = _first_from_list(marketing.get("cliffhanger_plan")) or (
        "Jie Wei Liu Xia Geng Da crisis or Wei Jie truth, not Zuo Wan Quan Shou Shu"
    )

    conflict_ladder: List[Dict[str, Any]] = []
    for idx, point in enumerate(_as_list(episode.get("plot_points"))[:5], start=1):
        if isinstance(point, dict):
            desc = (
                point.get("description") or point.get("summary") or point.get("title")
            )
            timing = point.get("timing")
        else:
            desc = str(point)
            timing = None
        if desc:
            conflict_ladder.append(
                {"sequence": idx, "description": str(desc), "timing": timing}
            )

    if not conflict_ladder:
        summary = _first_non_empty(episode.get("summary"), story.get("synopsis"))
        if summary:
            conflict_ladder.append(
                {"sequence": 1, "description": str(summary), "timing": "Zhong Duan"}
            )

    ad_candidate_beats = []
    for idx, snippet in enumerate(_as_list(marketing.get("ad_snippets"))[:5], start=1):
        if not isinstance(snippet, dict):
            continue
        hook = snippet.get("hook") or snippet.get("key_line")
        if not hook:
            continue
        ad_candidate_beats.append(
            {
                "sequence": idx,
                "duration_seconds": snippet.get("duration_seconds"),
                "hook": hook,
                "visual_summary": snippet.get("visual_summary")
                or snippet.get("visual_hook"),
                "call_to_action": snippet.get("call_to_action")
                or snippet.get("cliff_or_cta"),
            }
        )

    return {
        "opening_hook": opening_hook,
        "conflict_ladder": conflict_ladder,
        "payoff": payoff,
        "cliffhanger": cliffhanger,
        "twist_density": marketing.get("twist_density"),
        "market_region": marketing.get("market_region"),
        "micro_genre": marketing.get("micro_genre"),
        "ad_candidate_beats": ad_candidate_beats,
    }


def render_production_requirements(
    *,
    base_additional_requirements: Optional[str],
    hook_schedule: Dict[str, Any],
    rewrite_guidance: List[str],
    attempt_no: int,
) -> str:
    sections: List[str] = []
    if base_additional_requirements:
        sections.append(str(base_additional_requirements).strip())
    sections.append(
        "## production Ji script Lian Lu requirement\n"
        "Yan Ge Zun Shou Yi Xia hook_schedule.script Bi Xu opening_hook, conflict_ladder, "
        "payoff, cliffhanger Xie Cheng can Pai action, Duan dialogue and clear scene Shi Jian.\n"
        f"{json.dumps(hook_schedule, ensure_ascii=False, indent=2)}"
    )
    sections.append(_commercial_score_contract())
    if attempt_no > 1 and rewrite_guidance:
        sections.append(
            "## automatic Fan Xiu requirement\n"
            "on Yi Ban ScriptScore Wei Da Biao, Qing in Bao Liu character and Ji Ben Yin Guo Qian Ti below Zhong Xie: \n"
            + "\n".join(f"- {item}" for item in rewrite_guidance if item)
            + "\n\n"
            + _rewrite_closure_contract(rewrite_guidance)
        )
    return "\n\n".join(section for section in sections if section.strip())


def _commercial_score_contract() -> str:
    return (
        "## Shang Ye Ping Fen Ying Jiao Fu Qing Dan\n"
        "Ben Lun Sheng Cheng Bi Xu Neng directly through ScriptScore: overall_score >= 4.5, "
        "conflict_intensity / character_recognizability / cultural_fit / "
        "clip_ability/logic_coherence Mei Xiang >= 4.2.Bu Yao only in note Li Cheng Nuo, "
        "Bi Xu Luo Dao body text, scene summary, structured_script_contract.beats, "
        "dialogue_lines and action_lines.\n"
        "- character Bian Shi Du: Zhu Jue Mei Chang Zhi Shao 2 Ci Ju Ming Chu Chang, 1 Ge Wen Ding Xing Wei tag, "
        "1 Ju can Fu Yong Duan dialogue; Pei Jue/Fan Pai Bi Xu Xie Qing Ke Jian Dong Ji and Dang Chang Xuan Ze, "
        'Do not write only "assistant/tamperer/team member" without any actionable identifying tag.\n'
        "- Luo Ji Yi Zhi Xing: Mei Ge Zhi Kong Bi Xu has Ke Jian evidence Lian: Xin Xi Lai Yuan -> Xian Chang validation -> "
        "customer/contract/permission/file Hou Guo; recording, log, text message, contract, Original fileDi Yi Ci Chu Xian when"
        "Bi Xu Xie Qing Shi Shui Na Chu, Cong Na Li Lai, screen on Chu Xian Shen Me.\n"
        "- Xian Yi Ren/Fan Pai Dong Ji: cannot Zhu Jue Yi Wen Jiu Cheng Ren; Bi Xu first Kang Ju, Shi Tu Li Kai, "
        "delete file or Shuai Guo, and through Zhuan Zhang Ji Lu, Shang Ji text message, Ji Xiao threat, Zhai Wu or contract Li Yi"
        "Lu Chu specific Dong Ji.\n"
        "- Supporting and secondary characters need clear action tags rather than vague placeholders, such as blocking a suspect, pulling up cloud logs, locking a delete timestamp, or warning the protagonist about a countdown.\n"
        "- Corridor or office confrontations need external pressure, such as a client countdown, a contract about to expire, a file being deleted, a blocked exit, or a permission window about to close; evidence cannot appear by coincidence.\n"
        '- Every named supporting role should be explicitly named and used consistently; do not use generic labels like "customer", "assistant", or "tamperer" without identification.\n'
        '- Workplace data and contract stories should use high-intensity beats: a 60-second cancellation countdown, locked cloud logs, a phone grab, file deletion, or a threat message that reveals motive; the protagonist should also get reusable lines such as "Numbers do not lie, check the timestamp."\n'
        '- The second scene must keep ad-clip intensity: finger hovering over delete confirmation, someone blocking the exit, a 15-second phone countdown, or a cancel-delete button; the motive must also appear on screen through concrete messages such as "Finish it and I will give you 200,000."\n'
        "- Su Cai can Jian Xing: body text Bi Xu Nei Zhi 15s, 30s, 60s San Lei Tou Liu Pian Duan, "
        "Mei Lei all Yao has first frame action, key line, Jie Guo change and cliffhanger/CTA; "
        "Mei 60 seconds Zhi Shao 2 Ge line+frame Shuang Gou Zi.\n"
        "- conflict Qiang Du: 0-3 seconds directly Bao Wai Bu Sun Shi or threat; Mei Chang all Yao Xin Zeng Zu Li, "
        "Dai Jia or countdown, cannot only Chong Fu Ju file, Kan screen, Jie Shi Wu Hui.\n"
        "- Wen Hua Shi Pei: Yong contract, customer, permission, evidence, Ze Ren Lian advance conflict, "
        "avoid Gong Ju Shi dialogue and Min Gan can Fu Zhi Wei Gui Xi Jie."
    )


def _rewrite_closure_contract(rewrite_guidance: List[str]) -> str:
    actionable = [str(item).strip() for item in rewrite_guidance if str(item).strip()]
    checklist = "\n".join(
        f"{idx}. Zhen Dui「{item}」：Bi Xu Xin Zeng Huo Gai Xie at least 1 Ge visible_event、"
        "1 Ge action_line, 1 Ju Duan dialogue and 1 Ge Wai Bu Hou Guo; cannot Zhi Gai narration or note."
        for idx, item in enumerate(actionable[:8], start=1)
    )
    return (
        "## Fan Xiu Luo Di Jiao Yan\n"
        "Sheng Cheng Qian Xian Zhu Tiao Xiao Chu on Yi Ban Feng Xian; Sheng Cheng Jie Guo Li Bi Xu Neng Kan Dao Yi Xia change: \n"
        f"{checklist}\n"
        "Ru Guo on Yi Ban Zhi Chu character Bian Shi Ruo, Guo Du Ping, Dong Ji insufficient, Luo Ji Tiao Yue or Su Cai insufficient, "
        "Ben Ban Bi Xu Xin Zeng Ju Ming character action, evidence Lai Yuan shot, customer Tai Du change shot, Yi Ji"
        "15s/30s/60s Ke Jian Pian Duan, not Yun Xu Fu Yong on Yi Ban Tong Yi Zu action Jie Zou."
    )


def _merge_non_empty(*sources: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if value not in (None, "", [], {}):
                merged[key] = value
    return merged


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _first_from_list(value: Any) -> Optional[str]:
    for item in _as_list(value):
        if item not in (None, "", [], {}):
            return str(item)
    return None


def _first_non_empty(*values: Any) -> Optional[str]:
    for value in values:
        if value not in (None, "", [], {}):
            return str(value)
    return None
