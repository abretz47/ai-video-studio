## User Prompt

Update all parts of the backend that seed an AI prompt/response in Chinese to English. Users see Chinese characters driving the backend and agent prompts when using English translations in Next.js.

## Goals

Translate all AI prompt templates and seed data from Chinese to English so that when the English locale is active, AI-generated content is guided by English-language instructions.

## Changes

### Commit `5610353a` — Template files (81 `.txt` files)
- `app/prompts/templates/*.txt` — all system prompts, episode generation, story outline, script generation, storyboard, dialogue, timeline, virtual IP, macro fragment templates translated to natural English
- All Jinja2 syntax (`{{ }}`, `{% %}`, macros, filters) preserved exactly

### Commit `df9bbb94` — Python prompt/service files
- `app/prompts/template_defaults.py` — audience, style preferences, content restrictions, character example data
- `app/services/ai/episodes_mock.py` — mock episode titles, summaries, plot points
- `app/services/ai/episodes_mock_script.py` — mock script content, locations, descriptions
- `app/services/ai/script_text.py` — section headers, hooks, annotation markers
- `app/services/ai/commercial_script_text.py` — episode labels, hooks, stage directions
- `app/services/ai/commercial_script_beat_order.py` — stage direction fallback, narrator labels
- `app/services/agent_core/context_specs.py` — genre/tone field description examples
- `app/services/agent_core/failure_patterns.py` — repair hint strings

### Intentionally NOT translated
- Python comments/docstrings — developer notes, not AI prompts
- Regex patterns in `failure_patterns.py` that detect Chinese error output from AI (bilingual detection)
- Functional keyword detection in `prompt_variants.py`, `commercial_script_text.py` (INT/EXT parsers)
- `dialogue_audio_agent.py` `"zh"` emotion keywords — enable bilingual input handling

## Validation

- 0 template `.txt` files still contain Chinese characters
- Key Python prompt files checked clean (outside intentionally preserved bilingual regex patterns)
- All Jinja2 template syntax preserved intact

## Next Steps

Restart backend and test AI generation flows to confirm Chinese no longer appears in generated content when using English locale.

## Linked Commits

- `5610353a` i18n: translate all AI prompt templates from Chinese to English
- `df9bbb94` i18n: translate Chinese AI prompt strings and seed data to English
