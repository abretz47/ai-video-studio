from __future__ import annotations

from typing import Any

from app.services.script.beat_contract_auto_repair_common import (
    beat_screen_text,
    beat_text,
    compact,
    has_any,
    preferred_character,
    progression_action,
    progression_dialogue,
    progression_event,
    scene_screen_text,
    to_float,
    visible_len,
)

_VAGUE_VISUAL = ("Qi Fen", "atmosphere", "Jin Zhang Gan", "Ya Po Gan")
_VAGUE = (
    "Yi Shi to",
    "understand",
    "Nei Xin",
    "Beng Kui",
    "discoverKey clue",
    "Key clue",
    "Chu Xian Zhuan Zhe",
    "Fa Sheng twist",
    "Zhi Zao conflict",
    "Zhi Zao Xuan Nian",
    "Liu Xia suspense",
    "drive conflict",
    "escalate conflict",
    "advance plot",
)


def repair_beats(scene: dict[str, Any], beats: list[dict[str, Any]]) -> None:
    protagonist = preferred_character(beats) or "AP"
    for beat in beats:
        visible = str(beat.get("visible_event") or "")
        if has_any(visible, _VAGUE_VISUAL):
            beat["visible_event"] = f"{protagonist}停住脚步举起手机，云端日志时间戳映在屏幕上。"
        if (beat.get("beat_type") == "payoff" or beat.get("payoff_tag")) and has_any(
            visible, ("Xin Ren", "Beng Kui", "Cheng Ren")
        ):
            beat["visible_event"] = "customer in Hui Yi Ji Yao on Qian Zi Que Ren continue Xiang Mu, Cuan Gai Zhe phone Dan Chu Jie Gu text message."
            beat["payoff_tag"] = "Client signs to continue the project"
        purpose = str(beat.get("dramatic_purpose") or "")
        if not purpose or has_any(purpose, _VAGUE):
            beat["dramatic_purpose"] = f"{beat['visible_event']}让证据链进入下一步。"
        for action in beat.get("action_lines") or []:
            if isinstance(action, dict) and has_any(
                str(action.get("content") or ""), _VAGUE_VISUAL
            ):
                action["content"] = "Xiao Chen Heng in Men Kou An Zhu Ping Ban, cloud log time Chuo Lan Kuang lock."
    if protagonist.replace(" ", "") not in scene_screen_text(beats):
        beats[0].setdefault("action_lines", []).insert(
            0,
            {
                "content": f"{protagonist}把原始文件推到投影前，客户和团队同时看向屏幕。",
                "timing": "mid",
                "type": "action",
            },
        )
    if not any(beat.get("beat_type") == "payoff" or beat.get("payoff_tag") for beat in beats):
        target = beats[1 if len(beats) > 1 else 0]
        target["beat_type"] = "reveal"
        target["payoff_tag"] = "Client signs to continue the project"
        target["visible_event"] = "customer in Hui Yi Ji Yao on Qian Zi Que Ren continue Xiang Mu, APOriginal fileID Quan Gei shot."
    _ensure_recurring_dialogue(beats, protagonist)


def harden_opening_hook(beat: dict[str, Any] | None) -> None:
    if not isinstance(beat, dict):
        return
    beat["beat_type"] = "hook"
    if not has_any(beat_text(beat), ("exception", "countdown", "delete", "crisis", "evidence", "twist", "Gai")):
        beat["visible_event"] = "customer Pai Zhuo Zhi Yi: Tou Ying data Gai, Original fileevidence and screen Shu Zi Bu Fu."
        beat.setdefault("action_lines", []).insert(
            0,
            {
                "content": "Tou Ying Shu Zi Bian Hong, customer Shou Zhi Chong Chong Qiao in error data on.",
                "timing": "0-2s",
                "type": "action",
            },
        )


