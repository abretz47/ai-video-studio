"""
AI service provider management API

Provides a unified interface for multiple AI service providers, including text generation, image generation, video generation, and speech synthesis.
"""

from typing import Any, Dict, List, Optional

from app.core.middleware import get_current_active_user
from app.models.user import User
from app.schemas.style import StyleSpec
from app.services.ai_service import ai_service
from app.services.storage.oss_service import oss_service
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class TextGenerationRequest(BaseModel):
    """Text generation request"""

    prompt: str = Field(..., description="Generation prompt")
    model: Optional[str] = Field(None, description="Specific model")
    prefer_provider: Optional[str] = Field(None, description="Preferred provider")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    max_tokens: Optional[int] = Field(
        None, description="Maximum token count (unlimited when empty; determined by the model)"
    )
    temperature: float = Field(0.7, description="Creativity parameter")


class ImageGenerationRequest(BaseModel):
    """Image generation request"""

    prompt: str = Field(..., description="Image description")
    model: Optional[str] = Field(None, description="Specific model")
    prefer_provider: Optional[str] = Field(None, description="Preferred provider")
    width: int = Field(1024, description="Image width")
    height: int = Field(1024, description="Image height")
    style: str = Field("realistic", description="Image style")
    style_preset_id: Optional[str] = Field(
        None, description="Style preset ID (backend is the single source of truth)"
    )
    style_spec: Optional[StyleSpec] = Field(
        default=None, description="Style schema (partial fields allowed)"
    )
    count: int = Field(1, description="Number of images to generate")


class ImageToImageRequest(BaseModel):
    """Image-to-image request"""

    image_url: str = Field(..., description="Source image URL")
    prompt: Optional[str] = Field(None, description="Optional guidance prompt")
    model: Optional[str] = Field(
        None, description="Specific model (if omitted, the service selects automatically)"
    )
    prefer_provider: Optional[str] = Field(None, description="Preferred provider")
    style: Optional[str] = Field(
        None, description="Backward-compatible legacy style field (realistic/anime/cartoon/portrait)"
    )
    style_preset_id: Optional[str] = Field(
        None, description="Style preset ID (backend is the single source of truth)"
    )
    style_spec: Optional[StyleSpec] = Field(
        default=None, description="Style schema (partial fields allowed)"
    )
    count: int = Field(1, description="Number of images to generate")


class VideoGenerationRequest(BaseModel):
    """Video generation request"""

    prompt: Optional[str] = Field(None, description="Video description")
    image_url: Optional[str] = Field(None, description="Reference image URL")
    model: Optional[str] = Field(None, description="Specific model")
    prefer_provider: Optional[str] = Field(None, description="Preferred provider")
    duration: int = Field(5, description="Video duration (seconds)")
    fps: int = Field(24, description="Frame rate")
    resolution: str = Field("1280x720", description="Resolution")
    style: str = Field("realistic", description="Video style")


class SpeechGenerationRequest(BaseModel):
    """Speech generation request"""

    text: str = Field(..., description="Text to convert")
    model: Optional[str] = Field(None, description="Specific model")
    prefer_provider: Optional[str] = Field(None, description="Preferred provider")
    voice_type: Optional[str] = Field(None, description="Voice type")
    speed: float = Field(1.0, description="Speech rate")


class ProviderConfigRequest(BaseModel):
    """Provider configuration request"""

    enabled: Optional[bool] = Field(None, description="Enabled")
    weight: Optional[float] = Field(None, description="Weight")
    priority: Optional[str] = Field(None, description="Priority (high/medium/low)")
    max_requests_per_minute: Optional[int] = Field(None, description="Max requests per minute")


