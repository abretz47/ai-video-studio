"""Shared fakes/factories for dynamic prompt tests."""

from __future__ import annotations

import json
from types import SimpleNamespace


class FakeRefContext:
    def __init__(self):
        self.scene_by_number = {}
        self.scene_char_ids = {}
        self.vip_map = {}
        self.name_to_vip_id = {}


def make_script(**overrides):
    story = SimpleNamespace(
        title="Zui Quan",
        genre="Wu Xia",
        theme="Zui Zhong Cang Jin",
        world_building="Jiu Gang Feng Jiu Si Jiang Hu",
    )
    episode = SimpleNamespace(story=story, title="Jiu Guan Ye Dou", episode_number=1)
    defaults = {
        "episode": episode,
        "scenes": [
            {
                "scene_number": 1,
                "location": "outside the tavern",
                "time": "night",
                "description": "protagonist Zui Tai Ying Di",
            }
        ],
        "dialogues": [
            {"scene_number": 1, "content": "Ni He Duo Ba"},
            {"scene_number": 2, "content": "Bie De scene De Hua"},
        ],
        "stage_directions": [{"scene_number": 1, "content": "Di Ren from Liang Ce Bi Jin"}],
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_frames():
    return [
        {
            "scene_number": 1,
            "shot_type": "medium-long shot",
            "camera_movement": "Tui",
            "composition": "San Fen Fa",
            "duration_seconds": 1.0,
            "description": "Zui Bu Ru Chang",
        },
        {
            "scene_number": 1,
            "shot_type": "close-up",
            "camera_movement": "fixed",
            "composition": "Zhong Xin",
            "duration_seconds": 0.9,
            "description": "Yang Tou He Jiu",
        },
    ]


def make_ref_ctx():
    ctx = FakeRefContext()
    scene = SimpleNamespace(id=11)
    ctx.scene_by_number[1] = scene
    ctx.scene_char_ids[11] = {7}
    ctx.vip_map[7] = SimpleNamespace(
        name="A-Long", description="30Sui Wu Zhe，Jiu Bu Yi Duan Da", style_prompt=None
    )
    ctx.name_to_vip_id["A-Long"] = 7
    return ctx


class FakeAIManager:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = 0

    async def generate_text(self, **kwargs):
        self.calls += 1
        payload = self.payloads.pop(0) if self.payloads else None
        if payload is None:
            return SimpleNamespace(success=False, data=None, error="empty")
        return SimpleNamespace(
            success=True,
            data=json.dumps(payload, ensure_ascii=False),
            provider="fake",
            model="fake-model",
        )


def llm_payload(indexes):
    return {
        "frames": [
            {
                "frame_index": idx,
                "image_prompt": f"image prompt {idx}",
                "start_keyframe_prompt": f"start prompt {idx}",
                "end_keyframe_prompt": f"end prompt {idx}",
            }
            for idx in indexes
        ]
    }
