"""Volcengine provider model definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..base import AIModelType, ModelInfo
from .video_models import get_video_models


def get_available_models() -> List[ModelInfo]:
    """Return the list of available Volcengine models."""
    return [
        ModelInfo(
            model_id="doubao-lite-4k",
            name="Dou Bao Qing Liang Ban",
            description="Qing Liang Ji text Sheng Cheng model, quick response",
            model_type=AIModelType.TEXT_GENERATION,
            max_tokens=4096,
            capabilities=["text_generation", "conversation", "fast_response"],
        ),
        ModelInfo(
            model_id="doubao-pro-4k",
            name="Dou Bao Zhuan Ye Ban",
            description="Zhuan Ye Ji text Sheng Cheng model, High qualityoutput",
            model_type=AIModelType.TEXT_GENERATION,
            max_tokens=4096,
            capabilities=[
                "text_generation",
                "analysis",
                "reasoning",
                "high_quality",
            ],
        ),
        ModelInfo(
            model_id="doubao-pro-32k",
            name="Dou Bao Zhuan Ye Ban Zhang text",
            description="support Zhang Wen Ben Chu Li Zhuan Ye Ban model",
            model_type=AIModelType.TEXT_GENERATION,
            max_tokens=32768,
            capabilities=[
                "text_generation",
                "long_context",
                "document_analysis",
            ],
        ),
        ModelInfo(
            model_id="doubao-seedream-4-5-251128",
            name="Seedream 4.5",
            description="Fang Zhou Da model Fu Wu Ping Tai image Sheng Cheng model(Seedream 4.5)",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=[
                "text_to_image",
                "image_to_image",
                "high_resolution",
            ],
            metadata={
                "ui": {
                    "size_options": ["2K"],
                    "aspect_ratio_options": [
                        "1:1",
                        "16:9",
                        "9:16",
                        "4:3",
                        "3:4",
                    ],
                    "supports_reference_image": True,
                }
            },
        ),
        ModelInfo(
            model_id="volcengine-visual-v1",
            name="Volcengine Shi Jue Sheng ChengV1",
            description="High qualityimage Sheng Cheng model",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=["text_to_image", "style_control", "high_resolution"],
        ),
        ModelInfo(
            model_id="volcengine-visual-pro",
            name="Volcengine Shi Jue Sheng ChengPro",
            description="Zhuan Ye Ban image Sheng Cheng, support Geng multiple style",
            model_type=AIModelType.TEXT_TO_IMAGE,
            supported_formats=["png", "jpg"],
            capabilities=["text_to_image", "multiple_styles", "ultra_quality"],
        ),
        *get_video_models(),
        ModelInfo(
            model_id="volcengine-tts-v1",
            name="Volcengine voice He Cheng",
            description="High qualityvoice He Cheng service",
            model_type=AIModelType.TEXT_TO_SPEECH,
            supported_formats=["mp3", "wav"],
            capabilities=[
                "text_to_speech",
                "emotion_control",
                "voice_cloning",
            ],
        ),
    ]


def fallback_models(
    models: List[ModelInfo], model_type: Optional[AIModelType]
) -> List[ModelInfo]:
    """Filter models by type for fallback."""
    if model_type:
        return [m for m in models if m.model_type == model_type]
    return models


def infer_model_type(model_id: str, item: Dict[str, Any]) -> AIModelType:
    """Infer model type from model ID and capability fields."""
    tokens = _collect_tokens(model_id, item)

    def _has_any(keywords: List[str]) -> bool:
        return any(keyword in token for token in tokens for keyword in keywords)

    if _has_any(["seedance", "video", "vid", "movie", "imagetovideo"]):
        return AIModelType.TEXT_TO_VIDEO
    if _has_any(["image", "visual", "seedream", "picture", "painting"]):
        return AIModelType.TEXT_TO_IMAGE
    if _has_any(["tts", "speech", "voice", "audio"]):
        return AIModelType.TEXT_TO_SPEECH
    if _has_any(["stt", "asr"]):
        return AIModelType.SPEECH_TO_TEXT
    return AIModelType.TEXT_GENERATION


def infer_capabilities(
    model_type: AIModelType,
    item: Dict[str, Any],
) -> List[str]:
    """Infer model capabilities from type and item metadata."""
    tokens = _collect_tokens(str(item.get("id") or ""), item)
    ability_tokens = _collect_abilities(item)

    caps: List[str] = []
    if model_type == AIModelType.TEXT_TO_IMAGE:
        caps.append("text_to_image")
        if any("image-to-image" in token or "imagetoi" in token for token in tokens):
            caps.append("image_to_image")
    elif model_type == AIModelType.TEXT_TO_VIDEO:
        caps.extend(_infer_video_capabilities(tokens))
    elif model_type == AIModelType.TEXT_TO_SPEECH:
        caps.append("text_to_speech")
    elif model_type == AIModelType.SPEECH_TO_TEXT:
        caps.append("speech_to_text")
    else:
        caps.append("text_generation")

    for token in ability_tokens:
        if "code" in token:
            caps.append("code_generation")
        if "chat" in token:
            caps.append("conversation")
        if "embed" in token:
            caps.append("embedding")
    return list(dict.fromkeys(caps))


def _infer_video_capabilities(tokens: list[str]) -> list[str]:
    joined = " ".join(tokens)
    caps = ["text_to_video"]
    if any(key in joined for key in ["seedance", "image_to_video", "imagetovideo"]):
        caps.extend(["image_to_video", "image_to_video_start_frame"])
    if "seedance-2-0" in joined or "seedance-1-5" in joined:
        caps.extend(
            [
                "image_to_video_start_end_frame",
                "reference_images",
                "generate_audio",
            ]
        )
    if "seedance-2-0" in joined:
        caps.extend(["reference_video", "reference_audio", "4s", "15s"])
    return caps


def _collect_tokens(model_id: str, item: Dict[str, Any]) -> list[str]:
    tokens = [model_id.lower()]
    for key in ["task_type", "type", "category", "name", "model_name"]:
        val = item.get(key)
        if isinstance(val, str):
            tokens.append(val.lower())
    tokens.extend(_collect_abilities(item))
    return tokens


def _collect_abilities(item: Dict[str, Any]) -> list[str]:
    abilities = item.get("abilities") or item.get("ability") or []
    if isinstance(abilities, str):
        return [abilities.lower()]
    if isinstance(abilities, list):
        return [str(a).lower() for a in abilities]
    return []
