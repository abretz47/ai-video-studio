from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.episode_agent import EpisodeLangGraphAgent
from app.services.script_agent import ScriptLangGraphAgent
from app.services.story_agent import StoryLangGraphAgent
from app.services.storyboard_reasoner import (
    LANGGRAPH_AVAILABLE,
    StoryboardReActReasoner,
)

from .manager import (
    AI_MANAGER_AVAILABLE,
    AIServiceConfig,
    AIServiceManager,
    ProviderConfig,
    ProviderPriority,
    ProviderWeight,
)


class AIServiceBase:
    """Shared AI service initialization and provider setup."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.logger.info("Initializing AI Service")

        # keep Xiang after Jian Rong configuration
        self.base_url = settings.AI_SERVICE_URL
        self.api_key = settings.AI_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.stability_api_key = settings.STABILITY_API_KEY

        # Chu Shi Hua multiple providerAIservice manager
        self.ai_manager = self._initialize_ai_manager()
        self.model_cache: dict[str, list[dict]] = {}
        self._warm_model_cache()
        self.storyboard_reasoner = (
            StoryboardReActReasoner(self) if LANGGRAPH_AVAILABLE else None
        )
        self.episode_agent = (
            EpisodeLangGraphAgent(self) if LANGGRAPH_AVAILABLE else None
        )
        self.script_agent = ScriptLangGraphAgent(self) if LANGGRAPH_AVAILABLE else None
        self.story_agent = StoryLangGraphAgent(self) if LANGGRAPH_AVAILABLE else None

    def _initialize_ai_manager(self) -> Optional[AIServiceManager]:
        """Chu Shi HuaAIservice manager"""
        if settings.AI_FORCE_MOCK:
            self.logger.warning("AI_FORCE_MOCK enabled; skip provider manager init")
            return None

        if not AI_MANAGER_AVAILABLE:
            self.logger.warning("AIservice manager not allowed Yong, Shi Yongfallbackmode")
            return None

        try:
            # build provider configuration
            providers = {}
            provider_weights = {}

            # OpenAIconfiguration
            if self.openai_api_key:
                openai_base = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
                providers["openai"] = ProviderConfig(
                    name="openai",
                    api_key=self.openai_api_key,
                    base_url=openai_base,
                    timeout=120.0,
                )
                provider_weights["openai"] = ProviderWeight(
                    provider_name="openai",
                    weight=1.0,
                    priority=ProviderPriority.HIGH,
                    enabled=True,
                    max_requests_per_minute=100,
                )

            # Qi Ta provider configuration(support Shuang key Ren Zheng)
            # KlingAI(Kuai Shou)
            if settings.KELING_API_KEY and settings.KELING_SECRET_KEY:
                providers["keling"] = ProviderConfig(
                    name="keling",
                    api_key=settings.KELING_API_KEY,
                    api_secret=settings.KELING_SECRET_KEY,
                    base_url="https://api-beijing.klingai.com",
                    timeout=120.0,
                )
                provider_weights["keling"] = ProviderWeight(
                    provider_name="keling",
                    weight=0.8,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=60,
                )

            # Ji MengAI
            if settings.JIMENG_API_KEY and settings.JIMENG_SECRET_KEY:
                providers["jimeng"] = ProviderConfig(
                    name="jimeng",
                    api_key=settings.JIMENG_API_KEY,
                    api_secret=settings.JIMENG_SECRET_KEY,
                    base_url="https://api.jimeng.ai/v1",
                    timeout=120.0,
                )
                provider_weights["jimeng"] = ProviderWeight(
                    provider_name="jimeng",
                    weight=0.8,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=60,
                )

            # DeepSeek(Dan key)
            if settings.DEEPSEEK_API_KEY:
                providers["deepseek"] = ProviderConfig(
                    name="deepseek",
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com/v1",
                    timeout=120.0,
                )
                provider_weights["deepseek"] = ProviderWeight(
                    provider_name="deepseek",
                    weight=0.8,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=60,
                )

            # MiniMax
            if settings.MINIMAX_API_KEY:
                providers["minimax"] = ProviderConfig(
                    name="minimax",
                    api_key=settings.MINIMAX_API_KEY,
                    group_id=settings.MINIMAX_GROUP_ID,
                    base_url="https://api.minimax.chat/v1",
                    timeout=120.0,
                )
                provider_weights["minimax"] = ProviderWeight(
                    provider_name="minimax",
                    weight=0.7,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=60,
                )

            # Volcengine Yin Qing(Ark Seedream/text & image)
            if settings.VOLCENGINE_API_KEY:
                providers["volcengine"] = ProviderConfig(
                    name="volcengine",
                    api_key=settings.VOLCENGINE_API_KEY,
                    api_secret=settings.VOLCENGINE_SECRET_KEY,
                    timeout=120.0,
                )
                provider_weights["volcengine"] = ProviderWeight(
                    provider_name="volcengine",
                    weight=0.7,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=50,
                )

            # Google Gemini/Vertex AI text model
            google_vertex_enabled = bool(
                settings.GOOGLE_VERTEX_PROJECT_ID
                and settings.GOOGLE_VERTEX_LOCATION
                and (
                    settings.GOOGLE_VERTEX_ACCESS_TOKEN
                    or settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON
                    or settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_PATH
                    or settings.GOOGLE_VERTEX_API_KEY
                )
            )
            if settings.GOOGLE_API_KEY or google_vertex_enabled:
                google_base = (
                    settings.GOOGLE_BASE_URL
                    or "https://generativelanguage.googleapis.com"
                )
                providers["google"] = ProviderConfig(
                    name="google",
                    api_key=settings.GOOGLE_API_KEY,
                    # default Shi Yong Generative Language API, can through GOOGLE_BASE_URL Fu Gai
                    base_url=google_base,
                    video_base_url=settings.GOOGLE_VIDEO_BASE_URL,
                    vertex_project_id=settings.GOOGLE_VERTEX_PROJECT_ID,
                    vertex_location=settings.GOOGLE_VERTEX_LOCATION,
                    vertex_access_token=settings.GOOGLE_VERTEX_ACCESS_TOKEN,
                    vertex_api_key=settings.GOOGLE_VERTEX_API_KEY,
                    vertex_service_account_json=settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON,
                    vertex_service_account_path=settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_PATH,
                    timeout=120.0,
                    default_model=settings.GOOGLE_DEFAULT_MODEL,
                )
                provider_weights["google"] = ProviderWeight(
                    provider_name="google",
                    weight=0.8,
                    priority=ProviderPriority.MEDIUM,
                    enabled=True,
                    max_requests_per_minute=60,
                )

            # Ru Guo missing configuration anyprovider, returnNone
            if not providers:
                print("Jing Gao: missing configuration anyAIservice provider, Shi Yongfallbackmode")
                return None

            # createAIservice configuration
            config = AIServiceConfig(
                providers=providers,
                provider_weights=provider_weights,
                enable_fallback=True,
                enable_load_balancing=True,
                default_timeout=120.0,
                max_retries=3,
            )

            return AIServiceManager(config)
        except Exception as exc:
            print(f"AIFu Wu Guan Li Qi Chu Shi Hua failed: {exc}")
            return None
