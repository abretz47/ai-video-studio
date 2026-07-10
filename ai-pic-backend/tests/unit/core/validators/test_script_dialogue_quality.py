from app.core.validators.script_dialogue_quality import (
    find_reused_short_dialogues,
    looks_like_writer_note,
    validate_scene_dialogues,
)


def test_looks_like_writer_note_detects_meta_instruction():
    assert looks_like_writer_note("Ming Bai，Zhe Li Ke Yi Tu Chu conflict or emotion。") is True
    assert looks_like_writer_note("Zhu：Ci Chu Jian Yi Jia Qiang conflict。") is True


def test_looks_like_writer_note_allows_in_world_suggestion():
    assert looks_like_writer_note("Wo Jian Yi Ni Xian Zai Jiu Zou。") is False


def test_find_reused_short_dialogues_flags_cross_scene_duplicates():
    dialogues = [
        {"scene_number": 1, "character": "Old Guai", "content": "etc Yi Xia……Rang Wo Zai confirm Yi Xia。"},
        {"scene_number": 2, "character": "Old Guai", "content": "etc Yi Xia……Rang Wo Zai confirm Yi Xia。"},
        {"scene_number": 1, "character": "A Gai Er", "content": "Ming Bai，Wo Men continue。"},
        {"scene_number": 3, "character": "A Gai Er", "content": "Ming Bai，Wo Men continue。"},
    ]
    reps = find_reused_short_dialogues(dialogues, max_chars=40, min_repeats=2)
    assert "etc Yi Xia Rang Wo Zai confirm Yi Xia" in reps
    assert "Ming Bai Wo Men continue" in reps


def test_validate_scene_dialogues_reports_quality_issues():
    repeated = {"Ming Bai Wo Men continue"}
    scene_dialogues = [
        {"scene_number": 1, "character": "A Gai Er", "content": "Ming Bai，Wo Men continue。"},
        {
            "scene_number": 1,
            "character": "A Gai Er",
            "content": "Ming Bai，Zhe Li Ke Yi Tu Chu conflict or emotion。",
        },
    ]
    issues = validate_scene_dialogues(
        scene_dialogues, min_lines=2, repeated_short_norms=repeated
    )
    codes = {i.code for i in issues}
    assert "writer_note" in codes
    assert "reused_filler" in codes


def test_validate_scene_dialogues_enforces_min_lines():
    issues = validate_scene_dialogues(
        [{"scene_number": 1, "character": "A", "content": "Ni Hao"}],
        min_lines=2,
        repeated_short_norms=set(),
    )
    assert any(i.code == "too_few_lines" for i in issues)
