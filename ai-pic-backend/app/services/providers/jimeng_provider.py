"""
Ji Meng(JiMeng)service provider

Zhuan Zhu Yu image Sheng Cheng and Tu Xiang Chu Li feature
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

from .base import (
    AIModelType,
    AIResponse,
    AITaskType,
    BaseProvider,
    ModelInfo,
    ProviderConfig,
)
from .image_param_utils import normalize_image_params, size_to_dimensions


class JimengProvider(BaseProvider):
    """Ji Meng service provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.jimeng.ai/v1"

    @property
    def supported_model_types(self) -> List[AIModelType]:
        return [AIModelType.TEXT_TO_IMAGE, AIModelType.IMAGE_TO_IMAGE]

    @property
    def available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                model_id="jimeng-sd-v1.5",
                name="Ji Meng Stable Diffusion 1.5",
                description="Ji YuSD1.5High qualityimage Sheng Cheng",
                model_type=AIModelType.TEXT_TO_IMAGE,
                supported_formats=["png", "jpg"],
                capabilities=["text_to_image", "style_control", "high_detail"],
                metadata={
                    "ui": {
                        "size_options": ["1024x1024"],
                        "aspect_ratio_options": ["1:1", "3:4", "4:3", "16:9", "9:16"],
                        "supports_aspect_ratio": False,
                        "supports_reference_image": False,
                    }
                },
            ),
            ModelInfo(
                model_id="jimeng-sdxl",
                name="Ji Meng SDXL",
                description="Geng Da model, GengHigh qualityoutput",
                model_type=AIModelType.TEXT_TO_IMAGE,
                supported_formats=["png", "jpg"],
                capabilities=["text_to_image", "ultra_high_quality", "realistic"],
                metadata={
                    "ui": {
                        "size_options": ["1024x1024"],
                        "aspect_ratio_options": ["1:1", "3:4", "4:3", "16:9", "9:16"],
                        "supports_aspect_ratio": False,
                        "supports_reference_image": False,
                    }
                },
            ),
            ModelInfo(
                model_id="jimeng-anime",
                name="Ji Meng Dong Man style",
                description="Zhuan Men You Hua Dong Man style image Sheng Cheng",
                model_type=AIModelType.TEXT_TO_IMAGE,
                supported_formats=["png", "jpg"],
                capabilities=["text_to_image", "anime_style", "character_design"],
                metadata={
                    "ui": {
                        "size_options": ["1024x1024"],
                        "aspect_ratio_options": ["1:1", "3:4", "4:3", "16:9", "9:16"],
                        "supports_aspect_ratio": False,
                        "supports_reference_image": False,
                    }
                },
            ),
            ModelInfo(
                model_id="jimeng-img2img",
                name="Ji Meng Tu Sheng Tu",
                description="Ji Yu reference image style Zhuan Huan",
                model_type=AIModelType.IMAGE_TO_IMAGE,
                supported_formats=["png", "jpg"],
                capabilities=["image_to_image", "style_transfer", "inpainting"],
                metadata={
                    "ui": {
                        "size_options": ["1024x1024"],
                        "aspect_ratio_options": ["1:1", "3:4", "4:3", "16:9", "9:16"],
                        "supports_aspect_ratio": False,
                        "supports_reference_image": True,
                    }
                },
            ),
        ]

    async def _initialize_client(self):
        """Chu Shi HuaHTTPclient"""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def generate_text(
        self, prompt: str, model: str = None, **kwargs
    ) -> AIResponse:
        """Ji Meng not support text Sheng Cheng"""
        return AIResponse(
            success=False,
            error="Ji Meng not support Chun text Sheng Cheng feature",
            provider=self.name,
            model=model or "unknown",
            task_type=AITaskType.STORY_GENERATION,
            model_type=AIModelType.TEXT_GENERATION,
        )

    async def generate_image(
        self,
        prompt: str,
        model: str = "jimeng-sdxl",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: int = -1,
        negative_prompt: str = "",
        style: str = "realistic",
        **kwargs,
    ) -> AIResponse:
        """Shi Yong Ji Meng Sheng Cheng image"""
        try:
            size_value = kwargs.pop("size", None)
            try:
                normalized_size, _, _ = normalize_image_params(
                    self.name, model, size_value, None
                )
            except ValueError as exc:
                return AIResponse(
                    success=False,
                    error=str(exc),
                    provider=self.name,
                    model=model,
                    task_type=AITaskType.PORTRAIT_GENERATION,
                    model_type=AIModelType.TEXT_TO_IMAGE,
                )
            if normalized_size:
                dims = size_to_dimensions(normalized_size)
                if dims:
                    width, height = dims

            client = await self.get_client()

            request_data = {
                "model": model,
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "style": style,
                **kwargs,
            }

            if negative_prompt:
                request_data["negative_prompt"] = negative_prompt

            if seed != -1:
                request_data["seed"] = seed

            response = await client.post(
                f"{self.base_url}/images/generations", json=request_data
            )
            response.raise_for_status()

            data = response.json()

            # Ji Meng Ke Neng return Ren WuIDneed Lun Xun, or directly return Jie Guo
            if "task_id" in data:
                # async Ren Wu, need Lun Xun(failed/Chao Shi when _poll_task_status Pao exception)
                task_id = data["task_id"]
                result = await self._poll_task_status(task_id)
                return AIResponse(
                    success=True,
                    data={"images": result.get("images", [])},
                    provider=self.name,
                    model=model,
                    task_type=AITaskType.PORTRAIT_GENERATION,
                    model_type=AIModelType.TEXT_TO_IMAGE,
                    metadata={
                        "task_id": task_id,
                        "width": width,
                        "height": height,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "seed": result.get("seed"),
                        "style": style,
                    },
                )
            elif "images" in data:
                # directly return Jie Guo
                return AIResponse(
                    success=True,
                    data={"images": data["images"]},
                    provider=self.name,
                    model=model,
                    task_type=AITaskType.PORTRAIT_GENERATION,
                    model_type=AIModelType.TEXT_TO_IMAGE,
                    metadata={
                        "width": width,
                        "height": height,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "seed": data.get("seed"),
                        "style": style,
                    },
                )

            return AIResponse(
                success=False,
                error="image Sheng Cheng response format error",
                provider=self.name,
                model=model,
                task_type=AITaskType.PORTRAIT_GENERATION,
                model_type=AIModelType.TEXT_TO_IMAGE,
            )

        except Exception as e:
            return AIResponse(
                success=False,
                error=self.format_error(e),
                provider=self.name,
                model=model,
                task_type=AITaskType.PORTRAIT_GENERATION,
                model_type=AIModelType.TEXT_TO_IMAGE,
            )

    async def image_to_image(
        self,
        image_url: str,
        prompt: str = None,
        model: str = "jimeng-img2img",
        strength: float = 0.75,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: int = -1,
        **kwargs,
    ) -> AIResponse:
        """Ji Meng Tu Sheng Tu"""
        try:
            size_value = kwargs.pop("size", None)
            width = None
            height = None
            if size_value is not None:
                try:
                    normalized_size, _, _ = normalize_image_params(
                        self.name, model, size_value, None
                    )
                except ValueError as exc:
                    return AIResponse(
                        success=False,
                        error=str(exc),
                        provider=self.name,
                        model=model,
                        task_type=AITaskType.SCENE_GENERATION,
                        model_type=AIModelType.IMAGE_TO_IMAGE,
                    )
                if normalized_size:
                    dims = size_to_dimensions(normalized_size)
                    if dims:
                        width, height = dims

            client = await self.get_client()

            request_data = {
                "model": model,
                "init_image": image_url,
                "strength": strength,
                "steps": steps,
                "cfg_scale": cfg_scale,
                **kwargs,
            }
            if width is not None and height is not None:
                request_data["width"] = width
                request_data["height"] = height

            if prompt:
                request_data["prompt"] = prompt

            if seed != -1:
                request_data["seed"] = seed

            response = await client.post(
                f"{self.base_url}/images/img2img", json=request_data
            )
            response.raise_for_status()

            data = response.json()

            if "task_id" in data:
                task_id = data["task_id"]
                result = await self._poll_task_status(task_id)
                return AIResponse(
                    success=True,
                    data={"images": result.get("images", [])},
                    provider=self.name,
                    model=model,
                    task_type=AITaskType.SCENE_GENERATION,
                    model_type=AIModelType.IMAGE_TO_IMAGE,
                    metadata={
                        "task_id": task_id,
                        "init_image": image_url,
                        "width": width,
                        "height": height,
                        "strength": strength,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "seed": result.get("seed"),
                    },
                )
            elif "images" in data:
                return AIResponse(
                    success=True,
                    data={"images": data["images"]},
                    provider=self.name,
                    model=model,
                    task_type=AITaskType.SCENE_GENERATION,
                    model_type=AIModelType.IMAGE_TO_IMAGE,
                    metadata={
                        "init_image": image_url,
                        "width": width,
                        "height": height,
                        "strength": strength,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "seed": data.get("seed"),
                    },
                )

            return AIResponse(
                success=False,
                error="Tu Sheng Tu response format error",
                provider=self.name,
                model=model,
                task_type=AITaskType.SCENE_GENERATION,
                model_type=AIModelType.IMAGE_TO_IMAGE,
            )

        except Exception as e:
            return AIResponse(
                success=False,
                error=self.format_error(e),
                provider=self.name,
                model=model,
                task_type=AITaskType.SCENE_GENERATION,
                model_type=AIModelType.IMAGE_TO_IMAGE,
            )

    async def _poll_task_status(
        self, task_id: str, max_attempts: int = 30, delay: int = 2
    ) -> Optional[Dict[str, Any]]:
        """Lun Xun Ren Wu status, return Jie Guo dict or in failed/Chao Shi when Pao Chu exception."""
        client = await self.get_client()
        last_error: str | None = None

        for attempt in range(max_attempts):
            try:
                response = await client.get(f"{self.base_url}/tasks/{task_id}")
                response.raise_for_status()

                data = response.json()
                task_status = data.get("status")

                if task_status == "completed":
                    return data.get("result")
                elif task_status == "failed":
                    err_msg = data.get("error", "Ji Meng Ren Wu execute failed")
                    logger.warning("Ji Meng Ren Wu %s failed: %s", task_id, err_msg)
                    raise RuntimeError(f"即梦任务失败: {err_msg}")
                elif task_status in ["pending", "running"]:
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.warning("Ji Meng Ren Wu %s unknown status: %s", task_id, task_status)
                    raise RuntimeError(f"即梦任务未知状态: {task_status}")

            except RuntimeError:
                raise
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    "Lun Xun Ji Meng Ren Wu status failed (Chang Shi %d/%d): %s",
                    attempt + 1,
                    max_attempts,
                    e,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"即梦任务 {task_id} 轮询超时 ({max_attempts * delay}s)"
            + (f", 最后错误: {last_error}" if last_error else "")
        )

    async def get_styles(self) -> AIResponse:
        """get available style list"""
        try:
            client = await self.get_client()

            response = await client.get(f"{self.base_url}/styles")
            response.raise_for_status()

            data = response.json()

            return AIResponse(
                success=True,
                data=data.get("styles", []),
                provider=self.name,
                model="styles",
                task_type=AITaskType.PORTRAIT_GENERATION,
                model_type=AIModelType.TEXT_TO_IMAGE,
            )

        except Exception as e:
            return AIResponse(
                success=False,
                error=self.format_error(e),
                provider=self.name,
                model="styles",
                task_type=AITaskType.PORTRAIT_GENERATION,
                model_type=AIModelType.TEXT_TO_IMAGE,
            )
