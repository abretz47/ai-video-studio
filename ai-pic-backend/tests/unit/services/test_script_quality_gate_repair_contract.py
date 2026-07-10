from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from app.models.script import Story, StoryCharacter
from app.services.narrative_quality_gate import enforce_script_quality_gate_with_repair
from app.services.quality_gate_core import NarrativeQualityGateError


def _passing_script_text() -> str:
    return "\n".join(
        [
            "【sound effect】Bang! The door is forced open.",
            "Scene 1 living room - night",
            "【fast】【emotion goal：Bi Chu truth】Lin Xue Zhua Zhu ledger，camera Tui Jin Ta Fa Dou Shou。",
            "【sound effect】Jing Bao Sheng from Chuang Wai Bi Jin。",
            "Lin Xue：don't move！ledger on why have Ni name？",
            "Chen Mo：Bu Shi Wo，N...someone altered it。",
            "（action）Chen Mo Hou Tui Ban Bu，Bei Zi Luo Di。",
            "Scene 2 Tian Tai - night",
            "【slow】【emotion goal：Zhi Zao Fan Zhuan】Lin Xue ledger Ju Dao Deng Xia，red signature Lu Chu。",
            "Chen Mo：Ni Kan final Yi Ye。",
            "Lin Xue：Na real sign Ren is who？",
        ]
    )


def _script_content(text: str | None = None) -> dict[str, Any]:
    return {
        "content": text or _passing_script_text(),
        "scenes": [{"scene_number": 1, "description": "Lin Xue in living room press Chen Mo。"}],
        "dialogues": [
            {"scene_number": 1, "character": "Lin Xue", "content": "don't move！"},
            {"scene_number": 1, "character": "Chen Mo", "content": "Bu Shi Wo，N..."},
        ],
        "stage_directions": [{"scene_number": 1, "content": "Lin Xue Zhua Zhu ledger。"}],
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
                data={"passed": True, "score": 1.0, "reason": "ok"},
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


def _story_model_with_ap_registry() -> Story:
    story = Story(user_id=7, title="S", story_format="short_drama", genre="drama")
    story.default_aspect_ratio = "9:16"
    story.story_characters = [StoryCharacter(character_name="AP", is_deleted=False)]
    return story


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_refreshes_stale_unknown_speaker_flag_without_creation() -> None:
    content = {
        "content": _passing_script_text(),
        "scenes": [{"scene_number": 1, "description": "APCha Kan Duan Xin。"}],
        "dialogues": [
            {"scene_number": 1, "character": "AP", "content": "Zheng Ju in this。"},
            {"scene_number": 1, "character": "Duan Xin", "content": "Xia Yi Ge Jiu Shi Ni。"},
        ],
        "stage_directions": [{"scene_number": 1, "content": "APJu Qi phone。"}],
        "metadata": {},
    }

    result, _content, gate = await enforce_script_quality_gate_with_repair(
        ai_manager=_RepairManager([]),
        result={
            "character_validation_passed": False,
            "character_validation_results": [
                {
                    "passed": False,
                    "severity": "warning",
                    "message": "Found 2 unknown speaker(s) in dialogues",
                    "details": {"unknown_speakers": ["AP", "Duan Xin"]},
                }
            ],
            "character_warnings": ["Unknown speaker(s) in dialogues: AP, Duan Xin"],
            "unknown_names": ["AP", "Duan Xin"],
        },
        content=content,
        story={"characters": [{"name": "AP"}]},
        story_model=_story_model_with_ap_registry(),
        episode_id=55,
        db=_EpisodeCharacterDb(),
        lint_threshold=0.0,
    )

    assert gate["passed"] is True
    assert result["character_validation_passed"] is True
    assert result["unknown_names"] == []
    assert "auto_created_characters" not in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_repair_uses_generation_provider_for_auto_model() -> None:
    manager = _RepairManager([_script_content()])

    result, _content, gate = await enforce_script_quality_gate_with_repair(
        ai_manager=manager,
        result={"provider_used": "deepseek", "model_used": "deepseek-v4-flash"},
        content=_script_content("Bad text."),
        story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
    )

    assert gate["passed"] is True
    assert result["quality_gate"]["passed"] is True
    assert manager.calls == 1
    assert manager.call_kwargs[0]["prefer_provider"] == "deepseek"
    assert manager.call_kwargs[0]["model"] == "deepseek-v4-flash"
    assert "Return the repaired script payload itself" not in manager.call_kwargs[0][
        "prompt"
    ]
    assert "Every structured_script_contract.scenes item" not in manager.call_kwargs[0][
        "prompt"
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_script_gate_beat_contract_repair_prompt_is_payload_specific() -> None:
    manager = _RepairManager([_script_content()])

    with pytest.raises(NarrativeQualityGateError):
        await enforce_script_quality_gate_with_repair(
            ai_manager=manager,
            result={"provider_used": "deepseek", "model_used": "deepseek-v4-flash"},
            content=_script_content("Bad text."),
            story={"characters": [{"name": "Lin Xue"}, {"name": "Chen Mo"}]},
            require_beat_contract=True,
        )

    prompt = manager.call_kwargs[0]["prompt"]
    assert manager.call_kwargs[0]["prefer_provider"] == "deepseek"
    assert manager.call_kwargs[0]["model"] == "deepseek-v4-flash"
    assert "Return the repaired script payload itself" in prompt
    assert "Every structured_script_contract.scenes item" in prompt
    assert "duration_seconds values in each scene must sum" in prompt
