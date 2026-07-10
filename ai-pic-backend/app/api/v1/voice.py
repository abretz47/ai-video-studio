from typing import Any, Dict, List, Optional

from app.core.middleware import get_current_active_user
from app.models.user import User
from app.services.minimax_client import MinimaxAPIError
from app.services.voice_service import voice_service
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class VoiceSynthesisRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    model: str = Field("speech-2.6-hd", description="Voice model")
    voice_id: Optional[str] = Field(
        None, description="Voice ID; leave empty for the server to choose the default voice"
    )
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate，0.5~2.0")
    vol: Optional[float] = Field(1.0, gt=0, le=10, description="Volume")
    pitch: Optional[float] = Field(0.0, ge=-12, le=12, description="Pitch")
    emotion: Optional[str] = Field(
        None, description="Emotion tag, optional happy/sad/angry/..."
    )
    sample_rate: Optional[int] = Field(None, description="Sample rate")
    bitrate: Optional[int] = Field(None, description="Bitrate")
    format: Optional[str] = Field("mp3", description="Audio format")
    channel: Optional[int] = Field(1, ge=1, le=2, description="Channels")
    output_format: str = Field("url", description="Return format url/hex")
    stream: bool = Field(False, description="Whether to stream output")
    subtitle_enable: bool = Field(False, description="Whether to generate subtitles")
    aigc_watermark: bool = Field(False, description="Whether to add watermark")
    language_boost: Optional[str] = Field(None, description="Minor-language/dialect enhancement")
    text_normalization: Optional[bool] = Field(None, description="Whether to enable text normalization")
    latex_read: Optional[bool] = Field(None, description="Whether to read LaTeX formulas aloud")
    pronunciation_dict: Optional[Dict[str, Any]] = Field(
        None, description="Custom pronunciation dictionary"
    )
    stream_options: Optional[Dict[str, Any]] = Field(None, description="Streaming options")
    timber_weights: Optional[List[Dict[str, Any]]] = Field(
        None, description="Mixed voice settings"
    )
    provider: Optional[str] = Field(
        None, description="Specify the voice provider; the first available provider is used by default"
    )


class VoiceDesignRequest(BaseModel):
    prompt: str = Field(..., description="Voice description")
    preview_text: str = Field(..., description="Preview text")
    voice_id: Optional[str] = Field(None, description="Optional custom voice_id")
    aigc_watermark: bool = Field(False, description="Whether to watermark preview audio")
    provider: Optional[str] = Field(None, description="Voice provider")


class VoiceDeleteRequest(BaseModel):
    voice_type: str = Field(..., description="voice_cloning / voice_generation")
    voice_id: str = Field(..., description="voice_id to delete")
    provider: Optional[str] = Field(None, description="Voice provider")


class MusicGenerationRequest(BaseModel):
    model: str = Field("music-2.0", description="Music model")
    prompt: str = Field(..., description="Music description")
    lyrics: str = Field(..., description="Lyrics")
    stream: bool = Field(False, description="Whether to return a stream")
    output_format: str = Field("hex", description="Output format url/hex; only hex is supported when streaming")
    sample_rate: Optional[int] = Field(None, description="Sample rate")
    bitrate: Optional[int] = Field(None, description="Bitrate")
    format: Optional[str] = Field("mp3", description="Audio format")
    aigc_watermark: bool = Field(False, description="Whether to add watermark")
    provider: Optional[str] = Field(None, description="Voice provider")


@router.get("/enums")
async def list_voice_enums(current_user: User = Depends(get_current_active_user)):
    """Return available enums (Chinese-English mapping)"""
    enums = voice_service.enums()
    return {"success": True, "data": enums}


@router.get("/voices")
async def list_voices(
    voice_type: str = Query(
        "all", description="Voice type system/voice_cloning/voice_generation/all"
    ),
    provider: Optional[str] = Query(None, description="Specify provider"),
    refresh: bool = Query(False, description="Whether to force-refresh the remote list"),
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = await voice_service.list_voices(
            voice_type=voice_type, provider=provider, force_refresh=refresh
        )
        return {"success": True, "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MinimaxAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice query failed: {exc}")


@router.post("/tts")
async def synthesize_voice(
    request: VoiceSynthesisRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        output_format = request.output_format
        if request.stream and output_format == "url":
            output_format = "hex"

        result = await voice_service.synthesize(
            provider=request.provider,
            text=request.text,
            model=request.model,
            voice_id=request.voice_id,
            speed=request.speed,
            vol=request.vol,
            pitch=request.pitch,
            emotion=request.emotion,
            sample_rate=request.sample_rate,
            bitrate=request.bitrate,
            format=request.format,
            channel=request.channel,
            output_format=output_format,
            stream=request.stream,
            subtitle_enable=request.subtitle_enable,
            aigc_watermark=request.aigc_watermark,
            language_boost=request.language_boost,
            text_normalization=request.text_normalization,
            latex_read=request.latex_read,
            pronunciation_dict=request.pronunciation_dict,
            stream_options=request.stream_options,
            timber_weights=request.timber_weights,
        )
        return {"success": True, "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MinimaxAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {exc}")


@router.post("/design")
async def design_voice(
    request: VoiceDesignRequest, current_user: User = Depends(get_current_active_user)
):
    try:
        result = await voice_service.design_voice(
            prompt=request.prompt,
            preview_text=request.preview_text,
            voice_id=request.voice_id,
            aigc_watermark=request.aigc_watermark,
            provider=request.provider,
        )
        return {"success": True, "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MinimaxAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice design failed: {exc}")


@router.delete("/voices/{voice_id}")
async def delete_voice(
    voice_id: str,
    request: VoiceDeleteRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = await voice_service.delete_voice(
            voice_type=request.voice_type, voice_id=voice_id, provider=request.provider
        )
        return {"success": True, "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MinimaxAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete voice: {exc}")


@router.post("/music")
async def generate_music(
    request: MusicGenerationRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        output_format = request.output_format
        if request.stream:
            output_format = "hex"
        result = await voice_service.generate_music(
            provider=request.provider,
            model=request.model,
            prompt=request.prompt,
            lyrics=request.lyrics,
            stream=request.stream,
            output_format=output_format,
            sample_rate=request.sample_rate,
            bitrate=request.bitrate,
            format=request.format,
            aigc_watermark=request.aigc_watermark,
        )
        return {"success": True, "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MinimaxAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Music generation failed: {exc}")
