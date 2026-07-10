from app.services.storyboard.grid_storyboard_prompt_bridge import (
    build_clip_storyboard_panels,
    build_grid_storyboard_panels,
    build_grid_storyboard_sheet_prompt,
    build_grid_storyboard_video_prompt,
    grid_layout,
)


def test_grid_layout_clamps_to_supported_panel_counts():
    assert grid_layout(1).panel_count == 2
    assert (grid_layout(1).columns, grid_layout(1).rows) == (2, 1)
    assert grid_layout(4).panel_count == 4
    assert (grid_layout(6).columns, grid_layout(6).rows) == (3, 2)
    assert grid_layout(99).panel_count == 9
    assert (grid_layout(99).columns, grid_layout(99).rows) == (3, 3)


def test_build_grid_storyboard_panels_prefers_timeline_shot_plan_prompts():
    timeline_spec = {
        "tracks": [
            {
                "id": "video-main",
                "kind": "video",
                "clips": [
                    {
                        "id": "clip-1",
                        "scene_id": "scene-1",
                        "beat_id": "beat-1",
                        "start_ms": 0,
                        "end_ms": 2800,
                        "source_refs": {
                            "timeline_shot_plan": {
                                "shot_id": "shot-1",
                                "visual_prompt": "Lin Wan Zhan in rainy night doorway，Ni Hong Fan Guang，medium shot",
                                "video_prompt": "camera Huan Man Tui Jin，Yu Shui Luo in Ta Jian Tou",
                                "direction_anchor": "Chao Xiang rainy night doorway lonely search",
                                "aesthetic_reference": "IMAX film, Panavision C lens",
                                "composition_geometry": "Lin Wan in Zuo San Fen Xian，Men Kuang Qie Fen You Ce Fu Kong Jian",
                                "motion_timeline": [
                                    {"at_ms": 0, "action": "Lin Wan Ting in doorway"},
                                    {"at_ms": 1400, "action": "Yu Shui Luo in Jian Tou"},
                                    {"at_ms": 2800, "action": "Ta Tai Tou Kan Xiang Men Nei"},
                                ],
                                "emotional_landing": "Leng Yu in Ke Zhi lonely",
                            }
                        },
                        "ai_prompt": "fallback image prompt",
                    }
                ],
            }
        ]
    }

    panels = build_grid_storyboard_panels(timeline_spec, panel_count=2)

    assert len(panels) == 1
    panel = panels[0]
    assert panel["panel_index"] == 1
    assert panel["row"] == 1
    assert panel["column"] == 1
    assert panel["clip_id"] == "clip-1"
    assert panel["visual_prompt"] == "Lin Wan Zhan in rainy night doorway，Ni Hong Fan Guang，medium shot"
    assert panel["video_prompt"] == "camera Huan Man Tui Jin，Yu Shui Luo in Ta Jian Tou"
    assert panel["direction_anchor"] == "Chao Xiang rainy night doorway lonely search"
    assert panel["aesthetic_reference"] == "IMAX film, Panavision C lens"
    assert panel["composition_geometry"] == "Lin Wan in Zuo San Fen Xian，Men Kuang Qie Fen You Ce Fu Kong Jian"
    assert panel["motion_timeline"][2]["at_ms"] == 2800
    assert panel["emotional_landing"] == "Leng Yu in Ke Zhi lonely"
    assert "fallback image prompt" not in panel["storyboard_panel_prompt"]
    assert "Panel 1" in panel["storyboard_panel_prompt"]
    assert "Men Kuang Qie Fen You Ce Fu Kong Jian" in panel["storyboard_panel_prompt"]


