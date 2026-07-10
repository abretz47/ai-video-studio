"""Shared utilities for storyboard endpoints."""

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.script import Episode, Script, Story
from app.models.user import User


def _not_deleted(query, model):
    """Filter out soft-deleted records if model has is_deleted field."""
    if hasattr(model, "is_deleted"):
        return query.filter(model.is_deleted.is_(False))
    return query


def get_script_with_auth(
    db: Session,
    script_id: int,
    current_user: User,
    require_ownership: bool = True,
) -> Script:
    """Get script with authorization check.

    Args:
        db: Database session
        script_id: Script ID to retrieve
        current_user: Current authenticated user
        require_ownership: If True, non-admin users must own the script

    Returns:
        Script instance

    Raises:
        HTTPException: If script not found or unauthorized
    """
    script_query = (
        _not_deleted(db.query(Script), Script)
        .join(Episode, Script.episode_id == Episode.id)
        .join(Story, Episode.story_id == Story.id)
        .filter(Script.id == script_id)
    )

    if require_ownership and not (current_user.is_admin or current_user.is_superuser):
        script_query = script_query.filter(Story.user_id == current_user.id)

    script = script_query.first()
    if not script:
        raise HTTPException(status_code=404, detail="Script does not exist")

    return script


def now_iso() -> str:
    """Get current UTC time as ISO string."""
    return datetime.utcnow().isoformat()


def to_int(value: Any) -> Optional[int]:
    """Safely convert value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def coerce_uuid(value: Any) -> str:
    """Ensure value is a valid UUID string, generate new if invalid."""
    if not value:
        return str(uuid4())
    try:
        return str(UUID(str(value)))
    except Exception:
        return str(uuid4())


def ensure_iso_datetime(value: Any, fallback: str) -> str:
    """Ensure value is ISO datetime string."""
    if value is None:
        return fallback
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        return datetime.fromisoformat(str(value)).isoformat()
    except Exception:
        return fallback


def abs_url(url: str) -> str:
    """Ensure URL is absolute with scheme."""
    if not url:
        return ""
    if url.startswith("//"):
        return f"https:{url}"
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def enforce_storyboard_variety(frames: List[dict]) -> List[dict]:
    """Apply cinematic variety rules to storyboard frames.

    Ensures visual diversity across shots by cycling through:
    - Shot types: Wide shot, Medium shot, Close shot, Close-up
    - Camera movements: Static, Push, Pull, Pan, Move, Follow, Zoom
    - Compositions: Rule of thirds, Symmetry, Foreground/background layering, Diagonal composition, Central symmetry

    Args:
        frames: List of frame dictionaries

    Returns:
        Modified frames with enforced variety
    """
    shot_types = ["Wide shot", "Medium shot", "Close shot", "Close-up"]
    camera_movements = ["Static", "Push", "Pull", "Pan", "Move", "Follow", "Zoom"]
    compositions = ["Rule of thirds", "Symmetry", "Foreground/background layering", "Diagonal composition", "Central symmetry"]

    for i, frame in enumerate(frames):
        variety_index = i % 4

        # Apply variety based on position
        frame["shot_type"] = shot_types[variety_index % len(shot_types)]
        frame["camera_movement"] = camera_movements[
            variety_index % len(camera_movements)
        ]
        frame["composition"] = compositions[variety_index % len(compositions)]

        # Adjust duration for variety
        base_duration = frame.get("duration_seconds", 3)
        if isinstance(base_duration, (int, float)):
            frame["duration_seconds"] = max(2, min(10, base_duration + (variety_index - 2)))

        # Update description with camera movement emphasis
        desc = frame.get("description", "")
        movement = frame["camera_movement"]
        if movement != "Static" and movement not in desc:
            frame["description"] = f"{desc} ({movement} shot)"

        # Sync ai_prompt with description if needed
        if not frame.get("ai_prompt"):
            frame["ai_prompt"] = frame.get("description", "")

    return frames


def build_reference_image_context(
    labeled_references: Optional[List[dict]],
) -> str:
    """Generate human-readable context for reference images.

    Args:
        labeled_references: List of dicts with keys: url, label, type

    Returns:
        Formatted markdown description of reference images
    """
    if not labeled_references:
        return ""

    lines = ["[Reference image notes]"]
    type_labels = {
        "character": "Character",
        "environment": "Scene environment",
        "primary": "Primary style/composition",
        "other": "Supplementary reference",
    }

    for i, ref in enumerate(labeled_references, 1):
        ref_type = ref.get("type", "other")
        label = ref.get("label", "")
        type_desc = type_labels.get(ref_type, "Reference")

        if ref_type == "character" and label:
            lines.append(f"- Image {i} is a reference portrayal of character '{label}'")
        elif ref_type == "environment":
            lines.append(f"- Image {i} is a {type_desc} reference")
        else:
            desc = f"{type_desc}"
            if label:
                desc += f"（{label}）"
            lines.append(f"- Image {i} is {desc}")

    return "\n".join(lines)
