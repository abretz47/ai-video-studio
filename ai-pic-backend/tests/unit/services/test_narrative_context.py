from __future__ import annotations

import pytest

from app.services.narrative_context import extract_story_characters


@pytest.mark.unit
def test_extract_story_characters_prefers_characters() -> None:
    story = {
        "characters": [{"name": "protagonist"}, {"name": "protagonist"}, {"character_name": "Fan Pai"}],
        "character_profiles": [{"name": "Bei Yong"}],
        "main_characters": [{"name": "Jiu character"}],
    }

    assert extract_story_characters(story) == [
        {"name": "protagonist"},
        {"character_name": "Fan Pai", "name": "Fan Pai"},
    ]


@pytest.mark.unit
def test_extract_story_characters_supports_character_profiles() -> None:
    story = {"character_profiles": [{"character_name": "Lin Xue", "role": "lead"}]}

    assert extract_story_characters(story) == [
        {"character_name": "Lin Xue", "role": "lead", "name": "Lin Xue"}
    ]


@pytest.mark.unit
def test_extract_story_characters_supports_main_characters_strings() -> None:
    story = {"main_characters": ["Chen Zhe", {"name": "Lin Xue"}]}

    assert extract_story_characters(story) == [{"name": "Chen Zhe"}, {"name": "Lin Xue"}]