@router.post("/generate/text")
async def generate_text(
    request: TextGenerationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Generate text"""
    try:
        kwargs = {
            "prompt": request.prompt,
            "model": request.model,
            "prefer_provider": request.prefer_provider,
            "system_prompt": request.system_prompt,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        response = await ai_service.ai_manager.generate_text(**kwargs)

        if response.success:
            return {
                "success": True,
                "data": {
                    "content": response.data,
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "metadata": response.metadata,
                },
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


@router.post("/generate/image")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Generate image"""
    try:
        response = await ai_service.ai_manager.generate_image(
            prompt=request.prompt,
            model=request.model,
            prefer_provider=request.prefer_provider,
            width=request.width,
            height=request.height,
            style=request.style,
            style_preset_id=request.style_preset_id,
            style_spec=request.style_spec,
            n=request.count,
        )

        if response.success:
            return {
                "success": True,
                "data": {
                    "images": response.data.get("images", []),
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "metadata": response.metadata,
                },
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/generate/image-to-image")
async def generate_image_to_image(
    request: ImageToImageRequest, current_user: User = Depends(get_current_active_user)
):
    """Image-to-image generation endpoint (uniformly routed to providers that support IMAGE_TO_IMAGE)"""
    try:
        response = await ai_service.ai_manager.image_to_image(
            image_url=request.image_url,
            prompt=request.prompt,
            model=request.model,
            prefer_provider=request.prefer_provider,
            style=request.style,
            style_preset_id=request.style_preset_id,
            style_spec=request.style_spec,
            count=request.count,
        )

        if response.success:
            return {
                "success": True,
                "data": {
                    "images": response.data.get("images", []),
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "metadata": response.metadata,
                },
            }
        raise HTTPException(status_code=400, detail=response.error)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image-to-image generation failed: {str(e)}")


@router.post("/generate/video")
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Generate video"""
    try:
        if not request.prompt and not request.image_url:
            raise HTTPException(status_code=400, detail="Either prompt or image_url must be provided")

        response = await ai_service.ai_manager.generate_video(
            prompt=request.prompt,
            image_url=request.image_url,
            model=request.model,
            prefer_provider=request.prefer_provider,
            duration=request.duration,
            fps=request.fps,
            resolution=request.resolution,
        )

        if response.success:
            return {
                "success": True,
                "data": {
                    "video_url": response.data.get("video_url"),
                    "thumbnail_url": response.data.get("thumbnail_url"),
                    "duration": response.data.get("duration"),
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "metadata": response.metadata,
                },
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/generate/speech")
async def generate_speech(
    request: SpeechGenerationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Generate speech"""
    try:
        response = await ai_service.ai_manager.text_to_speech(
            text=request.text,
            model=request.model,
            prefer_provider=request.prefer_provider,
            voice_type=request.voice_type,
            speed=request.speed,
        )

        if response.success:
            return {
                "success": True,
                "data": {
                    "audio_url": response.data.get("audio_url"),
                    "duration": response.data.get("duration"),
                    "provider": response.provider,
                    "model": response.model,
                    "usage": response.usage,
                    "metadata": response.metadata,
                },
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")


@router.get("/providers/status")
async def get_providers_status(current_user: User = Depends(get_current_active_user)):
    """Get status for all providers"""
    try:
        status = ai_service.get_ai_providers_status()
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.put("/providers/{provider_name}/config")
async def update_provider_config(
    provider_name: str,
    request: ProviderConfigRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Update provider configuration"""
    try:
        # Verify that the provider exists
        status = ai_service.get_ai_providers_status()
        if provider_name not in status:
            raise HTTPException(
                status_code=404, detail=f"Provider {provider_name} does not exist"
            )

        ai_service.update_provider_config(
            provider_name=provider_name,
            enabled=request.enabled,
            weight=request.weight,
            priority=request.priority,
            max_requests_per_minute=request.max_requests_per_minute,
        )

        return {
            "success": True,
            "data": {"message": f"Provider {provider_name} configuration updated"},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.get("/providers/{provider_name}/models")
async def get_provider_models(
    provider_name: str, current_user: User = Depends(get_current_active_user)
):
    """Get available models for the specified provider"""
    try:
        status = ai_service.get_ai_providers_status()
        if provider_name not in status:
            raise HTTPException(
                status_code=404, detail=f"Provider {provider_name} does not exist"
            )

        provider_status = status[provider_name]
        return {
            "success": True,
            "data": {
                "provider": provider_name,
                "models": provider_status.get("available_models", []),
                "supported_model_types": provider_status.get(
                    "supported_model_types", []
                ),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model list: {str(e)}")


@router.get("/models/available")
async def get_available_models(
    model_type: Optional[str] = None,
    source: str = "auto",
    current_user: User = Depends(get_current_active_user),
):
    """Return the aggregated available model list from all providers

    Query:
    - model_type: Filter model type, for example 'text' / 'image' / 'video'
    - source: 'static' | 'remote' | 'auto' (default auto: prefer official APIs, fall back to static on failure)
    """
    try:
        if source not in {"static", "remote", "auto"}:
            source = "auto"

        status = ai_service.get_ai_providers_status()
        enabled_providers = [
            name for name, meta in status.items() if meta.get("enabled", True)
        ]
        if not enabled_providers:
            raise HTTPException(
                status_code=503,
                detail="No AI providers are currently available. Check whether OPENAI_API_KEY / VOLCENGINE_API_KEY and related settings have been injected into the container.",
            )

        # List models through the unified AIService/AIServiceManager
        models = await ai_service.list_models(
            model_type_alias=model_type, source=source
        )
        if not models:
            raise HTTPException(
                status_code=503,
                detail=f"No models are currently available (model_type={model_type or 'all'}). Confirm that the corresponding provider keys are configured and that service initialization completed without errors.",
            )
        # Add the frontend-expected model_id field (provider:model)
        enriched = [
            {
                "model_id": f"{m['provider']}:{m['id']}",
                "id": m["id"],
                "name": m.get("name"),
                "provider": m["provider"],
                "type": m.get("type"),
                "capabilities": m.get("capabilities", []),
                "metadata": m.get("metadata", {}),
            }
            for m in models
        ]
        return {"success": True, "data": {"models": enriched, "count": len(enriched)}}
    except HTTPException:
        # Pass through business exceptions directly to avoid wrapping them in a generic 500
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to get aggregated model list: {str(e)}")


@router.post("/providers/test/{provider_name}")
async def test_provider(
    provider_name: str, current_user: User = Depends(get_current_active_user)
):
    """Test the connection for the specified provider"""
    try:
        # Test text generation
        response = await ai_service.ai_manager.generate_text(
            prompt="Please say 'Hello World'",
            prefer_provider=provider_name,
        )

        if response.success:
            return {
                "success": True,
                "data": {
                    "provider": provider_name,
                    "status": "connected",
                    "test_response": response.data,
                    "model_used": response.model,
                    "usage": response.usage,
                },
            }
        else:
            return {
                "success": False,
                "data": {
                    "provider": provider_name,
                    "status": "failed",
                    "error": response.error,
                },
            }

    except Exception as e:
        return {
            "success": False,
            "data": {"provider": provider_name, "status": "error", "error": str(e)},
        }


# OSS storage management endpoints


class UploadUrlRequest(BaseModel):
    """URL upload request"""

    url: str = Field(..., description="File URL to upload")
    file_type: str = Field("image", description="File type (image/video/audio)")
    prefix: Optional[str] = Field(None, description="Storage prefix")
    metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")


class BatchUploadRequest(BaseModel):
    """Batch upload request"""

    urls: List[str] = Field(..., description="List of file URLs to upload")
    file_type: str = Field("image", description="File type")
    prefix: Optional[str] = Field(None, description="Storage prefix")
    metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")


@router.post("/storage/upload-url")
async def upload_from_url(
    request: UploadUrlRequest, current_user: User = Depends(get_current_active_user)
):
    """Upload a file from a URL to OSS"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        result = await oss_service.upload_from_url(
            url=request.url,
            file_type=request.file_type,
            prefix=request.prefix,
            metadata=request.metadata,
        )

        if result["success"]:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/storage/batch-upload")
async def batch_upload_from_urls(
    request: BatchUploadRequest, current_user: User = Depends(get_current_active_user)
):
    """Batch upload files from URLs to OSS"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        results = await oss_service.upload_multiple_urls(
            urls=request.urls,
            file_type=request.file_type,
            prefix=request.prefix,
            metadata=request.metadata,
        )

        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count

        return {
            "success": True,
            "data": {
                "total": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/storage/list")
async def list_storage_objects(
    prefix: str = "",
    max_keys: int = 100,
    marker: str = "",
    current_user: User = Depends(get_current_active_user),
):
    """List OSS storage objects"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        result = oss_service.list_objects(
            prefix=prefix, max_keys=max_keys, marker=marker
        )

        if result["success"]:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list objects: {str(e)}")


@router.get("/storage/info/{object_key:path}")
async def get_object_info(
    object_key: str, current_user: User = Depends(get_current_active_user)
):
    """Get OSS object information"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        result = oss_service.get_object_info(object_key)

        if result["success"]:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=404, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get object information: {str(e)}")


@router.delete("/storage/{object_key:path}")
async def delete_storage_object(
    object_key: str, current_user: User = Depends(get_current_active_user)
):
    """Delete OSS storage object"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        result = oss_service.delete_object(object_key)

        if result["success"]:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete object: {str(e)}")


@router.get("/storage/signed-url/{object_key:path}")
async def get_signed_url(
    object_key: str,
    expires: int = 3600,
    method: str = "GET",
    current_user: User = Depends(get_current_active_user),
):
    """Generate a signed URL for an OSS object"""
    if not oss_service:
        raise HTTPException(status_code=503, detail="OSS service is not configured")

    try:
        signed_url = oss_service.get_signed_url(
            object_key=object_key, expires=expires, method=method
        )

        return {
            "success": True,
            "data": {
                "object_key": object_key,
                "signed_url": signed_url,
                "expires_in": expires,
                "method": method,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {str(e)}")


@router.get("/storage/status")
async def get_storage_status(current_user: User = Depends(get_current_active_user)):
    """Get OSS storage service status"""
    if not oss_service:
        return {
            "success": False,
            "data": {"status": "disabled", "message": "OSS service is not configured"},
        }

    try:
        # Test OSS connection
        test_result = oss_service.list_objects(prefix="", max_keys=1)

        return {
            "success": True,
            "data": {
                "status": "enabled" if test_result["success"] else "error",
                "bucket": oss_service.bucket_name,
                "endpoint": oss_service.endpoint,
                "domain": oss_service.domain,
                "message": (
                    "OSS service is operating normally"
                    if test_result["success"]
                    else test_result.get("error", "Connection failed")
                ),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "data": {"status": "error", "message": f"OSS service status check failed: {str(e)}"},
        }
