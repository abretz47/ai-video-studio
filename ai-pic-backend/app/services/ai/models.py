from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .manager import AIModelType, ProviderPriority


class ModelRegistryMixin:
    def get_ai_providers_status(self) -> Dict[str, Any]:
        """getAIprovider status"""
        if not self.ai_manager:
            return {}
        return self.ai_manager.get_provider_status()

    async def list_models(
        self,
        model_type_alias: Optional[str] = None,
        source: str = "auto",
    ) -> List[Dict[str, Any]]:
        """
 unified Lie Chu model, support An Lei Xing and Lai Yuan Guo Lv.

        model_type_alias:
          - 'text' / 'text_generation'
          - 'image' / 'text_to_image'
          - 'video' / 'text_to_video'
          - 'tts' / 'text_to_speech'
        source:
          - 'static' | 'remote' | 'auto'
        """
        if not self.ai_manager:
            return []

        aliases = {
            "text": AIModelType.TEXT_GENERATION,
            "text_generation": AIModelType.TEXT_GENERATION,
            "image": AIModelType.TEXT_TO_IMAGE,
            "text_to_image": AIModelType.TEXT_TO_IMAGE,
            "image_to_image": AIModelType.IMAGE_TO_IMAGE,
            "img2img": AIModelType.IMAGE_TO_IMAGE,
            "image_to_video": AIModelType.IMAGE_TO_VIDEO,
            "img2vid": AIModelType.IMAGE_TO_VIDEO,
            "i2v": AIModelType.IMAGE_TO_VIDEO,
            "video": AIModelType.TEXT_TO_VIDEO,
            "text_to_video": AIModelType.TEXT_TO_VIDEO,
            "tts": AIModelType.TEXT_TO_SPEECH,
            "text_to_speech": AIModelType.TEXT_TO_SPEECH,
        }
        mt = aliases.get(model_type_alias, None)

        cache_key = "all" if mt is None else mt.value
        if source == "auto" and cache_key in self.model_cache:
            cached = self.model_cache.get(cache_key) or []
            if cached:
                return cached

        models = await self.ai_manager.list_models(model_type=mt, source=source)
        enriched: list[Dict[str, Any]] = []
        for item in models:
            try:
                enriched.append(self._apply_ui_metadata(item))
            except Exception:
                enriched.append(item)

        if source == "auto":
            try:
                self.model_cache[cache_key] = enriched or []
            except Exception:
                pass

        return enriched

    def update_provider_config(
        self,
        provider_name: str,
        enabled: bool = None,
        weight: float = None,
        priority: str = None,
        max_requests_per_minute: int = None,
    ):
        """update provider configuration"""
        priority_enum = None
        if priority:
            priority_map = {
                "high": ProviderPriority.HIGH,
                "medium": ProviderPriority.MEDIUM,
                "low": ProviderPriority.LOW,
            }
            priority_enum = priority_map.get(priority.lower())

        self.ai_manager.update_provider_config(
            provider_name=provider_name,
            enabled=enabled,
            weight=weight,
            priority=priority_enum,
            max_requests_per_minute=max_requests_per_minute,
        )

    async def _reload_model_cache(self) -> None:
        """La Qu and cache Chang Yong model list, An model type Fen Zu."""
        if not self.ai_manager:
            return

        type_keys = [
            ("all", None),
            ("text_generation", AIModelType.TEXT_GENERATION),
            ("text_to_image", AIModelType.TEXT_TO_IMAGE),
            ("image_to_image", AIModelType.IMAGE_TO_IMAGE),
            ("text_to_video", AIModelType.TEXT_TO_VIDEO),
            ("text_to_speech", AIModelType.TEXT_TO_SPEECH),
        ]
        cache: dict[str, List[Dict[str, Any]]] = {}
        for key, mt in type_keys:
            try:
                models = await self.ai_manager.list_models(model_type=mt, source="auto")
                cache[key] = models or []
            except Exception as exc:  # pragma: no cover - cache warm guard
                self.logger.warning("model cache Jia Zai failed key=%s err=%s", key, exc)
                cache[key] = []
        self.model_cache = cache

    def _warm_model_cache(self) -> None:
        """sync call Yi Chu Shi Hua model cache; for example failed only Ji Lu log, not Zhong Duan Qi Dong."""
        if not self.ai_manager:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            self.logger.info("Jian Ce to run in Shi Jian Xun Huan, Tiao Guo model cache Yu Re")
            return

        try:
            asyncio.run(self._reload_model_cache())
        except Exception as exc:  # pragma: no cover - init guard
            self.logger.warning("model cache Chu Shi Hua failed: %s", exc)
