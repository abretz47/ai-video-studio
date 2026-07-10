## User Prompt
Translate Chinese text to English in 25 AI prompt template files under `ai-pic-backend/app/prompts/templates/`, preserving all Jinja2 syntax exactly.

## Goals
- Translate all Chinese prompt text in the requested template files into natural professional English.
- Preserve all Jinja2 syntax, variable names, control blocks, and formatting.
- Validate that no Chinese characters remain in the targeted files.

## Changes
- Translated all requested script prompt templates to English:
  - `script_dialogues_short_drama.txt`
  - `script_generation.txt`
  - `script_generation_short_drama.txt`
  - `script_review.txt`
  - `script_scenes.txt`
  - `script_scenes_film.txt`
  - `script_scenes_short_drama.txt`
  - `script_scenes_tv_series.txt`
  - `script_score.txt`
  - `script_word_count_constraint.txt`
- Translated all requested Zhihu-story and story-outline prompt templates to English:
  - `story_novel_zhihu_chapter.txt`
  - `story_novel_zhihu_chapter_beats.txt`
  - `story_novel_zhihu_chapter_finalize.txt`
  - `story_novel_zhihu_chapter_rewrite.txt`
  - `story_novel_zhihu_ledger_update.txt`
  - `story_novel_zhihu_plan.txt`
  - `story_novel_zhihu_plan_compact.txt`
  - `story_outline.txt`
  - `story_outline_film.txt`
  - `story_outline_repair.txt`
  - `story_outline_short_drama.txt`
  - `story_outline_tv_series.txt`
- Translated requested storyboard prompt templates to English:
  - `storyboard_audio_visual_action.txt`
  - `storyboard_audio_visual_context.txt`
  - `storyboard_audio_visual_dialogue_read_text.txt`
- Kept all `{{ }}`, `{% %}`, filters, and variable names unchanged while translating surrounding prompt text.

## Validation
- `rg "[\\p{Han}]" <25 targeted files>` → no Chinese characters found in the requested files.
- `git --no-pager diff --check` → clean.
- `cd ai-pic-backend && python run_tests.py quick` → could not run because the repository virtual environment was not present (`虚拟环境不存在，请先创建虚拟环境`).

## Next Steps
- If backend test infrastructure is restored, rerun `cd ai-pic-backend && python run_tests.py quick` for an environment-backed verification pass.
- Optionally review neighboring prompt templates for punctuation/style normalization if broader English localization is desired.

## Linked Commits
- None in this session.
