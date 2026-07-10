from __future__ import annotations

import json

from app.models.script import Episode, Script, Story
from app.models.task import Task, TaskStatus, TaskType
from app.models.story_structure import Environment
from app.models.user import User
from app.models.virtual_ip import VirtualIP, VirtualIPEnvironment


def _create_script_context(db_session, user: User) -> Script:
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
    )
    db_session.add(script)
    db_session.commit()
    db_session.refresh(script)
    return script


def test_production_canvas_plan_api_reuses_ip_environment_assets(client, db_session):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    virtual_ip = VirtualIP(
        user_id=user.id,
        name="Lin Mei",
        description="Cheng Xu Yuan Shen Bian light comedy heroine",
        is_active=True,
    )
    environment = Environment(
        user_id=user.id,
        name="co-working area",
        category="indoor",
        reference_images=["https://example.test/office.png"],
    )
    db_session.add_all([virtual_ip, environment])
    db_session.commit()
    db_session.refresh(virtual_ip)
    db_session.refresh(environment)
    db_session.add(
        VirtualIPEnvironment(
            user_id=user.id,
            virtual_ip_id=virtual_ip.id,
            virtual_ip_business_id=virtual_ip.business_id,
            environment_id=environment.id,
            environment_business_id=environment.business_id,
            usage_type="main_scene",
            is_default=True,
        )
    )
    db_session.commit()

    response = client.post(
        "/api/v1/production-canvas/plan",
        json={"prompt": "based on Lin Mei Zuo Di 4 Ji，office light comedy"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["skill_manifest"]["version"] == "production_canvas.v1"
    assert payload["skill_manifest"]["skills"][0]["id"] == "brief.compose"
    assert payload["selected_assets"]["virtual_ips"][0]["name"] == "Lin Mei"
    assert payload["selected_assets"]["environments"][0]["name"] == "co-working area"
    assert payload["skill_results"][1]["skill"] == "asset.select"
    script_result = next(
        result
        for result in payload["skill_results"]
        if result["skill"] == "script.generate"
    )
    assert script_result["reuse_targets"][0]["target"].endswith("generate_script_async")
    assert payload["task_id"]
    assert payload["run_id"]
    assert payload["nodes"][1]["skill"] == "asset.select"
    assert payload["nodes"][1]["reuse_targets"][0]["kind"] == "repository"
    task = db_session.get(Task, payload["task_id"])
    assert task is not None
    assert task.business_id == payload["run_id"]
    assert task.task_type == TaskType.TEXT_GENERATION
    assert task.status == TaskStatus.COMPLETED
    assert task.result_file_path == f"production_canvas:{payload['run_id']}"
    params = json.loads(task.parameters)
    assert params["kind"] == "production_canvas_run"
    assert params["prompt"] == "based on Lin Mei Zuo Di 4 Ji，office light comedy"
    assert params["skill_results"][1]["skill"] == "asset.select"
    assert params["selected_assets"]["virtual_ips"][0]["name"] == "Lin Mei"


def test_production_canvas_execute_script_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.script.generation_queue.script_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "based on Lin Mei Zuo Di 4 Ji，office light comedy",
            "skill": "script.generate",
            "episode_id": 123,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "script.generate"
    assert payload["skill_result"]["status"] == "running"
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )
    assert payload["skill_result"]["outputs"]["canvas_run_id"] == (
        "abcdabcdabcdabcdabcdabcdabcdabcd"
    )

    task = db_session.get(Task, payload["task_id"])
    assert task is not None
    assert task.task_type == TaskType.SCRIPT_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    params = json.loads(task.parameters)
    assert params["episode_id"] == 123
    assert params["generation_mode"] == "production"
    assert params["auto_timeline_pipeline"] is True
    assert params["additional_requirements"] == "based on Lin Mei Zuo Di 4 Ji，office light comedy"
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["episode_id"] == 123


def test_production_canvas_execute_script_skill_blocks_without_episode(
    client,
    monkeypatch,
):
    calls = []

    def fake_delay(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr(
        "app.services.script.generation_queue.script_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "based on Lin Mei Zuo Di 4 Ji，office light comedy",
            "skill": "script.generate",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"] is None
    assert payload["task_status"] is None
    assert payload["skill_result"]["status"] == "blocked"
    assert payload["skill_result"]["outputs"]["required_inputs"] == ["episode_id"]
    assert calls == []


def test_production_canvas_execute_storyboard_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    script = _create_script_context(db_session, user)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.storyboard.generation_queue.storyboard_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "continue Xian You script Sheng Cheng Fen Jing",
            "skill": "storyboard.plan",
            "script_id": script.id,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "storyboard.plan"
    assert payload["skill_result"]["status"] == "running"
    assert payload["skill_result"]["outputs"]["script_id"] == script.id
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    assert task.task_type == TaskType.STORYBOARD_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    params = json.loads(task.parameters)
    assert params["script_id"] == script.id
    assert params["use_plan"] is True
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["script_id"] == script.id


def test_production_canvas_execute_timeline_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    script = _create_script_context(db_session, user)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.script.timeline_pipeline_queue.timeline_pipeline_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "Zu Zhuang Xian You script time Xian",
            "skill": "timeline.assemble",
            "script_id": script.id,
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "timeline.assemble"
    assert payload["skill_result"]["status"] == "running"
    assert payload["skill_result"]["outputs"]["script_id"] == script.id
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    assert task.task_type == TaskType.TIMELINE_PIPELINE
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    params = json.loads(task.parameters)
    assert params["script_id"] == script.id
    assert params["overwrite_audio"] is False
    assert params["overwrite_timeline"] is False
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["script_id"] == script.id
