"""Volcengine video generation module."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

import httpx

from ..base import AIModelType, AIResponse, AITaskType
from .video_request import _normalize_model, build_video_request, has_visual_reference
from .video_response import extract_error, extract_output_urls, extract_task_id

logger = logging.getLogger(__name__)

__all__ = [
    "_normalize_model",
    "generate_video",
    "poll_task_status",
]


async def poll_task_status(
    client: httpx.AsyncClient,
    base_url: str,
    task_id: str,
    max_attempts: int = 60,
    delay: int = 3,
) -> Dict[str, Any]:
    """Poll Volcengine content generation task status."""
    last_error: str | None = None

    for attempt in range(max_attempts):
        try:
            response = await client.get(
                f"{base_url}/contents/generations/tasks/{task_id}",
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            if not isinstance(data, dict):
                raise RuntimeError(
                    f"Huo Shan Yin Qing task {task_id} Fan Hui Fei dict Xiang Ying: {type(data).__name__}"
                )

            status = str(data.get("status") or "").lower()
            if status == "succeeded":
                return data
            if status in {"failed", "canceled", "cancelled", "expired"}:
                err_msg = extract_error(data) or f"task status: {status}"
                raise RuntimeError(f"Huo Shan Yin Qing task failed: {err_msg}")
            if status in {"queued", "running", "processing", "pending"}:
                await asyncio.sleep(delay)
                continue

            logger.warning("Volcengine Yin Qing Ren Wu %s unknown status: %s", task_id, status)
            raise RuntimeError(f"Huo Shan Yin Qing task unknown status: {status}")
        except RuntimeError:
            raise
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "Lun Xun Volcengine Yin Qing Ren Wu status failed (Chang Shi %d/%d): %s",
                attempt + 1,
                max_attempts,
                exc,
            )
            await asyncio.sleep(delay)

    suffix = f", Zui Hou error: {last_error}" if last_error else ""
    raise RuntimeError(
        f"Huo Shan Yin Qing task {task_id} Lun Xun Chao Shi ({max_attempts * delay}s){suffix}"
    )


async def generate_video(
    client: httpx.AsyncClient,
    base_url: str,
    provider_name: str,
    prompt: Optional[str] = None,
    image_url: Optional[str] = None,
    model: Optional[str] = None,
    duration: int = 5,
    fps: int = 24,
    resolution: str = "720p",
    end_image_url: Optional[str] = None,
    ratio: Optional[str] = None,
    watermark: Optional[bool] = None,
    seed: Optional[int] = None,
    camera_fixed: Optional[bool] = None,
    service_tier: Optional[str] = None,
    execution_expires_after: Optional[int] = None,
    return_last_frame: Optional[bool] = None,
    format_error: Callable = str,
    **kwargs: Any,
) -> AIResponse:
    """Generate video using Volcengine Ark Video Generation API."""
    try:
        ark_model, model_type, request_data, resolved = build_video_request(
            prompt=prompt,
            image_url=image_url,
            end_image_url=end_image_url,
            model=model,
            duration=duration,
            fps=fps,
            resolution=resolution,
            ratio=ratio,
            watermark=watermark,
            seed=seed,
            camera_fixed=camera_fixed,
            service_tier=service_tier,
            execution_expires_after=execution_expires_after,
            return_last_frame=return_last_frame,
            extra_kwargs=kwargs,
        )
        create_resp = await client.post(
            f"{base_url}/contents/generations/tasks",
            json=request_data,
        )
        create_resp.raise_for_status()
        create_data = create_resp.json() if create_resp.content else {}

        error_message = extract_error(create_data)
        if error_message:
            return _failure_response(
                f"Huo Shan Yin Qing video generate error: {error_message}",
                provider_name,
                ark_model,
                model_type,
            )

        task_id = extract_task_id(create_data)
        if not task_id:
            return _failure_response(
                "Volcengine Yin Qing video Sheng Cheng response missing Ren WuID",
                provider_name,
                ark_model,
                model_type,
                metadata={"raw": create_data},
            )

        result = await poll_task_status(
            client,
            base_url,
            task_id,
            max_attempts=(600 if model_type == AIModelType.IMAGE_TO_VIDEO else 120),
            delay=3,
        )
        urls = extract_output_urls(result)
        if not urls.get("video_url"):
            return _failure_response(
                "Volcengine Yin Qing video Sheng Cheng successful Dan not return videoURL",
                provider_name,
                ark_model,
                model_type,
                metadata={"task_id": task_id, "raw": result},
            )

        return AIResponse(
            success=True,
            data={**urls, "duration": resolved["duration"]},
            provider=provider_name,
            model=ark_model,
            task_type=AITaskType.VIDEO_GENERATION,
            model_type=model_type,
            metadata={
                "task_id": task_id,
                "prompt": _extract_prompt(request_data),
                "watermark": watermark,
                "seed": seed,
                "service_tier": service_tier,
                **resolved,
            },
        )
    except Exception as exc:
        return _failure_response(
            format_error(exc),
            provider_name,
            model or _normalize_model(None),
            (
                AIModelType.IMAGE_TO_VIDEO
                if image_url or has_visual_reference(kwargs)
                else AIModelType.TEXT_TO_VIDEO
            ),
        )


def _failure_response(
    message: str,
    provider_name: str,
    model: str,
    model_type: AIModelType,
    metadata: Optional[Dict[str, Any]] = None,
) -> AIResponse:
    return AIResponse(
        success=False,
        error=message,
        provider=provider_name,
        model=model,
        task_type=AITaskType.VIDEO_GENERATION,
        model_type=model_type,
        metadata=metadata or {},
    )


def _extract_prompt(request_data: Dict[str, Any]) -> str:
    content = request_data.get("content") or []
    if not isinstance(content, list):
        return ""
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            return str(item.get("text") or "")
    return ""
