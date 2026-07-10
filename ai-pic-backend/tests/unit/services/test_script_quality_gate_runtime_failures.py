from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from app.models.script import Story, StoryCharacter
from app.services.narrative_quality_gate import enforce_script_quality_gate_with_repair


def _passing_script_text() -> str:
 return "\n".join(
 [
 "【sound effect】Bang! The door is forced open.",
 "Scene 1 living room - night",
 "【fast】【emotion goal: Bi Chu Zhen Xiang】Lin Xue Zhua Zhu ledger, camera Tui Jin Ta Fa Dou De Shou.",
 "【sound effect】Jing Bao Sheng from Chuang Wai Bi Jin.",
 "Lin Xue: don't move!ledger Shang why You you De name?",
 "Chen Mo: Bu Shi Wo, N...someone altered it.",
 "(action)Chen Mo Hou Tui Ban Bu, Bei Zi Luo Di.",
 "Scene 2 Tian Tai - night",
 "【slow】【emotion goal: Zhi Zao Fan Zhuan】Lin Xue Ba ledger Ju Dao Deng Xia, red signature Lu Chu.",
 "Chen Mo: you Kan final Yi Ye.",
 "Lin Xue: Na real signed De Ren Shi Shui?",
 ]
)


def _script_content(text: str | None = None) -> dict[str, Any]:
 return {
 "content": text or _passing_script_text(),
 "scenes": [{"scene_number": 1, "description": "Lin Xue Zai living room press Chen Mo."}],
 "dialogues": [
 {"scene_number": 1, "character": "Lin Xue", "content": "don't move!"},
 {"scene_number": 1, "character": "Chen Mo", "content": "Bu Shi Wo, N..."},
 ],
 "stage_directions": [{"scene_number": 1, "content": "Lin Xue Zhua Zhu ledger."}],
 "metadata": {},
 }


class _RepairManager:
 def __init__(self, payloads: list[dict[str, Any]]) -> None:
 self.payloads = list(payloads)
 self.calls = 0
 self.call_kwargs: list[dict[str, Any]] = []

 async def generate_text(self, **kwargs: Any) -> Any:
 schema = kwargs.get("json_schema") or {}
 if schema.get("name") == "script_cliffhanger_judgement":
 return SimpleNamespace(
 success=True,
 provider="fake",
 model="fake-model",
 data={
 "passed": True,
 "score": 1.0,
 "reason": "ok",
 "evidence": "tail",
 "suggestion": "",
 },
)
 self.calls += 1
 self.call_kwargs.append(kwargs)
 payload = self.payloads.pop(0) if self.payloads else {}
 return SimpleNamespace(success=True, data=payload)


class _EpisodeCharacterQuery:
 def __init__(self, rows: list[Any]) -> None:
 self.rows = rows

 def filter(self, *args: Any, **kwargs: Any) -> "_EpisodeCharacterQuery":
 return self

 def all(self) -> list[Any]:
 return list(self.rows)


class _EpisodeCharacterDb:
 def __init__(self) -> None:
 self.episode_chars: list[Any] = []

 def query(self, model: Any) -> _EpisodeCharacterQuery:
 return _EpisodeCharacterQuery(self.episode_chars)


def _story_model_with_registry() -> Story:
 story = Story(
 user_id=7,
 title="S",
 story_format="short_drama",
 genre="drama",
 default_aspect_ratio="9:16",
)
 story.story_characters = [
 StoryCharacter(character_name="Lin Xue", is_deleted=False),
 StoryCharacter(character_name="Chen Mo", is_deleted=False),
 ]
 return story


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_auto_creates_episode_temporary_speaker(
 monkeypatch: pytest.MonkeyPatch,
) -> None:
 content = _script_content()
 content["scenes"][0]["characters"] = ["Lin Xue", "Kuai Di Yuan"]
 content["dialogues"].append(
 {"scene_number": 1, "character": "Kuai Di Yuan", "content": "don't move!"}
)
 db = _EpisodeCharacterDb()

 async def fake_auto_create_episode_characters(
 **kwargs: Any,
) -> list[dict[str, Any]]:
 assert kwargs["unknown_names"] == ["Kuai Di Yuan"]
 kwargs["db"].episode_chars.append(
 SimpleNamespace(
 character_name="Kuai Di Yuan",
 virtual_ip=None,
 virtual_ip_id=99,
 is_deleted=False,
)
)
 return [{"episode_character_id": 123, "character_name": "Kuai Di Yuan"}]

 monkeypatch.setattr(
 "app.services.script.auto_character_creator.auto_create_episode_characters",
 fake_auto_create_episode_characters,
)

 result, updated_content, gate = await enforce_script_quality_gate_with_repair(
 ai_manager=_RepairManager([]),
 result={
 "character_validation_passed": False,
 "character_validation_results": [
 {
 "passed": False,
 "severity": "warning",
 "message": "Found 1 unknown speaker(s) in dialogues",
 "details": {"unknown_speakers": ["Kuai Di Yuan"]},
 }
 ],
 "character_warnings": ["Unknown speaker(s) in dialogues: Kuai Di Yuan"],
 "unknown_names": ["Kuai Di Yuan"],
 },
 content=content,
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
 story_model=_story_model_with_registry(),
 episode_id=55,
 db=db,
 lint_threshold=0.0,
)

 assert gate["passed"] is True
 assert result["character_validation_passed"] is True
 assert result["unknown_names"] == []
 assert result["auto_created_characters"] == [
 {"episode_character_id": 123, "character_name": "Kuai Di Yuan"}
 ]
 assert updated_content["dialogues"][-1]["character"] == "Kuai Di Yuan"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_rejects_repair_that_drops_script_structure() -> None:
 manager = _RepairManager(
 [
 {
 "content": "Di3Ji",
 "scenes": [],
 "dialogues": [],
 "stage_directions": [],
 "metadata": {},
 },
 _script_content(),
 ]
)

 result, content, gate = await enforce_script_quality_gate_with_repair(
 ai_manager=manager,
 result={},
 content=_script_content("Bad text."),
 story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
)

 assert gate["passed"] is True
 assert result["quality_gate"]["passed"] is True
 assert content["content"] == _passing_script_text()
 assert manager.calls == 2
 assert gate["repair_attempts"][0]["structure_guard"]["passed"] is False
 assert gate["repair_attempts"][0]["structure_guard"]["lost_fields"] == [
 "scenes",
 "dialogues",
 "stage_directions",
 ]
