from __future__ import annotations

import json
from typing import Any

_SCENE_PLAN_SCHEMA_PAYLOAD = {
    "name": "script_scenes",
    "schema": json.loads(
        '{"type":"object","properties":{"scenes":{"type":"array","items":{"type":"object","properties":{"scene_number":{"type":"integer"},"slug_line":{"type":"string"},"location":{"type":"string"},"time_of_day":{"type":"string"},"summary":{"type":"string"},"estimated_duration_seconds":{"anyOf":[{"type":"integer"},{"type":"null"}]},"dialogue_ratio":{"anyOf":[{"type":"number"},{"type":"null"}]}}}}}}'
    ),
}

_DIALOGUE_SCHEMA_PAYLOAD = {
    "name": "script_dialogues",
    "schema": json.loads(
        '{"type":"object","properties":{"dialogues":{"type":"array","items":{"type":"object","properties":{"scene_number":{"anyOf":[{"type":"integer"},{"type":"null"}]},"character":{"anyOf":[{"type":"string"},{"type":"null"}]},"content":{"type":"string"},"emotion":{"anyOf":[{"type":"string"},{"type":"null"}]},"action":{"anyOf":[{"type":"string"},{"type":"null"}]}}}},"stage_directions":{"type":"array","items":{"type":"object","properties":{"scene_number":{"anyOf":[{"type":"integer"},{"type":"null"}]},"timing":{"anyOf":[{"type":"string"},{"type":"null"}]},"content":{"type":"string"},"type":{"anyOf":[{"type":"string"},{"type":"null"}]}}}},"scenes":{"type":"array","items":{"type":"object","properties":{"scene_number":{"anyOf":[{"type":"integer"},{"type":"null"}]},"slug_line":{"anyOf":[{"type":"string"},{"type":"null"}]},"summary":{"anyOf":[{"type":"string"},{"type":"null"}]}}}}}}'
    ),
}

_BEAT_CONTRACT_SCHEMA_PAYLOAD = {
    "name": "script_beat_contract",
    "schema": json.loads(
        '{"type":"object","properties":{"contract_version":{"type":"string"},"title":{"anyOf":[{"type":"string"},{"type":"null"}]},"logline":{"anyOf":[{"type":"string"},{"type":"null"}]},"scenes":{"type":"array","items":{"type":"object","properties":{"scene_number":{"type":"integer"},"slug_line":{"type":"string"},"location":{"anyOf":[{"type":"string"},{"type":"null"}]},"time_of_day":{"anyOf":[{"type":"string"},{"type":"null"}]},"estimated_duration_seconds":{"anyOf":[{"type":"integer"},{"type":"null"}]},"dramatic_role":{"type":"string"},"conflict":{"type":"object"},"beats":{"type":"array"}}}}},"required":["contract_version","scenes"]}'
    ),
}

_SCENE_PLAN_REPAIR_HINT = '{"scenes":[__PH_0__]}'
_DIALOGUE_REPAIR_HINT = '{"dialogues":[__PH_0__],"stage_directions":[__PH_1__],"scenes":[__PH_2__]}'
_BEAT_CONTRACT_REPAIR_HINT = '{"contract_version":"script-beat-v1","scenes":[__PH_4__]}'

_SCENE_PLAN_MAX_TOKENS = 2048
_DIALOGUE_MAX_TOKENS = 4096
_BEAT_CONTRACT_MAX_TOKENS = 6000
_REPAIR_MAX_TOKENS = 4096
_MAX_DIALOGUE_SCENES = 20
_MAX_EPISODE_SCENES_SAMPLE = 10


def _minify_episode_for_prompt(episode: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(episode, dict):
        return {}

    cloned = dict(episode)
    scenes = cloned.get("scenes")
    if not isinstance(scenes, list) or len(scenes) <= _MAX_EPISODE_SCENES_SAMPLE:
        return cloned

    samples: list[dict[str, Any]] = []
    for raw in scenes[:_MAX_EPISODE_SCENES_SAMPLE]:
        if not isinstance(raw, dict):
            continue
        samples.append(
            {
                "scene_number": raw.get("scene_number"),
                "slug_line": raw.get("slug_line"),
                "summary": raw.get("summary") or raw.get("description"),
            }
        )

    cloned["scenes_total"] = len(scenes)
    cloned["scenes_sample"] = samples
    cloned["scenes"] = []
    return cloned
