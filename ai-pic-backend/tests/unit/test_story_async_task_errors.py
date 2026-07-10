from __future__ import annotations

from fastapi import HTTPException

from app.api.v1.endpoints.stories.async_tasks import _story_generation_error_message


def test_story_generation_error_message_uses_http_exception_detail() -> None:
    exc = HTTPException(status_code=500, detail="AIstory generate failed")

    assert _story_generation_error_message(exc) == "AIstory generate failed"
