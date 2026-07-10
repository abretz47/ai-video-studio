"""
AIservice provider module

support Duo Zhong Di San FangAIservice provider: 
- OpenAI (text, image)
- Kling (video Sheng Cheng)
- Ji Meng (image Sheng Cheng)
- MiniMax (text, voice)
- DeepSeek (text)
- Volcengine Yin Qing (text, image, video)
"""

from .base import (
    AIModelType,
    AIResponse,
    AITaskType,
    BaseProvider,
    ModelInfo,
    ProviderConfig,
)
from .codex_provider import CodexProvider
from .deepseek_provider import DeepSeekProvider
from .jimeng_provider import JimengProvider
from .keling_provider import KelingProvider
from .minimax_provider import MinimaxProvider
from .openai_provider import OpenAIProvider
from .volcengine_provider import VolcengineProvider

__all__ = [
    "BaseProvider",
    "AIResponse",
    "AIModelType",
    "AITaskType",
    "ModelInfo",
    "ProviderConfig",
    "CodexProvider",
    "OpenAIProvider",
    "KelingProvider",
    "JimengProvider",
    "MinimaxProvider",
    "DeepSeekProvider",
    "VolcengineProvider",
]