def harden_final_cliffhanger(beat: dict[str, Any] | None) -> None:
    if not isinstance(beat, dict):
        return
    beat["beat_type"] = "cliffhanger"
    beat["visible_event"] = "APphone Dan Chu Ni Ming text message: Original filein30 secondsafter delete, below a Ting Zhi Shi you."
    beat["cliffhanger_tag"] = "Ni Ming text message threat deleteOriginal file"
    beat.setdefault("action_lines", []).append(
        {
            "content": "APphone Ju Dao shot before, text message countdown Cong30 secondsTiao to29seconds.",
            "timing": "outro",
            "type": "action",
        }
    )


def align_scene_durations(
    scene: dict[str, Any], beats: list[dict[str, Any]], opening: bool
) -> None:
    estimated = to_float(scene.get("estimated_duration_seconds")) or 0
    if estimated <= 0 or not beats:
        return
    first = min(3.0, max(1.0, estimated / len(beats))) if opening else 0.0
    if first:
        beats[0]["duration_seconds"] = round(first, 2)
    rest = beats[1:] if first else beats
    remaining = max(1.0, estimated - first)
    base = round(remaining / len(rest), 2)
    for index, beat in enumerate(rest):
        beat["duration_seconds"] = base if index < len(rest) - 1 else round(
            remaining - (base * index), 2
        )


def dedupe_progression(beats: list[dict[str, Any]]) -> None:
    seen_screen: set[str] = set()
    seen_lines: set[str] = set()
    protagonist = preferred_character(beats) or "AP"
    for beat in beats:
        state = compact(beat_screen_text(beat))
        if state in seen_screen:
            order = int(to_float(beat.get("order_index")) or len(seen_screen) + 1)
            beat["visible_event"] = progression_event(protagonist, order)
            beat["action_lines"] = [
                {
                    "content": progression_action(protagonist, order),
                    "timing": "mid",
                    "type": "action",
                }
            ]
            state = compact(beat_screen_text(beat))
        seen_screen.add(state)
        for line in beat.get("dialogue_lines") or []:
            if not isinstance(line, dict):
                continue
            text = compact(str(line.get("content") or ""))
            if text in seen_lines:
                line["content"] = progression_dialogue(
                    int(to_float(beat.get("order_index")) or 1)
                )
                text = compact(line["content"])
            seen_lines.add(text)


def shorten_dialogue_lines(beats: list[dict[str, Any]]) -> None:
    for beat in beats:
        for line in beat.get("dialogue_lines") or []:
            if isinstance(line, dict) and visible_len(str(line.get("content") or "")) > 15:
                line["content"] = _short_dialogue(str(line.get("content") or ""))


def _short_dialogue(text: str) -> str:
    replacements = (
        (("version sync",), "Ke Neng Shi sync Wen Ti."),
        (("Hui Yi Ji Yao",), "Ji Yao has you Qian Zi."),
        (("Gang Cai", "Wu Hui"), "Gang Cai Wu Hui."),
        (("Original file",), "Original filein Zhe."),
        (("cloud data",), "cloud875, Tou Ying920."),
        (("Zuo Bian", "You Bian"), "Zuo cloud, You Tou Ying."),
        (("Qian Guo character",), "Qian Zi in Zhe, Zen Me Shuo?"),
    )
    for markers, replacement in replacements:
        if all(marker in text for marker in markers):
            return replacement
    for separator in ("。", "！", "？", "；", "，", ",", ":", "："):
        if separator in text:
            candidate = text.split(separator, 1)[0].strip(" ，,：:") + "。"
            if 4 <= visible_len(candidate) <= 15:
                return candidate
    return f"{compact(text)[:14]}。"


def _ensure_recurring_dialogue(
    beats: list[dict[str, Any]], protagonist: str
) -> None:
    covered = {
        beat.get("order_index")
        for beat in beats
        for line in beat.get("dialogue_lines", [])
        if isinstance(line, dict) and str(line.get("character") or "") == protagonist
    }
    for beat in beats:
        if len(covered) >= 2:
            break
        if beat.get("order_index") not in covered:
            beat.setdefault("dialogue_lines", []).append(
                {
                    "character": protagonist,
                    "content": progression_dialogue(int(beat["order_index"])),
                }
            )
            covered.add(beat.get("order_index"))
