from __future__ import annotations

from typing import Any, Iterable

from app.services.providers.volcengine_provider.guidance_scale import (
    supports_guidance_scale,
)
from app.utils.model_utils import is_gpt_image_model

from .provider_params import supported_ai_manager_keys
from .types import ImageGenMode


def _bool(value: bool) -> bool:
    return bool(value)


def build_image_gen_ui_metadata(
    *,
    provider: str | None,
    model_id: str | None,
    caps: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build UI metadata describing supported image-gen params by provider+mode."""
    provider_key = (provider or "").strip().lower()
    mid = (model_id or "").strip()
    caps_list = [str(c).lower() for c in (caps or []) if c is not None]

    text_keys = supported_ai_manager_keys(provider_key, ImageGenMode.TEXT_TO_IMAGE)
    image_keys = supported_ai_manager_keys(provider_key, ImageGenMode.IMAGE_TO_IMAGE)

    supports_cfg_scale_t2i = "cfg_scale" in text_keys
    supports_cfg_scale_i2i = "cfg_scale" in image_keys
    if provider_key == "volcengine":
        # Volcengine accepts cfg_scale (mapped to guidance_scale) only on specific models.
        supports_cfg = supports_guidance_scale(mid)
        supports_cfg_scale_t2i = supports_cfg
        supports_cfg_scale_i2i = supports_cfg

    max_count_t2i = 4 if "n" in text_keys else 1
    max_count_i2i = 4 if "count" in image_keys else 1
    is_openai_gpt_image = provider_key == "openai" and is_gpt_image_model(mid)
    if provider_key == "openai" and "dall-e-3" in mid.lower():
        # DALL·E 3 only supports n=1 in practice (and image_to_image is unsupported).
        max_count_t2i = 1
        max_count_i2i = 1

    # Some providers expose img2img as a capability on text_to_image models.
    supports_reference_image = "image_to_image" in caps_list

    max_reference_images_t2i: int | None = None
    if provider_key == "keling":
        max_reference_images_t2i = 1
    if provider_key == "google":
        max_reference_images_t2i = 4
    if provider_key == "openai" and is_openai_gpt_image:
        max_reference_images_t2i = 4

    supports_reference_images_t2i = (
        "reference_images" in text_keys
        or "extra_images" in text_keys
        or "image" in text_keys
    )
    if provider_key == "openai":
        supports_reference_images_t2i = is_openai_gpt_image

    text_to_image = {
        "supports_seed": _bool("seed" in text_keys),
        "supports_steps": _bool("steps" in text_keys),
        "supports_cfg_scale": _bool(supports_cfg_scale_t2i),
        "supports_negative_prompt": _bool("negative_prompt" in text_keys),
        "supports_style_preset_id": _bool("style_preset_id" in text_keys),
        "supports_style_spec": _bool("style_spec" in text_keys),
        "max_count": max_count_t2i,
        "supports_reference_images": _bool(supports_reference_images_t2i),
    }

    if (
        max_reference_images_t2i is not None
        and text_to_image["supports_reference_images"]
    ):
        text_to_image["max_reference_images"] = max_reference_images_t2i

    image_to_image = {
        "supports_seed": _bool("seed" in image_keys),
        "supports_steps": _bool("steps" in image_keys),
        "supports_cfg_scale": _bool(supports_cfg_scale_i2i),
        "supports_negative_prompt": _bool("negative_prompt" in image_keys),
        "supports_style_preset_id": _bool("style_preset_id" in image_keys),
        "supports_style_spec": _bool("style_spec" in image_keys),
        "supports_strength": _bool("strength" in image_keys),
        "supports_image_reference": _bool("image_reference" in image_keys),
        "supports_image_fidelity": _bool("image_fidelity" in image_keys),
        "supports_human_fidelity": _bool("human_fidelity" in image_keys),
        "max_count": max_count_i2i,
        "supports_extra_images": _bool(
            "extra_images" in image_keys or "reference_images" in image_keys
        ),
    }

    def _append_note(target: list[str], note: str) -> None:
        if note and note not in target:
            target.append(note)

    text_notes: list[str] = []
    image_notes: list[str] = []

    negative_prompt_note = "Gai provider not support negative_prompt: Chang Yong Yue Shu need write prompt(template Nei Zhi Constraints)"
    if not text_to_image["supports_negative_prompt"]:
        _append_note(text_notes, negative_prompt_note)

    if supports_reference_image and not image_to_image["supports_negative_prompt"]:
        if provider_key == "keling":
            _append_note(
                image_notes, "Ke Ling Tu Sheng Tu not support negative_prompt: Qing Yue Shu write prompt"
            )
        else:
            _append_note(image_notes, negative_prompt_note)

    volc_cfg_note = "Volcengine Yin Qing cfg_scale will Ying She to guidance_scale(You Xiao range Yue 1-10)"
    if provider_key == "volcengine":
        if text_to_image["supports_cfg_scale"]:
            _append_note(text_notes, volc_cfg_note)
        if supports_reference_image and image_to_image["supports_cfg_scale"]:
            _append_note(image_notes, volc_cfg_note)

    if provider_key == "keling" and text_to_image["supports_reference_images"]:
        _append_note(
            text_notes,
            "Kling Wen Sheng Tu reference Tu Jin support 1 Zhang; Shi Yong reference Tu Shi negative_prompt will He Bing Jin prompt",
        )

    if provider_key == "google" and text_to_image["supports_reference_images"]:
        _append_note(
            text_notes,
            "Google/Gemini reference Tu Hui Yi Nei Lian Fang Shi Shang Chuan: as avoid 413, suggestion≤4Zhang Qie Jin Liang Xiao Tu(background will automatic Ya Suo)",
        )
    if is_openai_gpt_image and text_to_image["supports_reference_images"]:
        _append_note(
            text_notes,
            "GPT Image 2 reference Tu Hui through OpenAI image edit API process, image input automatic An Gao Bao Zhen Ji Fei",
        )

    payload: dict[str, Any] = {
        "version": 1,
        "text_to_image": {**text_to_image, "notes": text_notes},
        "image_to_image": {**image_to_image, "notes": image_notes},
    }

    legacy_notes: list[str] = []
    for note in [*text_notes, *image_notes]:
        _append_note(legacy_notes, note)
    if legacy_notes:
        payload["notes"] = legacy_notes

    return {"image_gen": payload}
