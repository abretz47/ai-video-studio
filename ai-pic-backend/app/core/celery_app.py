"""
Celery application configuration

Yong Yu unified process Hou Tai Ren Wu(story/episode/script Sheng Cheng Deng), You Du Li worker Jin Cheng run.
"""

import sys
from datetime import timedelta
from importlib import import_module

from app.core.config import settings
from celery import Celery


def _running_under_pytest() -> bool:
    # Avoid connecting to external Redis in unit/script tests.
    return "pytest" in sys.modules


def _task_always_eager() -> bool:
    # pytest and lite mode all Zou eager, avoid Yi Lai Wai Bu Redis/Du Li worker.
    return _running_under_pytest() or bool(
        getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False)
    )


def _get_broker_url() -> str:
    # default Fu Yong REDIS_URL, subsequent Ru Xu Qu Fen can Kuo Zhan Dan Du CELERY_BROKER_URL
    if _task_always_eager():
        return "memory://"
    return getattr(settings, "REDIS_URL", "redis://localhost:6379/0")


def _get_backend_url() -> str:
    # Celery does not support "memory://" as result backend.
    if _task_always_eager():
        return "cache+memory://"
    return getattr(settings, "REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery(
    "ai_video_studio",
    broker=_get_broker_url(),
    backend=_get_backend_url(),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    # Default timeout: 30 min hard limit, 25 min soft limit (raises SoftTimeLimitExceeded)
    task_time_limit=1800,
    task_soft_time_limit=1500,
    beat_schedule={
        "poll-video-generation-tasks": {
            "task": "tasks.video_generation_poll",
            "schedule": timedelta(seconds=30),
            "args": (50,),
        },
    },
    task_always_eager=_task_always_eager(),
    task_store_eager_result=False,
    task_eager_propagates=bool(getattr(settings, "CELERY_TASK_EAGER_PROPAGATES", True)),
)

# Ensure all tasks are registered after Celery application initialization
# Ren Wu Ding Yi Wei Yu app.services.task_worker Deng module in, Shi Yong Xian Shi name(for example "tasks.virtual_ip_image_generate")
# through Dao Ru Gai module complete Zhu Ce, avoid worker Qi Dong when Chu Xian KeyError.
for _task_module in (
    "app.services.task_worker",
    "app.services.task_worker_scene_grid",
    "app.services.task_worker_script_quality",
    "app.services.task_worker_storyboard_media",
    "app.services.task_worker_timeline_keyframes",
    "app.services.task_worker_timeline_render",
    "app.services.task_worker_timeline_rework",
):
    import_module(_task_module)
