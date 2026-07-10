from app.prompts.manager import prompt_manager
from app.services.story.story_novel_export_continuity import (
    ensure_markers,
    extract_chapter_markers,
    normalize_ledger_update_payload,
)


def test_extract_chapter_markers_parses_summary_and_cliffhanger():
    text = (
        "Zheng Wen Di Yi Duan\nZheng Wen Di Er Duan\n\n"
        "【Ben Zhang Xiao Jie】\n- Fa Sheng A\n- Fa Sheng B\n\n"
        "【Ben Zhang cliffhanger】\nMen Wai Jiao Bu Sheng Yue Lai Yue Jin。"
    )
    body, summary, cliffhanger = extract_chapter_markers(text)

    assert body == "Zheng Wen Di Yi Duan\nZheng Wen Di Er Duan"
    assert "- Fa Sheng A" in summary
    assert "Jiao Bu Sheng" in cliffhanger


def test_extract_chapter_markers_strips_leading_marker_block():
    text = (
        "【Ben Zhang Xiao Jie】\n- Xian Gei Xiao Jie\n\n"
        "【Ben Zhang cliffhanger】\nXian Gei cliffhanger\n\n"
        "Zheng Wen from Zhe Li start\ncontinue Zheng Wen"
    )
    body, summary, cliffhanger = extract_chapter_markers(text)

    assert body.startswith("Zheng Wen from Zhe Li start")
    assert "Xian Gei Xiao Jie" in summary
    assert cliffhanger == "Xian Gei cliffhanger"


def test_ensure_markers_appends_missing_markers():
    body = "Zheng Wen"
    merged = ensure_markers(
        body, summary_text="- Yao Dian 1\n- Yao Dian 2", cliffhanger_text="hook Ju Zi"
    )

    assert "【Ben Zhang Xiao Jie】" in merged
    assert "【Ben Zhang cliffhanger】" in merged
    assert merged.endswith("\n")


def test_normalize_ledger_update_payload_formats_summary_and_skips_missing_ledger():
    payload = {
        "chapter_summary": ["1. Di Yi Jian Shi", "- Di Er Jian Shi", "  • Di San Jian Shi  "],
        "chapter_cliffhanger": "  hook  ",
    }
    ledger, summary_text, cliffhanger = normalize_ledger_update_payload(payload)

    assert ledger == {}
    assert summary_text == "- Di Yi Jian Shi\n- Di Er Jian Shi\n- Di San Jian Shi"
    assert cliffhanger == "hook"


def test_normalize_ledger_update_payload_compacts_ledger_when_present():
    payload = {
        "ledger": {
            "version": 2,
            "facts": list(range(40)),
            "timeline": [{"chapter": 1, "events": ["a"]}] * 50,
            "characters": {"A": {"status": "ok", "goal": "", "relationships": {}}},
            "open_threads": ["x"] * 40,
            "resolved_threads": ["y"] * 40,
        },
        "chapter_summary": "Fa Sheng Shi",
        "chapter_cliffhanger": "",
    }
    ledger, summary_text, cliffhanger = normalize_ledger_update_payload(payload)

    assert ledger["version"] == 2
    assert len(ledger["facts"]) == 25
    assert len(ledger["timeline"]) == 30
    assert len(ledger["open_threads"]) == 25
    assert len(ledger["resolved_threads"]) == 25
    assert summary_text.startswith("- ")
    assert cliffhanger == ""


def test_story_novel_zhihu_prompts_render_with_new_variables():
    base_payload = {
        "story": {"title": "test story", "genre": "drama"},
        "plan": {"chapter_total": 3, "current_chapter": {"chapter_number": 1}},
        "ledger": {
            "version": 1,
            "facts": [],
            "timeline": [],
            "characters": {},
            "open_threads": [],
            "resolved_threads": [],
        },
        "previous_tail": "",
        "chapter": {
            "chapter_number": 1,
            "title": "update 1",
            "target_words": 1200,
            "key_beats": ["Qi Bi", "Tui Jin", "Fan Zhuan"],
            "cliffhanger_hint": "cliffhanger prompt",
        },
        "running_summary": "",
        "remaining_target_words": 20000,
        "total_target_words": 20000,
    }

    prompt_manager.render_prompt("story_novel_zhihu_chapter", base_payload)
    prompt_manager.render_prompt(
        "story_novel_zhihu_chapter_rewrite", {**base_payload, "draft": "Cao Gao content"}
    )

    prompt_manager.render_prompt(
        "story_novel_zhihu_ledger_update",
        {
            "previous_ledger": base_payload["ledger"],
            "chapter_number": 1,
            "chapter_title": "update 1",
            "chapter_text": "Zheng Wen\n【Ben Zhang Xiao Jie】\n- Yao Dian\n【Ben Zhang cliffhanger】\nhook\n",
            "extracted_summary": "- Yao Dian",
            "extracted_cliffhanger": "hook",
        },
    )
