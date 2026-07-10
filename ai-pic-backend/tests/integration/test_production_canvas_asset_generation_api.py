from __future__ import annotations

import json

from app.models.task import Task, TaskType
from app.models.story_structure import Environment
from app.models.user import User
from app.models.virtual_ip import VirtualIP


def test_production_canvas_execute_virtual_ip_image_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    virtual_ip = VirtualIP(
        user_id=user.id,
        name="Lin Mei",
        description="Cheng Xu Yuan Shen Bian light comedy heroine",
        is_active=True,
    )
    db_session.add(virtual_ip)
    db_session.commit()
    db_session.refresh(virtual_ip)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.task_worker_assets.virtual_ip_image_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "Gei Lin Mei generate character image",
            "skill": "virtual_ip.image",
            "virtual_ip_id": virtual_ip.id,
            "model": "codex:gpt-image-2",
            "aspect_ratio": "1:1",
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "virtual_ip.image"
    assert payload["skill_result"]["status"] == "running"
    assert payload["skill_result"]["outputs"]["virtual_ip_id"] == virtual_ip.id
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    assert task.task_type == TaskType.VIRTUAL_IP_IMAGE_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    params = json.loads(task.parameters)
    assert params["virtual_ip_id"] == virtual_ip.id
    assert params["model"] == "codex:gpt-image-2"
    assert params["aspect_ratio"] == "1:1"
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["virtual_ip_id"] == virtual_ip.id


def test_production_canvas_execute_environment_image_skill_dispatches_existing_task(
    client,
    db_session,
    monkeypatch,
):
    user = db_session.query(User).filter(User.username == "test_admin").first()
    environment = Environment(
        user_id=user.id,
        name="co-working area",
        category="indoor",
        description="Ming Liang office scene",
    )
    db_session.add(environment)
    db_session.commit()
    db_session.refresh(environment)
    dispatched = {}

    def fake_delay(task_id, params, user_id):
        dispatched["task_id"] = task_id
        dispatched["params"] = params
        dispatched["user_id"] = user_id

    monkeypatch.setattr(
        "app.services.task_worker_assets.environment_image_generate_task.delay",
        fake_delay,
    )

    response = client.post(
        "/api/v1/production-canvas/execute",
        json={
            "prompt": "generate Gong Xiang Ban Gong Qu environment image",
            "skill": "environment.image",
            "environment_id": environment.id,
            "model": "codex:gpt-image-2",
            "aspect_ratio": "16:9",
            "run_id": "abcdabcdabcdabcdabcdabcdabcdabcd",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["task_id"]
    assert payload["task_status"] == "pending"
    assert payload["skill_result"]["skill"] == "environment.image"
    assert payload["skill_result"]["status"] == "running"
    assert payload["skill_result"]["outputs"]["environment_id"] == environment.id
    assert (
        payload["skill_result"]["outputs"]["dispatched_task_id"] == payload["task_id"]
    )

    task = db_session.get(Task, payload["task_id"])
    assert task.task_type == TaskType.ENVIRONMENT_IMAGE_GENERATION
    assert task.target_business_id == "abcdabcdabcdabcdabcdabcdabcdabcd"
    params = json.loads(task.parameters)
    assert params["env_id"] == environment.id
    assert params["model"] == "codex:gpt-image-2"
    assert params["aspect_ratio"] == "16:9"
    assert dispatched["task_id"] == task.id
    assert dispatched["params"]["env_id"] == environment.id
