from __future__ import annotations

import re
from dataclasses import dataclass

DIALOGUE_RE = re.compile(
    r"^([\u4e00-\u9fa5A-Za-z0-9·（）()VvOoSs\.\s，,、]{1,40})[：:]\s*(.+)$"
)
SCENE_HEADER_RE = re.compile(
    r"(^\[Di?\d+Chang\])|(^scene\s*\d+)|(^Scene\s*\d+)|(^INT\.|^EXT\.)|(^Di\d+Ji)|(^\d+[-－]\d+\s+(interior|exterior|interior/exterior|exterior/interior)\.)",
    re.I,
)
TAG_RE = re.compile(r"【([^】]+)】")


@dataclass(frozen=True)
class PhraseRule:
    phrase: str
    severity: str
    suggestion: str


# "not allowed Pai"/"not allowed directly Pai She"Chang Jian Biao Shu(only Dui Fei dialogue Xing Zuo prompt)
UNFILMABLE_PHRASES: list[PhraseRule] = [
    PhraseRule(
        "Ta Gan Dao", "error", "change to can Pai action: Di Tou, Shou Kou Yi Jiao, Hu Xi Ji Cu, Yan Kuang Fa Hong Deng."
    ),
    PhraseRule("Ta Gan Dao", "error", "change to can Pai action: Hou Tui Ban Bu, Shou Zhi Fa Dou, Qiang Cheng Wei Xiao Deng."),
    PhraseRule("Gan Dao", "warn", "avoid Xin Li Miao Xie, change to shot Ke Jian action/Biao Qing/environment change."),
    PhraseRule("Jue De", "warn", "avoid Zhu Guan determine, change to shot Ke Jian action/Wu Li Fan Kui."),
    PhraseRule("Qi Fen", "warn", "change to can Pai Xin Hao: Deng Guang Hu Mie, Feng Chui Dao Wu Ti, Yuan Chu Jing Di Deng."),
    PhraseRule("atmosphere", "warn", "change to can Pai Xin Hao: Guang Ying, environment Yin, Dao Ju change."),
    PhraseRule("relationship Po Lie", "error", "change to can Pai Gou Tu: Liang Ren Zuo You Liang Duan, Bei Dui Bei, Ju Jue Dui Shi Deng."),
    PhraseRule("Liang Ren relationship", "warn", "change to specific action and Kong Jian relationship, Bu Yao Chou Xiang description relationship."),
    PhraseRule("sad", "warn", "change to can Pai action: Yan Kuang Fa Hong, Tun Yan, Shou Zhi Kou Jin Deng."),
    PhraseRule("angry", "warn", "change to can Pai action: Yao Ya, Quan Tou Zuan Jin, Bei Zi Zhen Dong Deng."),
    PhraseRule("Ya Yi", "warn", "change to can Pai Xin Hao: Chen Men Di Pin Sheng, Deng Guang Shan Shuo, Kong Jian Bi Ze Gou Tu."),
]


TEMPO_TAGS = ("Kuai", "Man", "Jia Su Qu", "Jian Su Qu")
EMOTION_TAG_KEYWORDS = ("EmotionMu Di", "Emotiontarget")
SFX_TAG_KEYWORDS = ("sound effect", "atmosphere Yin", "environment Yin")
COMMERCIAL_ACTION_MARKERS = ("▲", "[close-up]", "[Te Xiao]", "[shot]", "Qie Zhi")

HOOK_MARKERS = (
    "[sound effect]",
    "(sound effect",
    "(sound effect",
    "▲",
    "Pa",
    "Peng",
    "Dong",
    "！",
    "?",
    "？",
    "Gui",
    "Xue",
    "Sha",
)

UNIMPLEMENTED_CHECKS = [
    "action Si Duan Shi(Qi Shi→Guo Cheng→Luo Dian/Wu Li Fan Kui→Fan Ying)",
    "Ping Xing Ren Wu(Dui Hua when Shou Shang Bi Xu You Shi Zuo)",
    "scene Ji Xing twist(The Turn)and San Chong Zhang Ai Di Zeng",
    "Di San Yan Yuan Dao Ju(through Wu Ti Chuan Di relationship)",
    "Tong Kuang Guo Du and Zhuan Chang Luo Ji tag(Sheng Yin/action/Pi Pei)",
]
