from __future__ import annotations

import pytest
from app.models.script import Story, StoryCharacter
from app.models.virtual_ip import VirtualIP
from app.services.script.script_character_policy import enforce_script_character_policy


def _make_story_with_registry() -> Story:
 story = Story(
 user_id=1,
 title="S",
 story_format="short_drama",
 genre="drama",
 default_aspect_ratio="9:16",
)

 vip_male = VirtualIP(user_id=1, name="short dramaE2ENan Zhu-Chen Zhe")
 vip_female = VirtualIP(user_id=1, name="short dramaE2Eheroine-Lin Xue-2026-01-19T03-52-25-958Z")

 sc_male = StoryCharacter(
 story_id=1,
 virtual_ip_id=1,
 character_name="Chen Zhe",
 is_deleted=False,
)
 sc_male.virtual_ip = vip_male

 # character_name intentionally omitted to cover preferred_display_name(vip.name).
 sc_female = StoryCharacter(
 story_id=1,
 virtual_ip_id=2,
 character_name=None,
 is_deleted=False,
)
 sc_female.virtual_ip = vip_female

 story.story_characters = [sc_male, sc_female]
 return story


@pytest.mark.unit
def test_enforce_script_character_policy_normalizes_and_detects_unknown() -> None:
 story = _make_story_with_registry()
 scenes = [{"characters": ["Xiao Xue", "Passerby A", "Fan Pai Lao Guai"]}]
 dialogues = [{"character": "clerkA", "content": "Ni Hao"}, {"content": "Pang Bai Nei Rong"}]

 result = enforce_script_character_policy(
 story=story, scenes=scenes, dialogues=dialogues
)

 assert result.unknown_names == ["Fan Pai Lao Guai"]
 assert set(result.canonical_names) == {"Chen Zhe", "Lin Xue"}
 assert result.normalized_count >= 1

 assert scenes[0]["characters"] == ["Lin Xue", "passerby", "Fan Pai Lao Guai"]
 assert dialogues[0]["character"] == "clerk"
 assert dialogues[1]["character"] == "voiceover"


@pytest.mark.unit
def test_enforce_script_character_policy_allows_short_drama_functional_roles() -> None:
 story = _make_story_with_registry()
 scenes = [{"characters": ["Lin Xue", "customer", "Tuan Dui Cheng YuanA", "Cuan Gai Zhe"]}]
 dialogues = [
 {"character": "customer", "content": "Zhe data Bu Dui."},
 {"character": "Zhu Li", "content": "Wo Ma Shang Diao file."},
 {"character": "Tuan Dui Cheng YuanB", "content": "Bu Shi Wo."},
 {"character": "recording", "content": "data Wo Gai Le."},
 ]

 result = enforce_script_character_policy(
 story=story, scenes=scenes, dialogues=dialogues
)

 assert result.unknown_names == []
 assert scenes[0]["characters"] == ["Lin Xue", "customer", "Tuan Dui Cheng Yuan", "Cuan Gai Zhe"]
 assert [d["character"] for d in dialogues] == [
 "customer",
 "Zhu Li",
 "Tuan Dui Cheng Yuan",
 "recording",
 ]


@pytest.mark.unit
def test_enforce_script_character_policy_is_backwards_compatible_without_registry() -> (
 None
):
 story = Story(
 user_id=1,
 title="S",
 story_format="short_drama",
 genre="drama",
 default_aspect_ratio="9:16",
)
 story.story_characters = []

 scenes = [{"characters": ["Chen Zhe"]}]
 dialogues = [{"content": "Mei You speaker Shi Ying Mo Ren voiceover"}]

 result = enforce_script_character_policy(
 story=story, scenes=scenes, dialogues=dialogues
)

 assert result.unknown_names == []
 assert result.canonical_names == []
 assert result.normalized_count == 0
 assert dialogues[0]["character"] == "voiceover"
