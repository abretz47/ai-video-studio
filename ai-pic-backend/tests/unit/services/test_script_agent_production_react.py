from typing import Any
from types import SimpleNamespace

import pytest

from app.services.script_agent import ScriptLangGraphAgent


@pytest.mark.unit
def test_script_agent_character_validation_ignores_functional_roles() -> None:
    agent = ScriptLangGraphAgent(SimpleNamespace())
    content: dict[str, Any] = {
        "dialogues": [
            {"character": "APreturn character-20260618T164912", "content": "Cha Yuan Shi file。"},
            {"character": "client", "content": "Jie Shi Qing Chu。"},
            {"character": "Zhu Li", "content": "Ma Shang Tou Ping。"},
            {"character": "team Cheng YuanA", "content": "Bu Shi Wo。"},
            {"character": "recording", "content": "data Wo Gai。"},
        ]
    }

    result = agent._validate_script_characters(
        content,
        [
            {
                "name": "APreturn character-20260618T164912",
                "description": "project Fu Ze Ren",
            }
        ],
    )

    assert result["character_validation_passed"] is True
    assert result["unknown_names"] == []
