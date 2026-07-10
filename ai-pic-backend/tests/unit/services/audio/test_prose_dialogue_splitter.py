from app.services.audio.dialogue_processing.audio_dialogue_filter import (
    repair_scene_dialogues_for_audio,
    should_treat_dialogue_as_action_for_audio,
    split_audio_dialogues_and_action_blocks,
)
from app.services.audio.dialogue_processing.prose_dialogue_splitter import (
    sanitize_stage_directions_for_audio,
    split_prose_dialogue_block,
)


def test_split_prose_dialogue_block_extracts_quoted_dialogues_with_speakers() -> None:
    alias_to_canonical = {"Wen Wen": "Wen Wen", "Old Guai": "Old Guai"}
    text = (
        "Wen Wen Zhen Jing Di Hou Tui Ban Bu：“Ni……Ni Zen Me Zhi Dao Wo in Xie Xiao Shuo？Hai Zhi Dao Wo have Ping Jing？” "
        "Old Guai Zhi Zhi Ta Dian Nao：“Ni Si Ji before，screen Can Liu Jie Mian is Xie Zuo Ruan Jian Bian Ji Chuang Kou。"
        "Ling Wai，Wo Gang Cai in Tiao Shi Jiao Ben when，Jian Kong to Gong GongWi-Fion have Yi Ge Zhong Duan Chi Xu Xiang Yun Duan Tong Bu Yi Ge Da Xing Wen Dang，"
        "Dan Jin Yi Xiao Shi INT data Zeng Liang Ji Xiao。Zhe Shi Dian Xing content Chuang Zuo Zhe Yu Dao‘Ka Wen’when Wang Luo Xing Wei Mo Shi。” "
        "Wen Wen Lian Se Fa Bai，Dan“Ka Wen”Zhe Ge Ci Jing Zhun Chuo in Ta Tong Dian。Ta Qiang Zuo Zhen Ding：“Na You Zen Yang？"
        "Chuang Zuo Xu Yao Ling Gan，Xu Yao Qing Gan，Bu Shi Leng Bing Bing Shu Ju Fen Xi！” "
        "Old Guai：“Suo Yi Ni Hui Ka in Zhe Li。Xi Tong Hua Shu Li Ke Yi Jie Jue Zhe Ge issue。Ni‘Gan Jue’not Ke Kao，"
        "Dan logic and data Ke Kao。”"
    )

    parts = split_prose_dialogue_block(text, alias_to_canonical=alias_to_canonical)
    assert [p["character"] for p in parts] == ["Wen Wen", "Old Guai", "Wen Wen", "Old Guai"]
    assert parts[0]["content"].startswith("Ni……Ni Zen Me Zhi Dao")
    assert all(p["content"] != "Ka Wen" for p in parts)


def test_split_prose_dialogue_block_skips_ui_screen_text_quotes() -> None:
    alias_to_canonical = {"Wen Wen": "Wen Wen", "Old Guai": "Old Guai"}
    text = (
        "Wen Wen Bao Bi：“Xing A，Wo Dao Yao Kan Kan Ni Suan Fa have Duo Li Hai。” "
        "Old Guai connection Shang Wen Wen Dian Nao，Kai Shi Yun Xing repair Cheng Xu，and Tong Shi Qi Dong Yi Ge data Ti Qu Jiao Ben，"
        "screen on Dai Ma Gun Dong，display“Zheng Zai Ti Qu and Fen Xi Wen Dang structure data……”"
    )

    parts = split_prose_dialogue_block(text, alias_to_canonical=alias_to_canonical)
    assert [p["character"] for p in parts] == ["Wen Wen"]
    assert all("Zheng Zai Ti Qu and Fen Xi" not in p["content"] for p in parts)


def test_repair_scene_dialogues_for_audio_splits_narrator_prose_block() -> None:
    alias_to_canonical = {"Wen Wen": "Wen Wen", "Old Guai": "Old Guai"}
    dialogues = [
        {
            "character": "voiceover",
            "content": (
                "Wen Wen：“Ni Shuo Ni Neng Bang Wo……You Hua it，is Zhen De Ma？” "
                "Old Guai Dian Tou：“Zhen De。Wo Suan Fa Ke Yi You Hua Ni outline structure。”"
            ),
        }
    ]

    repaired = repair_scene_dialogues_for_audio(
        dialogues, alias_to_canonical=alias_to_canonical
    )
    assert [d["character"] for d in repaired] == ["Wen Wen", "Old Guai"]
    assert repaired[0]["content"].startswith("Ni Shuo Ni Neng Bang Wo")


def test_split_prose_dialogue_block_handles_chinese_single_quotes() -> None:
    alias_to_canonical = {"Li Zong": "Li Zong", "Su Qing": "Su Qing"}
    text = "Li Zong Zhui Wen：‘have Ju Ti Biao Di Ma？’ Su Qing Hui Da：‘Bi Ru，Ke Xun Ke Ji。’"

    parts = split_prose_dialogue_block(text, alias_to_canonical=alias_to_canonical)

    assert [p["character"] for p in parts] == ["Li Zong", "Su Qing"]
    assert [p["content"] for p in parts] == ["have Ju Ti Biao Di Ma？", "Bi Ru，Ke Xun Ke Ji。"]


def test_sanitize_stage_directions_removes_ascii_single_quoted_dialogue() -> None:
    cleaned = sanitize_stage_directions_for_audio(
        [
            {
                "scene_number": 1,
                "content": "Old Guai Tai Tou：'Shen Me Qing Kuang？' Ta Xun Su Qie Huan screen。",
            }
        ]
    )

    assert cleaned[0]["content"] == "Old Guai Tai Tou： Ta Xun Su Qie Huan screen。"


def test_split_audio_dialogues_moves_fallback_narrator_prose_to_action() -> None:
    dialogues = [
        {
            "character": "voiceover",
            "scene_number": 3,
            "fallback": True,
            "fallback_reason": "missing_dialogues",
            "content": (
                "conflict escalate：Mian Shi Xian Chang。heroine Zuo Zai Zhang Zhuo Yi Ce。" "Li Zong Zhui Wen：‘have Ju Ti Biao Di Ma？’"
            ),
        }
    ]

    repaired, action_blocks = split_audio_dialogues_and_action_blocks(
        dialogues,
        alias_to_canonical={},
    )

    assert repaired == []
    assert action_blocks == [
        {
            "type": "action",
            "timing": "mid",
            "content": dialogues[0]["content"],
            "scene_number": 3,
            "source": "dialogue_fallback",
        }
    ]
    assert should_treat_dialogue_as_action_for_audio(dialogues[0]) is True
