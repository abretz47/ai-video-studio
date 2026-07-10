# Translate AI Prompt Strings to English

## User Prompt
Translate Chinese text in specific Python files in the AI video production platform. ONLY string VALUES passed to AI models as prompts or used as seed/default data. Do not translate comments, docstrings, error messages, or detection/regex logic strings.

## Goals
1. Translate all qualifying Chinese string literals across 16 specified files
2. Preserve detection/regex/keyword logic strings that must match Chinese input
3. Update the affected unit test to match new English output

## Changes

### `app/prompts/template_defaults.py`
- `DEFAULT_GENERATION_PARAMS`: translated `target_audience`, `style_preferences`, `content_restrictions`
- `QUALITY_ENHANCERS["text"]`: translated all Chinese list values (creativity, quality, structure)
- `NEGATIVE_PROMPTS["text"]`: translated content and quality restriction lists
- `TEMPLATE_EXAMPLES`: translated all character names (Xiao Ya, Li Ming), descriptions, story title, genre, theme

### `app/services/ai/episodes_mock.py`
- Translated mock episode data: story title fallback, episode titles, summaries, plot point descriptions, timing labels, character arc/conflict descriptions, scene slug lines, locations, scene summaries, and prompt field

### `app/services/ai/episodes_mock_script.py`
- Translated default summary, episode title fallback, default location list, scene description fallbacks, stage direction content, camera suggestion, lighting value, character narrator fallback, production requirements label, timing value, and prompt field

### `app/services/ai/script_text.py`
- Translated: opening hook line, section headers (Scenes/Dialogue/Stage Directions), scene/dialogue line format prefixes (Scene N), narrator fallback, ending hook line with emotional annotation markers

### `app/services/ai/commercial_script_text.py`
- Translated: episode label (`第N集` → `Episode N`), opening hook stage direction, fallback scene summary, default stage direction fallback, default character name ("Narrator"), default dialogue content, default emotion label ("hushed tone"), cliffhanger line and stage direction
- `_normalize_space_type`: return values changed from `内`/`外` to `INT`/`EXT`
- `_normalize_time_of_day`: return values changed from `夜`/`晨`/`昏`/`日` to `NIGHT`/`MORNING`/`DUSK`/`DAY`
- Translated `or "主要场景"` fallback, default stage direction, narrator fallback in `_stage_line` and `_dialogue_line`

### `app/services/ai/commercial_script_beat_order.py`
- Translated default stage direction content and narrator fallback

### `app/services/agent_core/context_specs.py`
- Translated Chinese genre examples in `StoryContext.genre` description
- Translated Chinese tone examples in `StoryContext.tone` description

### `app/services/agent_core/failure_patterns.py`
- Translated all `repair_hints` lists (14 repair hint groups) from Chinese to English

### `tests/unit/services/test_commercial_script_text.py`
- Updated test assertions to match new English output (`Episode 1`, `Characters:`)

## Files With No Qualifying Chinese (Skipped or Clean)
- `prompt_variants.py`: Chinese strings are detection keywords in code logic (`短剧`, `电影` etc.), not AI prompt content
- `episodes.py`: Chinese only in docstrings and comments
- `scripts.py`: Chinese only in comments
- `storyboard_generation.py`: Chinese only in print error message
- `storyboard_plan.py`: Chinese only in print error messages
- `story_outline.py`: Chinese only in log warning / print error messages
- `quality_loop.py`: Chinese in detection keyword lists (not AI prompt content)
- `dialogue_audio_agent.py`: Chinese in `EMOTION_KEYWORDS["zh"]` - functional keyword detection lists for Chinese TTS input classification (left intact)

## Validation
- All 8 modified Python files pass `ast.parse()` syntax check
- `tests/unit/services/test_commercial_script_text.py` passes (1 passed)
- All other test failures verified as pre-existing (confirmed by git stash test)

## Next Steps
- None; translation task is complete. The detection/regex patterns that contain Chinese characters are intentionally preserved to continue matching Chinese-format screenplay sluglines and error messages.

## Linked Commits
- (this commit)
