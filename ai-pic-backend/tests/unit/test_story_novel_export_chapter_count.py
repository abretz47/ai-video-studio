import re

import pytest
from app.services.story import story_novel_export_zhihu as export_module
from app.services.story import story_novel_export_zhihu_chapter as chapter_module


@pytest.mark.asyncio
async def test_story_novel_export_generates_all_planned_chapters(monkeypatch, tmp_path):
 monkeypatch.setattr(
 export_module.settings, "UPLOAD_DIR", str(tmp_path), raising=False
)

 chapter_total = 11
 chapters = [
 {
 "chapter_number": idx,
 "title": f"update {idx}",
 "target_words": 900,
 "chapter_goal": "Tui Jin conflict Bing Yin Chu new information",
 "cliffhanger_hint": "Liu Xia Xuan Nian Yin Dao Xia Yi Zhang",
 }
 for idx in range(1, chapter_total + 1)
 ]
 plan = {
 "question_title": "Wen Ti Biao Ti",
 "question_detail": "Wen Ti Bu Chong",
 "narrator_profile": "Hui Da Zhe Li Chang",
 "running_summary_seed": "",
 "chapters": chapters,
 }

 async def fake_plan_compact(**_):
 return plan, chapters

 async def fake_chapter_beats(**_):
 return ["beat1", "beat2", "beat3", "beat4", "beat5"]

 async def fake_generate_text(*, prompt: str, **_):
 chapter_match = re.search(r"Zhang Jie Hao: \s*(\d+)", prompt)
 chapter_no = int(chapter_match.group(1)) if chapter_match else 1
 if "Lian Guan Xing ledger(ledger)" in prompt and "output**Yan Ge JSON**" in prompt:
 return (
 '{"ledger":{"version":1,"facts":[],"timeline":[],"characters":{},'
 '"open_threads":[],"resolved_threads":[]},'
 '"chapter_summary":["ok"],"chapter_cliffhanger":"next"}'
)
 return (
 f"Di{chapter_no}Zhang Zheng Wen\n\n" "【chapter summary】\n- ok\n\n" "【chapter cliffhanger】\nnext\n"
)

 monkeypatch.setattr(export_module, "generate_zhihu_plan_compact", fake_plan_compact)
 monkeypatch.setattr(
 chapter_module, "generate_zhihu_chapter_beats", fake_chapter_beats
)
 monkeypatch.setattr(chapter_module, "generate_story_novel_text", fake_generate_text)
 monkeypatch.setattr(export_module, "generate_story_novel_text", fake_generate_text)

 result = await export_module.export_zhihu_novel_to_file(
 story_title="Test Story",
 story_payload={"title": "Test Story"},
 target_words=10000,
 chapter_total=chapter_total,
 model_id=None,
 prefer_provider=None,
 temperature=0.7,
 progress=None,
)

 assert result.chapter_count == chapter_total

 output_path = tmp_path / result.relative_path
 assert output_path.exists()
 text = output_path.read_text(encoding="utf-8")
 assert text.count("-- update ") == chapter_total
