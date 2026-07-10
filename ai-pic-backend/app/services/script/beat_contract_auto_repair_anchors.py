from __future__ import annotations

from typing import Any

from app.services.script.beat_contract_auto_repair_common import (
    compact,
    has_any,
    preferred_character,
)


def needs_workplace_anchors(scenes: list[Any]) -> bool:
    text = compact(str(scenes))
    return has_any(
        text, ("contract", "customer", "Bing Gou", "Jin Diao", "Zhang Zong", "Chen Mo", "Xiao Chen")
    ) and has_any(text, ("Cuan Gai", "time Chuo", "log", "Original file", "Tou Ying"))


def apply_workplace_anchors(
    scene: dict[str, Any], beats: list[dict[str, Any]], index: int, count: int
) -> None:
    protagonist = preferred_character(beats) or "AP"
    if "AP" in protagonist or "Hui Gui" in protagonist:
        protagonist = "AP"
    if index == 0:
        data = [
            ("hook", "Zhang Zong phone countdown Cong60seconds Tiao to59seconds, Tou Ying Bing Gou data Hong Kuang Biao Chu, andAPShou LiOriginal fileCha E300Wan.", ("Zhang Zong", "60seconds, contract Zuo Fei!"), (protagonist, "Shu Zi Bu Hui Sa Huang.")),
            ("reveal", "APOriginal file, cloud log time Chuo Bing Pai Tou to screen, Cha E Hong Kuang Quan Chu.", (protagonist, "Kan time Chuo."), ("Xiao Chen", "backup Hai in.")),
            ("conflict", "Xiao Chen lock cloud log, Chen Mo Shou Zhi Xuan Zai delete Que Ren Jian, Zhang Zong countdown Tiao to45seconds.", ("Xiao Chen", "log Yi Suo."), ("Chen Mo", "Xian Guan Tou Ying!")),
        ]
    elif index == 1:
        data = [
            ("conflict", "Chen Mo Tu Ran QiangAPphone, Tong Zhi Lan Lu Chu Gai Wan Gei you20Wan, delete Que Ren Kuang Ting in Hong Se An Niu on.", ("Chen Mo", "phone Gei I."), (protagonist, "delete Jian Bie Peng.")),
            ("reveal", "Xiao Chen Suo Zhu log Tou Ping, Chen Mo Zuo Wan23:41Zhang Hao Ji Lu Hong Kuang Tao Zhu.", ("Xiao Chen", "Zhang Hao Shi Chen Mo."), (protagonist, "recording Ye in.")),
            ("payoff", "Chen Mo phone Tong Zhi Lan Tiao Chu"Gai Wan Gei you20Wan", Zhang Zong Ting Zhi Che Dan Dian Hua.", ("Zhang Zong", "15seconds."), ("Chen Mo", "I Bi.")),
        ]
    elif index == count - 1:
        data = [
            ("setup", "Hui Yi Shi Gang An Jing, Tou Ying onOriginal fileID Tu Ran Shan Hong.", (protagonist, "Bie Guan Tou Ying."), ("Xiao Chen", "file in Bian.")),
            ("conflict", "Ni Ming Zhang Hao Kai Shi Yuan Cheng deleteOriginal file, Jin Du Tiao Cong1%Tiao to7%.", ("Xiao Chen", "Hai You Yuan Cheng permission."), (protagonist, "Xian Bao Yuan Jian.")),
            ("cliffhanger", "APphone Dan Chu Ni Ming text message: Original filein30 secondsafter delete, below a Ting Zhi Shi you.", (protagonist, "Zhe Zhi Shi Di Yi Ceng."), (protagonist, "Ding Zhu countdown.")),
        ]
    else:
        data = [
            ("reveal", "Chen Mo phone Dan Chu20Wan Dao Zhang text message and Nv Er Zhu Yuan Fei threat.", ("Chen Mo", "Ta Men Bi I."), (protagonist, "Shui Gei Qian?")),
            ("conflict", "Xiao Chen Chen Mo Zhang Hao, Shou Kuan text message and delete time Pai Cheng San Lie.", ("Xiao Chen", "San Lie all Dui on."), (protagonist, "time Xian complete.")),
            ("reveal", "APrecording Bo Xing Zan Ting in Chen Mo Di Sheng Gai data Ju Zi on.", (protagonist, "recording Dui on."), ("Chen Mo", "I Zhi Shi Zhuan Fa.")),
        ]
    for beat, item in zip(beats[:3], data):
        _set_beat(beat, *item, protagonist=protagonist)


def _set_beat(
    beat: dict[str, Any],
    beat_type: str,
    visible: str,
    first_line: tuple[str, str],
    second_line: tuple[str, str],
    *,
    protagonist: str,
) -> None:
    beat["beat_type"] = beat_type
    beat["visible_event"] = visible
    beat["dramatic_purpose"] = f"{visible}迫使客户和团队在屏幕前确认证据。"
    beat["action_lines"] = [
        {
            "content": f"{protagonist}把原始文件推到投影前，屏幕证据被镜头推近。",
            "timing": "mid",
            "type": "action",
        }
    ]
    beat["dialogue_lines"] = [
        {"character": first_line[0], "content": first_line[1]},
        {"character": second_line[0], "content": second_line[1]},
    ]
    if beat_type == "payoff":
        beat["payoff_tag"] = "Client signs to continue the project"
    if beat_type == "cliffhanger":
        beat["cliffhanger_tag"] = "Ni Ming text message threat deleteOriginal file"
