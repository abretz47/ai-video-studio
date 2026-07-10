from __future__ import annotations

import json

from app.models.script import Episode, Script, Story
from app.models.task import Task, TaskStatus, TaskType
from app.models.user import User


def _storyboard_frames() -> list[dict]:
    return [
        {
            "scene_number": 1,
            "description": "Lin Mei in Gong Xiang Ban Gong Qu Tiao Shi Zhi Neng Yin Xiang",
            "ai_prompt": "Gong Xiang Ban Gong Qu Li，Nian Qing Cheng Xu Yuan Zheng Zai Tiao Shi Zhi Neng Yin Xiang",
            "duration_seconds": 3.2,
            "reference_images": ["https://example.com/office-ref.png"],
            "image_url": "https://example.com/start-frame.png",
            "end_image_url": "https://example.com/end-frame.png",
        },
        {
            "scene_number": 1,
            "description": "Cheng Xu Yuan discover Yin Xiang start Tu Cao Dai Ma",
            "ai_prompt": "Cheng Xu Yuan Cuo E Di Kan Xiang Hui Shuo Hua Zhi Neng Yin Xiang",
            "duration_seconds": 2.8,
            "reference_images": ["https://example.com/device-ref.png"],
            "image_url": "https://example.com/start-frame-2.png",
        },
    ]


def _create_storyboard_script(db_session, user: User) -> Script:
    story = Story(user_id=user.id, title="Cheng Xu Yuan light comedy", genre="comedy")
    db_session.add(story)
    db_session.commit()
    episode = Episode(story_id=story.id, episode_number=4, title="Zhi Neng Sheng Huo Ru Men")
    db_session.add(episode)
    db_session.commit()
    script = Script(
        episode_id=episode.id,
        title="Di 4 Ji script",
        content="office light comedy",
        extra_metadata={"storyboard": {"frames": _storyboard_frames()}},
    )
    db_session.add(script)
    db_session.commit()
    db_session.refresh(script)
    return script


def test_production_canvas_execute_image_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    script = _create_storyboard_script(db_session, user)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.storyboard.storyboard_image_autogen."
        "storyboard_image_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "generate Xian You storyboard Tu Pian Hou Xuan",
            "skill": "image.candidates",
            "script_id": script.id,
            "frame_indexes": [1],
            "model": "codex:gpt-image-2",
            "aspect_ratio": "16:9",
            "require_reference_images": False,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "image.candidates"
    assert payload["skill_result"]["outputs"]["queued_frame_count"] == 1
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    params = json.loads(task.parameters)
    assert task.task_type == TaskType.STORYBOARD_IMAGE_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    assert params["script_id"] == script.id
    assert params["frame_indexes"] == [1]
    assert params["model"] == "codex:gpt-image-2"
    assert params["aspect_ratio"] == "16:9"
    assert params["require_reference_images"] is False
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["script_id"] == script.id


def test_production_canvas_execute_video_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    script = _create_storyboard_script(db_session, user)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.storyboard.video_generation_queue."
        "storyboard_video_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "generate Xian You storyboard video Hou Xuan",
            "skill": "video.candidates",
            "script_id": script.id,
            "frame_indexes": [1],
            "model": "minimax:video-01",
            "duration": 6,
            "fps": 30,
            "resolution": "1080p",
            "ratio": "16:9",
            "camera_fixed": True,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "video.candidates"
    assert payload["skill_result"]["outputs"]["frame_count"] == 2
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    params = json.loads(task.parameters)
    assert task.task_type == TaskType.VIDEO_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    assert params["script_id"] == script.id
    assert params["frame_indexes"] == [1]
    assert params["model"] == "minimax:video-01"
    assert params["duration"] == 6
    assert params["fps"] == 30
    assert params["resolution"] == "1080p"
    assert params["ratio"] == "16:9"
    assert params["camera_fixed"] is True
    assert params["return_last_frame"] is True
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["script_id"] == script.id


def test_production_canvas_execute_report_skill_summarizes_existing_task(
    client,
    db_session,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    task = Task(
        title="Sheng Chan Hua Bu Zheng Ti create",
        description="Production canvas skill run",
        task_type=TaskType.TEXT_GENERATION,
        status=TaskStatus.COMPLETED,
        prompt="based on Lin Mei Zuo Di 4 Ji",
        parameters=json.dumps(
            {
                "kind": "production_canvas_run",
                "prompt": "based on Lin Mei Zuo Di 4 Ji",
                "selected_assets": {"virtual_ips": [{"name": "Lin Mei"}]},
            },
            ensure_ascii=False,
        ),
        result_file_path="production_canvas:abcdabcdabcdabcdabcdabcdabcdabcd",
        user_id=user.id,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "Hui Zong Zhe Ci Hua Bu Zhi Xing Zheng Ju",
            "skill": "report.summarize",
            "task_id": task.id,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"] == task.id
    assert payload["task_status"] == "completed"
    assert payload["skill_result"]["skill"] == "report.summarize"
    assert payload["skill_result"]["status"] == "review"
    assert payload["skill_result"]["outputs"]["task_type"] == "text_generation"
    assert payload["skill_result"]["outputs"]["source_kind"] == (
        "production_canvas_run"
    )
    assert "Sheng Chan Hua Bu Zheng Ti create" in payload["skill_result"]["detail"]
