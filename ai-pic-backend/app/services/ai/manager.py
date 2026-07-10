from app.core.logging import get_logger

try:
    from app.services.ai_service_manager import (
        AIServiceConfig,
        AIServiceManager,
        ProviderPriority,
        ProviderWeight,
    )
    from app.services.providers.base import AIModelType, ProviderConfig

    AI_MANAGER_AVAILABLE = True
except ImportError as exc:
    logger = get_logger()
    logger.warning(f"AIFu Wu Guan Li Qi Dao Ru failed，Jiang Shi YongfallbackMo Shi: {exc}")
    AIServiceManager = None
    AIServiceConfig = None
    ProviderWeight = None
    ProviderPriority = None
    ProviderConfig = None
    AIModelType = None
    AI_MANAGER_AVAILABLE = False

__all__ = [
    "AI_MANAGER_AVAILABLE",
    "AIServiceConfig",
    "AIServiceManager",
    "ProviderPriority",
    "ProviderWeight",
    "ProviderConfig",
    "AIModelType",
]
