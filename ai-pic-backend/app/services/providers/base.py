"""
AIservice provider Ji Lei

Ding Yi allAIservice provider unified API and Gui Fan
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AIModelType(Enum):
    """AImodel type Mei Ju"""

    TEXT_GENERATION = "text_generation"  # text Sheng Cheng
    TEXT_TO_IMAGE = "text_to_image"  # Wen Sheng Tu
    IMAGE_TO_IMAGE = "image_to_image"  # Tu Sheng Tu
    IMAGE_TO_VIDEO = "image_to_video"  # Tu Sheng video
    TEXT_TO_VIDEO = "text_to_video"  # Wen Sheng video
    TEXT_TO_SPEECH = "text_to_speech"  # text Zhuan voice
    SPEECH_TO_TEXT = "speech_to_text"  # voice Zhuan text
    IMAGE_UNDERSTANDING = "image_understanding"  # image Li Jie
    VIDEO_UNDERSTANDING = "video_understanding"  # video Li Jie


class AITaskType(Enum):
    """AIRen Wu type Mei Ju"""

    STORY_GENERATION = "story_generation"  # story Sheng Cheng
    CHARACTER_CREATION = "character_creation"  # character create
    EPISODE_PLANNING = "episode_planning"  # episode Gui Hua
    SCRIPT_WRITING = "script_writing"  # script Xie Zuo
    PORTRAIT_GENERATION = "portrait_generation"  # Xiao Xiang Sheng Cheng
    SCENE_GENERATION = "scene_generation"  # scene Sheng Cheng
    VIDEO_GENERATION = "video_generation"  # video Sheng Cheng
    VOICE_GENERATION = "voice_generation"  # voice Sheng Cheng


class AIRequest(BaseModel):
    """AIrequest Ji Lei"""

    task_type: AITaskType
    model_type: AIModelType
    prompt: str
    parameters: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    model_config = {"protected_namespaces": ()}


class AIResponse(BaseModel):
    """AIresponse Ji Lei"""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    provider: str
    model: str
    task_type: AITaskType
    model_type: AIModelType
    usage: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()

    model_config = {"protected_namespaces": ()}


class ModelInfo(BaseModel):
    """model Xin Xi"""

    model_id: str
    name: str
    description: str
    model_type: AIModelType
    max_tokens: Optional[int] = None
    supported_formats: List[str] = []
    pricing: Dict[str, Any] = {}
    capabilities: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"protected_namespaces": ()}


class ProviderConfig(BaseModel):
    """service provider configuration"""

    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    group_id: Optional[str] = None
    region: Optional[str] = None
    base_url: Optional[str] = None
    video_base_url: Optional[str] = None
    vertex_project_id: Optional[str] = None
    vertex_location: Optional[str] = None
    vertex_access_token: Optional[str] = None
    vertex_api_key: Optional[str] = None
    vertex_service_account_json: Optional[str] = None
    vertex_service_account_path: Optional[str] = None
    timeout: int = 180
    max_retries: int = 3
    rate_limit: Dict[str, int] = {}
    enabled: bool = True
    default_model: Optional[str] = None

    model_config = {"protected_namespaces": (), "extra": "ignore"}


class BaseProvider(ABC):
    """AIservice provider Ji Lei"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
        self._client = None
        self._loop_id: Optional[int] = None

    @property
    @abstractmethod
    def supported_model_types(self) -> List[AIModelType]:
        """support model type list"""
        pass

    @property
    @abstractmethod
    def available_models(self) -> List[ModelInfo]:
        """available model list"""
        pass

    @abstractmethod
    async def _initialize_client(self):
        """Chu Shi HuaAPIclient"""
        pass

    async def get_client(self):
        """
 getAPIclient, if Guan Bi or Bang Ding in Bu Tong Shi Jian Xun Huan on then retry Chu Shi Hua.

 Celery worker in will through anyio.run Qi Dong Xin Shi Jian Xun Huan, 
 if Fu Yong Bang Ding in Jiu loop on AsyncClient will Dao Zhi `Event loop is closed`.
 Yin Ci here An current loop id Zuo Yi Ci Ge Li.
        """
        try:
            loop = asyncio.get_running_loop()
            loop_id = id(loop)
        except RuntimeError:
            # missing run in Shi Jian Xun Huan(Bu Tai Ke Neng Chu Xian in async context), Tui Hui Jian Dan check
            loop_id = None

        client = self._client
        if (
            client is None
            or getattr(client, "is_closed", False)
            or (loop_id is not None and self._loop_id != loop_id)
        ):
            await self._initialize_client()
            client = self._client
            self._loop_id = loop_id
        return client

    @abstractmethod
    async def generate_text(
        self, prompt: str, model: str = None, **kwargs
    ) -> AIResponse:
        """Sheng Cheng text"""
        pass

    @abstractmethod
    async def generate_image(
        self, prompt: str, model: str = None, **kwargs
    ) -> AIResponse:
        """Wen Sheng Tu"""
        pass

    async def image_to_image(
        self, image_url: str, prompt: str = None, model: str = None, **kwargs
    ) -> AIResponse:
        """Tu Sheng Tu(can Xuan Shi Xian)"""
        return AIResponse(
            success=False,
            error="Tu Sheng Tu feature not Shi Xian",
            provider=self.name,
            model=model or "unknown",
            task_type=AITaskType.SCENE_GENERATION,
            model_type=AIModelType.IMAGE_TO_IMAGE,
        )

    async def generate_video(
        self, prompt: str = None, image_url: str = None, model: str = None, **kwargs
    ) -> AIResponse:
        """video Sheng Cheng(can Xuan Shi Xian)"""
        return AIResponse(
            success=False,
            error="video Sheng Cheng feature not Shi Xian",
            provider=self.name,
            model=model or "unknown",
            task_type=AITaskType.VIDEO_GENERATION,
            model_type=(
                AIModelType.TEXT_TO_VIDEO if prompt else AIModelType.IMAGE_TO_VIDEO
            ),
        )

    async def text_to_speech(
        self, text: str, model: str = None, **kwargs
    ) -> AIResponse:
        """text Zhuan voice(can Xuan Shi Xian)"""
        return AIResponse(
            success=False,
            error="text Zhuan voice feature not Shi Xian",
            provider=self.name,
            model=model or "unknown",
            task_type=AITaskType.VOICE_GENERATION,
            model_type=AIModelType.TEXT_TO_SPEECH,
        )

    async def understand_image(
        self, image_url: str, question: str = None, model: str = None, **kwargs
    ) -> AIResponse:
        """image Li Jie(can Xuan Shi Xian)"""
        return AIResponse(
            success=False,
            error="image Li Jie feature not Shi Xian",
            provider=self.name,
            model=model or "unknown",
            task_type=AITaskType.CHARACTER_CREATION,
            model_type=AIModelType.IMAGE_UNDERSTANDING,
        )

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """get model Xin Xi"""
        for model in self.available_models:
            if model.model_id == model_id:
                return model
        return None

    async def fetch_remote_models(
        self,
        model_type: Optional[AIModelType] = None,
    ) -> List[ModelInfo]:
        """
 default Yuan Duan model La Qu Shi Xian: priority call provider base_url below/models API, 
 then and local whitelist Jiao Ji, Zui Zhong failed then fallback Jing Tai list.
        """
        # Yu Bei cache Zuo Wei fallback
        fallback_models = self.available_models
        if model_type:
            fallback_models = [m for m in fallback_models if m.model_type == model_type]

        try:
            client = await self.get_client()
            base_url = getattr(self, "base_url", None)
            if client is None or not base_url:
                return fallback_models

            resp = await client.get(f"{base_url}/models")
            resp.raise_for_status()
            payload = resp.json()
            server_ids = {
                item.get("id")
                for item in payload.get(
                    "data", payload if isinstance(payload, dict) else []
                )
                if isinstance(item, dict) and item.get("id")
            }
            if not server_ids:
                return fallback_models

            # only return in Yuan Duan Cun Zai Qie in local Bai Ming Dan in model
            filtered = [
                m
                for m in self.available_models
                if m.model_id in server_ids
                and (not model_type or m.model_type == model_type)
            ]
            return filtered or fallback_models
        except Exception:
            return fallback_models

    def supports_model_type(self, model_type: AIModelType) -> bool:
        """check Shi Fou support Zhi Ding model type"""
        return model_type in self.supported_model_types

    async def health_check(self) -> bool:
        """Jian Kang Jian Cha"""
        try:
            client = await self.get_client()
            return client is not None
        except Exception:
            return False

    def estimate_cost(self, request: AIRequest) -> float:
        """Gu Suan request Cheng Ben(can Xuan Shi Xian)"""
        return 0.0

    def format_error(self, error: Exception) -> str:
        """Ge Shi Hua Cuo Wu Xin Xi"""
        detail = str(error)
        try:
            import httpx

            if isinstance(error, httpx.HTTPStatusError):
                response_text = (error.response.text or "").strip()
                if response_text:
                    detail = f"{detail} | response={response_text[:1000]}"
        except Exception:
            pass
        return f"{self.name} 错误: {detail}"
