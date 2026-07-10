import json
import logging

from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.task import TASK_STATUS_TRANSITIONS, Task, TaskStatus, TaskType
from app.models.user import User
from app.schemas.task import TaskCreate, TaskList, TaskResponse, TaskUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


def _not_deleted(query, model):
    return query.filter(model.is_deleted.is_(False))




def _serialize_task(task: Task) -> TaskResponse:
    """Serialize ORM task objects into response models and parse parameters as dicts"""
    params = None
    if task.parameters:
        try:
            params = json.loads(task.parameters)
        except Exception:
            params = None

    progress_detail = task.description or None
    if task.status in {TaskStatus.FAILED, TaskStatus.CANCELLED} and task.error_message:
        progress_detail = task.error_message

    return TaskResponse(
        id=task.id,
        business_id=getattr(task, "business_id", None),
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        prompt=task.prompt,
        parameters=params,
        status=task.status,
        result_file_path=task.result_file_path,
        error_message=task.error_message,
        user_id=task.user_id,
        target_business_id=getattr(task, "target_business_id", None),
        progress_detail=progress_detail,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new task"""
    # Convert parameters to a JSON string
    parameters_json = None
    if task_data.parameters:
        parameters_json = json.dumps(task_data.parameters)

    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        prompt=task_data.prompt,
        parameters=parameters_json,
        user_id=current_user.id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return _serialize_task(db_task)


@router.get("/", response_model=TaskList)
def get_tasks(
    skip: int = 0,
    limit: int = 20,
    status_filter: TaskStatus = None,
    task_type: TaskType = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the user's task list"""
    query = _not_deleted(db.query(Task), Task).filter(Task.user_id == current_user.id)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    if task_type:
        query = query.filter(Task.task_type == task_type)

    total = query.count()
    tasks = query.order_by(Task.id.desc()).offset(skip).limit(limit).all()

    return TaskList(
        tasks=[_serialize_task(t) for t in tasks],
        total=total,
        page=skip // limit + 1,
        size=limit,
    )


@router.get("", response_model=TaskList, include_in_schema=False)
def get_tasks_no_slash(
    skip: int = 0,
    limit: int = 20,
    status_filter: TaskStatus = None,
    task_type: TaskType = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Support /api/v1/tasks requests without a trailing slash to avoid FastAPI returning 307 redirects.

    Internally reuse get_tasks pagination and filtering logic directly.
    """
    return get_tasks(
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        task_type=task_type,
        db=db,
        current_user=current_user,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get specific task information"""
    task = (
        _not_deleted(db.query(Task), Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist")

    return _serialize_task(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update task information"""
    task = (
        _not_deleted(db.query(Task), Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist")

    # Update task information
    update_data = task_data.model_dump(exclude_unset=True)

    # Validate status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        allowed = TASK_STATUS_TRANSITIONS.get(task.status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Transition from {task.status.value} to {new_status.value} is not allowed, "
                    f"allowed target states: {[s.value for s in allowed] or 'none'}"
                ),
            )

    # If parameters are updated, convert them to a JSON string
    if "parameters" in update_data:
        update_data["parameters"] = json.dumps(update_data["parameters"])

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # Keep response consistent with other endpoints (parameters as dict)
    return _serialize_task(task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete task"""
    task = (
        _not_deleted(db.query(Task), Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist")

    task.soft_delete(user_id=current_user.id, reason="user delete")
    db.commit()

    return {"message": "Task deleted"}


def _dispatch_celery_task(task: Task, user_id: int) -> bool:
    """Dispatch a Task to the matching Celery worker. Returns True on success."""
    params = {}
    if task.parameters:
        try:
            params = json.loads(task.parameters)
        except Exception:
            params = {}

    from app.services.task_worker import (
        episode_generate_task,
        script_dialogue_audio_generate_task,
        script_generate_task,
        script_regenerate_task,
        storyboard_generate_task,
        story_generate_task,
        story_novel_generate_task,
        timeline_pipeline_generate_task,
    )
    from app.services.task_worker_assets import (
        environment_image_generate_task,
        environment_image_variant_task,
        virtual_ip_image_generate_task,
        virtual_ip_image_variant_task,
    )
    from app.services.task_worker_storyboard_media import (
        storyboard_image_generate_task,
        storyboard_video_generate_task,
    )

    dispatch_map = {
        TaskType.STORY_GENERATION: story_generate_task,
        TaskType.TEXT_GENERATION: story_novel_generate_task,
        TaskType.EPISODE_GENERATION: episode_generate_task,
        TaskType.SCRIPT_GENERATION: script_generate_task,
        TaskType.SCRIPT_REVIEW: script_regenerate_task,
        TaskType.DIALOGUE_AUDIO_GENERATION: script_dialogue_audio_generate_task,
        TaskType.STORYBOARD_GENERATION: storyboard_generate_task,
        TaskType.TIMELINE_PIPELINE: timeline_pipeline_generate_task,
        TaskType.VIRTUAL_IP_IMAGE_GENERATION: virtual_ip_image_generate_task,
        TaskType.VIRTUAL_IP_IMAGE_VARIANT_GENERATION: virtual_ip_image_variant_task,
        TaskType.ENVIRONMENT_IMAGE_GENERATION: environment_image_generate_task,
        TaskType.ENVIRONMENT_IMAGE_VARIANT_GENERATION: environment_image_variant_task,
        TaskType.STORYBOARD_IMAGE_GENERATION: storyboard_image_generate_task,
        TaskType.VIDEO_GENERATION: storyboard_video_generate_task,
    }

    celery_task = dispatch_map.get(task.task_type)
    if celery_task is None:
        return False

    celery_task.delay(task.id, params, user_id)
    return True


@router.post("/{task_id}/start")
def start_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start executing task"""
    task = (
        _not_deleted(db.query(Task), Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist")

    if task.status not in (TaskStatus.PENDING, TaskStatus.FAILED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Current status ({task.status.value}) does not allow execution to start",
        )

    dispatched = _dispatch_celery_task(task, current_user.id)
    if not dispatched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task type {task.task_type.value} does not currently support manual start",
        )

    task.status = TaskStatus.PROCESSING
    task.error_message = None
    db.commit()
    logger.info("Task %s dispatched to Celery (type=%s)", task_id, task.task_type.value)

    return {"message": "Task execution started", "task_id": task_id}