def test_build_grid_storyboard_panels_falls_back_to_clip_text():
    timeline_spec = {
        "tracks": [
            {
                "kind": "video",
                "clips": [
                    {
                        "id": "clip-2",
                        "start_ms": 1000,
                        "end_ms": 4000,
                        "text": "Ta Tui Kai conference room Da Men，Zhong Ren Hui Tou。",
                    }
                ],
            }
        ]
    }

    panels = build_grid_storyboard_panels(timeline_spec, panel_count=4)

    assert panels[0]["visual_prompt"] == "Ta Tui Kai conference room Da Men，Zhong Ren Hui Tou。"
    assert panels[0]["video_prompt"] == "Ta Tui Kai conference room Da Men，Zhong Ren Hui Tou。"
    assert panels[0]["duration_ms"] == 3000


def test_build_clip_storyboard_panels_diversifies_clip_text_fallback():
    clip = {
        "clip_id": "video_scene_91_beat_4003_013",
        "scene_id": 91,
        "beat_id": 4003,
        "start_ms": 36260,
        "end_ms": 45444,
        "text": "Chu Fang and Kai Fang Shi Can Ting Xiang Lian。Old Guai and A Gai Er Zhan in Zhong Dao Tai Pang。",
        "source_refs": {},
    }

    panels = build_clip_storyboard_panels(clip, panel_count=4)

    assert len(panels) == 4
    visual_prompts = [panel["visual_prompt"] for panel in panels]
    assert len(set(visual_prompts)) == 4
    assert all("Key moment" not in prompt for prompt in visual_prompts)
    assert "Opening frame" in visual_prompts[0]
    assert "Interaction frame" in visual_prompts[1]
    assert "Detail frame" in visual_prompts[2]
    assert "Closing frame" in visual_prompts[3]
    assert panels[0]["motion_timeline"][0]["at_ms"] == 36260
    assert panels[3]["motion_timeline"][0]["at_ms"] > panels[0]["motion_timeline"][0]["at_ms"]
    assert len({panel["composition_geometry"] for panel in panels}) == 4


def test_grid_sheet_and_video_prompts_constrain_text_and_panel_scope():
    panels = [
        {
            "panel_index": 1,
            "clip_id": "clip-1",
            "visual_prompt": "Lin Wan Zhan in rainy night doorway，Ni Hong Fan Guang，medium shot",
            "video_prompt": "camera Huan Man Tui Jin，Yu Shui Luo in Ta Jian Tou",
            "direction_anchor": "Chao Xiang rainy night doorway lonely search",
            "aesthetic_reference": "IMAX film, Panavision C lens",
            "composition_geometry": "Lin Wan in Zuo San Fen Xian，Men Kuang Qie Fen You Ce Fu Kong Jian",
            "motion_timeline": [
                {"at_ms": 0, "action": "Lin Wan Ting in doorway"},
                {"at_ms": 2800, "action": "Ta Tai Tou Kan Xiang Men Nei"},
            ],
            "emotional_landing": "Leng Yu in Ke Zhi lonely",
        },
        {
            "panel_index": 2,
            "clip_id": "clip-2",
            "visual_prompt": "Chen Zhe Zuo Zai Che INT，Ce Lian be phone Ping Zhao Liang",
            "video_prompt": "The camera remains still, capturing only his hesitant expression",
        },
    ]

    sheet_prompt = build_grid_storyboard_sheet_prompt(
        panels,
        style="vertical short-drama, cinematic realism",
    )
    video_prompt = build_grid_storyboard_video_prompt(panels[1])

    assert "2-panel" in sheet_prompt
    assert "2x1" in sheet_prompt
    assert "panel numbers" in sheet_prompt
    assert "No subtitles" in sheet_prompt
    assert "Lin Wan Zhan in rainy night doorway" in sheet_prompt
    assert "IMAX film" in sheet_prompt
    assert "Men Kuang Qie Fen You Ce Fu Kong Jian" in sheet_prompt
    assert "0ms Lin Wan Ting in doorway" in sheet_prompt
    assert "Leng Yu in Ke Zhi lonely" in sheet_prompt
    assert "Use panel 2 only" in video_prompt
    assert "clip-2" in video_prompt
    assert "Generate only this shot" in video_prompt
    assert "camera keep Jing Zhi" in video_prompt
