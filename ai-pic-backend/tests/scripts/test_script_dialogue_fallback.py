import json
from types import SimpleNamespace

from app.models.story_structure import Scene
from tests.fixtures.mock_ai_script_payloads import mock_passing_script_payload
from tests.factories import EpisodeFactory, setup_factories


def test_generate_script_dialogue_fallback(client, db_session, monkeypatch):
    setup_factories(db_session)
    episode = EpisodeFactory()

    # Rang generate_script Jin return scene，Chu Fa dialogue/stage directions Zhan Wei generate
    from app.services import ai_service as ai_module

    async def fake_generate_script(**_: object):
        return {
            "content": {
                "scenes": [{"scene_number": 1, "summary": "test scene dialogue Que Shi"}],
                "dialogues": [],
                "stage_directions": [],
            },
            "prompt": "mock",
            "generation_method": "mock-provider:fallback",
        }

    monkeypatch.setattr(ai_module.ai_service, "generate_script", fake_generate_script)

    async def fake_generate_text(prompt: str, **_: object):
        if "failed strict quality gate validation" in prompt:
            data = mock_passing_script_payload("Character1")
        else:
            data = {
                "passed": True,
                "score": 0.95,
                "reason": "mock cliffhanger pass",
                "evidence": "mock",
                "suggestion": "",
            }
        return SimpleNamespace(
            success=True,
            data=json.dumps(data, ensure_ascii=False),
            provider="mock-provider",
            model="mock-model",
            usage={},
        )

    monkeypatch.setattr(
        ai_module.ai_service.ai_manager,
        "generate_text",
        fake_generate_text,
    )

    payload = {
        "episode_id": episode.id,
        "format_type": "screenplay",
        "language": "zh-CN",
        "dialogue_style": "natural",
        "scene_detail_level": "medium",
        "temperature": 0.7,
    }

    resp = client.post("/api/v1/scripts/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["dialogues"], "dialogue Ying Zi Dong Bu Qi"
    assert data["dialogues"][0]["scene_number"] == 1
    assert data["stage_directions"], "stage directions Ying Zi Dong Bu Qi"

    # Que Bao Gui Fan Hua scene Reng Tong Bu
    scenes = (
        db_session.query(Scene)
        .filter(Scene.script_id == data["id"])
        .order_by(Scene.scene_number.asc())
        .all()
    )
    assert len(scenes) == 1
