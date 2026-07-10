from types import SimpleNamespace

import pytest
from app.services.script.story_structure_sync import (
 sync_script_scenes_to_story_structure,
)


@pytest.mark.unit
def test_sync_script_scenes_creates_scene_beats(monkeypatch):
 created_beat_payloads = []
 created_shots = []
 scene = SimpleNamespace(id=10, scene_number="1")

 def list_scenes_by_script(db, script_id):
 return []

 def create_scene(db, payload):
 return scene

 def create_scene_beat(db, payload):
 created_beat_payloads.append(payload)
 return SimpleNamespace(id=20, order_index=payload.order_index)

 def create_shot(db, payload):
 created_shots.append(payload)
 return SimpleNamespace(id=30)

 from app.services.script import story_structure_sync as module

 monkeypatch.setattr(
 module.story_structure_svc,
 "list_scenes_by_script",
 list_scenes_by_script,
)
 monkeypatch.setattr(module.story_structure_svc, "create_scene", create_scene)
 monkeypatch.setattr(
 module.story_structure_svc,
 "create_scene_beat",
 create_scene_beat,
)
 monkeypatch.setattr(module.story_structure_svc, "create_shot", create_shot)

 script = SimpleNamespace(
 id=1,
 scenes=[
 {
 "scene_number": 1,
 "slug_line": "INT. control room - night",
 "summary": "Shui Qing Kong Le bonus?",
 "beats": [
 {
 "order_index": 1,
 "beat_type": "hook",
 "dramatic_purpose": "Pao Chu Sun Shi",
 "visible_event": "screen bonus Gui Ling",
 "dialogue_lines": [
 {"character": "Xiao Ji", "content": "Jiang Jin Qing Ling?"}
 ],
 "action_lines": [{"content": "Hong Se Jing Bao Liang Qi"}],
 "duration_seconds": 5,
 "hook_tag": "loss",
 }
 ],
 }
 ],
 extra_metadata={},
)

 result = sync_script_scenes_to_story_structure(object(), script)

 assert result["created"] == 1
 assert result["beats_created"] == 1
 assert created_beat_payloads[0].beat_type == "hook"
 assert created_beat_payloads[0].dialogue_excerpt == "Xiao Ji: Jiang Jin Qing Ling?"
 assert created_beat_payloads[0].metadata["visible_event"] == "screen bonus Gui Ling"
 assert len(created_shots) == 1
