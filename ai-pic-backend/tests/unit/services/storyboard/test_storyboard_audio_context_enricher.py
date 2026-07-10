from __future__ import annotations

from app.models.story_structure import Environment, Scene
from app.services.storyboard.storyboard_audio_context_enricher import (
    enrich_storyboard_frames_with_story_context,
)
from tests.factories import (
    EpisodeFactory,
    ScriptFactory,
    StoryCharacterFactory,
    StoryFactory,
    VirtualIPFactory,
    setup_factories,
)


def test_audio_timeline_storyboard_enricher_injects_cards_and_reference_images(
    db_session,
) -> None:
    setup_factories(db_session)

    story = StoryFactory()
    episode = EpisodeFactory(story=story)
    script = ScriptFactory(episode=episode)

    vip_a = VirtualIPFactory(
        name="short drama heroine-Lin Wan-2026-01-30T00-00-00Z",
        description="25Suifemale，Hei Chang Fa，Mi Se Mao Yi，Bai Se Duan Xue。",
        style_prompt="urban Xie Shi style，Mi Se Zhen Zhi Shan，Jian Jie Zhuang Rong。",
        default_avatar_url="http://example.com/lw.png",
        style_reference_images=[],
    )
    vip_b = VirtualIPFactory(
        name="Chen Zhe",
        description="30Sui Nan Xing，Duan Fa，Shen Se Jia Ke。",
        style_prompt="urban Xie Shi style，Shen Se Niu Zai Jia Ke。",
        default_avatar_url="http://example.com/cz.png",
        style_reference_images=[],
    )
    StoryCharacterFactory(
        story=story, virtual_ip=vip_a, character_name="Lin Wan", importance=5
    )
    StoryCharacterFactory(
        story=story, virtual_ip=vip_b, character_name="Chen Zhe", importance=4
    )

    env = Environment(
        name="Gong Yu living room",
        category="indoor",
        description="modern Gong Yu living room",
        reference_images=["http://example.com/env.png"],
    )
    db_session.add(env)
    db_session.flush()

    scene = Scene(
        script_id=script.id,
        scene_number="1",
        slug_line="INT. APARTMENT - NIGHT",
        location="Shang Hai",
        time_of_day="night",
        environment_id=env.id,
    )
    db_session.add(scene)
    db_session.commit()

    frames = [
        {
            "frame_id": "f1",
            "frame_number": 1,
            "scene_id": int(scene.id),
            "scene_number": 1,
            "characters": ["Lin Wan", "Chen Zhe", "voiceover"],
            "prompt_description": "main subject: vertical short drama Dan camera，Lin Wan Zheng Zai Kai Kou Shuo Hua。Biao Yan action: Yan Shen Zhui Wen Dui Fang。Jin Zhi Xiang: Dan Fu frame，no subtitles，Wu Ke Du Wen Zi。",
        }
    ]

    enrich_storyboard_frames_with_story_context(
        db_session,
        story_id=story.id,
        script_id=script.id,
        frames=frames,
        max_reference_images=3,
        max_character_cards=3,
    )

    assert frames[0]["characters"] == ["Lin Wan", "Chen Zhe"]
    assert frames[0]["reference_images"] == [
        "http://example.com/lw.png",
        "http://example.com/cz.png",
        "http://example.com/env.png",
    ]
    assert "main subject:" in frames[0]["prompt_description"]
    assert "character Yi Zhi Xing:" in frames[0]["prompt_description"]
    assert "Lin Wan" in frames[0]["prompt_description"]
    assert "Chen Zhe" in frames[0]["prompt_description"]
    assert "environment Mao Dian:" in frames[0]["prompt_description"]
    assert "Gong Yu living room" in frames[0]["prompt_description"]
    assert "camera Lian Xu Xing Bu Chong:" in frames[0]["prompt_description"]


def test_audio_timeline_storyboard_enricher_does_not_override_manual_reference_images(
    db_session,
) -> None:
    setup_factories(db_session)

    story = StoryFactory()
    episode = EpisodeFactory(story=story)
    script = ScriptFactory(episode=episode)

    vip_a = VirtualIPFactory(
        name="Lin Wan",
        default_avatar_url="http://example.com/lw.png",
        style_reference_images=[],
    )
    StoryCharacterFactory(story=story, virtual_ip=vip_a, character_name="Lin Wan")

    frames = [
        {
            "frame_id": "f1",
            "frame_number": 1,
            "scene_id": 1,
            "scene_number": 1,
            "characters": ["Lin Wan"],
            "prompt_description": "main subject: vertical short drama Dan camera，Lin Wan Zheng Zai Kai Kou Shuo Hua。",
            "reference_images": ["http://example.com/manual.png"],
        }
    ]

    enrich_storyboard_frames_with_story_context(
        db_session,
        story_id=story.id,
        script_id=script.id,
        frames=frames,
        max_reference_images=3,
        max_character_cards=3,
    )

    assert frames[0]["reference_images"] == ["http://example.com/manual.png"]
    assert "character Yi Zhi Xing:" in frames[0]["prompt_description"]
