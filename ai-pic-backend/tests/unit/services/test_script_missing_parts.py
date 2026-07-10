import pytest
from app.services.script_missing_parts import populate_dialogues_and_stage_if_missing


@pytest.mark.unit
def test_no_missing_returns_original_lists():
    scenes = [{"scene_number": 1, "summary": "scene1"}]
    dialogues = [{"scene_number": 1, "character": "A", "content": "Ni Hao"}]
    stage = [{"scene_number": 1, "timing": "mid", "content": "action", "type": "action"}]

    out_dialogues, out_stage = populate_dialogues_and_stage_if_missing(
        scenes, dialogues, stage, story=None
    )

    assert out_dialogues == dialogues
    assert out_stage == stage


@pytest.mark.unit
def test_missing_dialogue_adds_narration_from_summary():
    scenes = [
        {"scene_number": 1, "summary": "scene1Zhai Yao"},
        {"scene_number": 2, "summary": "scene2Zhai Yao"},
    ]
    dialogues = [{"scene_number": 2, "character": "A", "content": "Ni Hao"}]
    stage = [{"scene_number": 2, "timing": "mid", "content": "action", "type": "action"}]

    out_dialogues, out_stage = populate_dialogues_and_stage_if_missing(
        scenes, dialogues, stage, story=None
    )

    # Scene 1 gets a narration fallback (no generic fake dialogue)
    scene1 = [d for d in out_dialogues if d.get("scene_number") == 1]
    assert len(scene1) == 1
    assert scene1[0].get("character") == "voiceover"
    assert scene1[0].get("content") == "scene1Zhai Yao"
    assert scene1[0].get("fallback") is True

    # Stage directions are also filled for missing scenes
    scene1_stage = [s for s in out_stage if s.get("scene_number") == 1]
    assert len(scene1_stage) == 1
    assert scene1_stage[0].get("type") == "action"
    assert scene1_stage[0].get("fallback") is True


@pytest.mark.unit
def test_missing_dialogue_extracts_quoted_scene_lines_before_narration():
    scenes = [
        {
            "scene_number": 1,
            "characters": ["Old Guai", "Wen Wen"],
            "description": (
                "Old Guai Zuo Zai Dian Nao Qian，screen Gun Dong Dai Ma。Ta Wei Wei Yi Xiao：'You Yi Ge Zi Dong Hua complete。'"
                "Jing Bao Sheng Da Zuo，'Shen Me Qing Kuang？'Ta Zhou Mei Zi Yan Zi Yu。"
            ),
        }
    ]

    out_dialogues, _ = populate_dialogues_and_stage_if_missing(
        scenes, [], [], story=None
    )

    assert [
        (item.get("character"), item.get("content"), item.get("fallback"))
        for item in out_dialogues
    ] == [
        ("Old Guai", "You Yi Ge Zi Dong Hua complete。", None),
        ("Old Guai", "Shen Me Qing Kuang？", None),
    ]


@pytest.mark.unit
def test_missing_dialogue_keeps_speakers_when_quotes_are_adjacent():
    scenes = [
        {
            "scene_number": 3,
            "characters": ["Old Guai", "Wen Wen"],
            "description": (
                "Wen Wen Zhu Yi to Lao Guai Dai Ma screen。'Zhe Xie is Shen Me？'Ta Zhi Zhe Yi Chuan data Wen。"
                "Old Guai Song Jian：'Sheng Cun Suan Fa，Ji Suan Mei Ge Ren Jia Zhi。'"
                "Wen Wen Zhou Mei：'Ni is in Gei Ren Tie Biao Qian Ma？'"
                "Old Guai Wu Nai：'Xiao Lv Zhi Shang。'"
                "Wen Wen Jian Ding：'Wo Hui Liu Xia，Bang Ni Jia Dian Ren Xing Hua。'"
            ),
        }
    ]

    out_dialogues, _ = populate_dialogues_and_stage_if_missing(
        scenes, [], [], story=None
    )

    assert [(item.get("character"), item.get("content")) for item in out_dialogues] == [
        ("Wen Wen", "Zhe Xie is Shen Me？"),
        ("Old Guai", "Sheng Cun Suan Fa，Ji Suan Mei Ge Ren Jia Zhi。"),
        ("Wen Wen", "Ni is in Gei Ren Tie Biao Qian Ma？"),
        ("Old Guai", "Xiao Lv Zhi Shang。"),
        ("Wen Wen", "Wo Hui Liu Xia，Bang Ni Jia Dian Ren Xing Hua。"),
    ]
