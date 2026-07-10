import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Xiang Mu Ji Ben Xin Xi
    PROJECT_NAME: str = "AIimage Sheng ChengAPI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # An Quan configuration
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # database configuration
    DATABASE_URL: str = (
        "mysql+pymysql://root:Pa88word@127.0.0.1:13306/ai_video_studio?charset=utf8mb4"
    )

    # Redisconfiguration
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_EAGER_PROPAGATES: bool = True

    # CORSconfiguration
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "localhost:8000",
        "127.0.0.1:8000",
        "*",
    ]

    # file Shang Chuan configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif"]

    # AIservice configuration
    AI_SERVICE_URL: Optional[str] = None
    AI_API_KEY: Optional[str] = None

    # OpenAIconfiguration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    CODEX_AUTH_PATH: Optional[str] = None
    CODEX_RESPONSES_URL: Optional[str] = None
    CODEX_DEFAULT_MODEL: Optional[str] = "gpt-5.4"
    AI_FORCE_MOCK: bool = False

    # Stability AIconfiguration
    STABILITY_API_KEY: Optional[str] = None

    # Qi TaAIservice configuration
    # KlingAI(Kuai Shou)- Shuang key Ren Zheng
    KELING_API_KEY: Optional[str] = None
    KELING_SECRET_KEY: Optional[str] = None

    # Ji MengAI - Shuang key Ren Zheng
    JIMENG_API_KEY: Optional[str] = None
    JIMENG_SECRET_KEY: Optional[str] = None

    # MiniMaxconfiguration
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_GROUP_ID: Optional[str] = None

    # DeepSeekconfiguration
    DEEPSEEK_API_KEY: Optional[str] = None

    # Volcengine Yin Qing configuration
    VOLCENGINE_API_KEY: Optional[str] = None
    VOLCENGINE_SECRET_KEY: Optional[str] = None
    VOLCENGINE_REGION: Optional[str] = None

    # Google Gemini/Vertex AI configuration(text model)
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_DEFAULT_MODEL: Optional[str] = "gemini-3-pro-preview"
    GOOGLE_BASE_URL: Optional[str] = None
    GOOGLE_VIDEO_BASE_URL: Optional[str] = None
    GOOGLE_VERTEX_PROJECT_ID: Optional[str] = None
    GOOGLE_VERTEX_LOCATION: Optional[str] = None
    GOOGLE_VERTEX_ACCESS_TOKEN: Optional[str] = None
    GOOGLE_VERTEX_API_KEY: Optional[str] = None
    GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON: Optional[str] = None
    GOOGLE_VERTEX_SERVICE_ACCOUNT_PATH: Optional[str] = None

    # A Li YunOSSconfiguration
    ALIYUN_ACCESS_KEY_ID: Optional[str] = None
    ALIYUN_ACCESS_KEY_SECRET: Optional[str] = None
    ALIYUN_OSS_ENDPOINT: Optional[str] = None
    ALIYUN_OSS_BUCKET: Optional[str] = None
    ALIYUN_OSS_DOMAIN: Optional[str] = None

    # You Jian configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # log configuration
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True
    ENABLE_JSONL_LOGGING: bool = True
    JSONL_LOG_PATH: str = "logs/ai-video-studio.jsonl"
    LOG_BACKUP_COUNT: int = 7
    FEISHU_WEBHOOK_URL: Optional[str] = None

    # Rong Qi Nei Bu access after Duan De basic Di Zhi(Yong Yu Celery/Provider La Qu Ben Ji Shang Chuan image Deng Zi Yuan)
    INTERNAL_BACKEND_URL: Optional[str] = None

    # storyboard Tu Dong Tai prompt Ci(Sheng Tu Ren Wu interior An scene Pi Liang call LLM, Jie He script contextGeneration prompt)
    STORYBOARD_DYNAMIC_PROMPT_ENABLED: bool = False
    STORYBOARD_DYNAMIC_PROMPT_MAX_FRAMES_PER_CALL: int = 8
    STORYBOARD_DYNAMIC_PROMPT_MODEL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def _normalize_optional_str(value: Optional[str]) -> Optional[str]:
    """Trim whitespace and treat empty strings as None for optional secrets."""
    if value is None:
        return None
    value = value.strip()
    return value or None


# Gui Fan Hua Bu Fen can Xuan key, avoid ".env" in Liu Xia Kong Zi Fu Chuan when Wu Pan as configuration
settings.GOOGLE_API_KEY = _normalize_optional_str(settings.GOOGLE_API_KEY)
settings.OPENAI_API_KEY = _normalize_optional_str(settings.OPENAI_API_KEY)
settings.OPENAI_BASE_URL = _normalize_optional_str(settings.OPENAI_BASE_URL)
settings.CODEX_AUTH_PATH = _normalize_optional_str(settings.CODEX_AUTH_PATH)
settings.CODEX_RESPONSES_URL = _normalize_optional_str(settings.CODEX_RESPONSES_URL)
settings.CODEX_DEFAULT_MODEL = _normalize_optional_str(settings.CODEX_DEFAULT_MODEL)
settings.GOOGLE_BASE_URL = _normalize_optional_str(settings.GOOGLE_BASE_URL)
settings.GOOGLE_VIDEO_BASE_URL = _normalize_optional_str(settings.GOOGLE_VIDEO_BASE_URL)
settings.GOOGLE_VERTEX_PROJECT_ID = _normalize_optional_str(
    settings.GOOGLE_VERTEX_PROJECT_ID
)
settings.GOOGLE_VERTEX_LOCATION = _normalize_optional_str(
    settings.GOOGLE_VERTEX_LOCATION
)
settings.GOOGLE_VERTEX_ACCESS_TOKEN = _normalize_optional_str(
    settings.GOOGLE_VERTEX_ACCESS_TOKEN
)
settings.GOOGLE_VERTEX_API_KEY = _normalize_optional_str(settings.GOOGLE_VERTEX_API_KEY)
settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON = _normalize_optional_str(
    settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON
)
settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_PATH = _normalize_optional_str(
    settings.GOOGLE_VERTEX_SERVICE_ACCOUNT_PATH
)
settings.STABILITY_API_KEY = _normalize_optional_str(settings.STABILITY_API_KEY)
settings.KELING_API_KEY = _normalize_optional_str(settings.KELING_API_KEY)
settings.KELING_SECRET_KEY = _normalize_optional_str(settings.KELING_SECRET_KEY)
settings.JIMENG_API_KEY = _normalize_optional_str(settings.JIMENG_API_KEY)
settings.JIMENG_SECRET_KEY = _normalize_optional_str(settings.JIMENG_SECRET_KEY)
settings.MINIMAX_API_KEY = _normalize_optional_str(settings.MINIMAX_API_KEY)
settings.MINIMAX_GROUP_ID = _normalize_optional_str(settings.MINIMAX_GROUP_ID)
settings.DEEPSEEK_API_KEY = _normalize_optional_str(settings.DEEPSEEK_API_KEY)
settings.VOLCENGINE_API_KEY = _normalize_optional_str(settings.VOLCENGINE_API_KEY)
settings.VOLCENGINE_SECRET_KEY = _normalize_optional_str(settings.VOLCENGINE_SECRET_KEY)
settings.VOLCENGINE_REGION = _normalize_optional_str(settings.VOLCENGINE_REGION)
settings.INTERNAL_BACKEND_URL = _normalize_optional_str(settings.INTERNAL_BACKEND_URL)


def _is_container_env() -> bool:
    """Heuristic to detect containerized environments (Docker/K8s)."""
    return bool(os.getenv("KUBERNETES_SERVICE_HOST")) or os.path.exists("/.dockerenv")


def _looks_like_localhost(url: str | None) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return "localhost" in lowered or "127.0.0.1" in lowered


def _resolve_internal_backend_url(raw: Optional[str]) -> str:
    """
    Resolve a backend base URL that Celery workers/providers can reach.

    - Prefer explicit env/setting when it's not localhost inside a container.
    - When running in Docker/K8s without an explicit URL (or explicitly set
      to localhost), fall back to the service name used in docker-compose.
    - Default to localhost for bare-metal dev.
    """
    normalized = _normalize_optional_str(raw)
    if normalized:
        normalized = normalized.rstrip("/")
    container_default = (
        os.getenv("CONTAINER_BACKEND_URL") or "http://ai-video-backend:8000"
    )

    if _is_container_env():
        # in Rong Qi Li Bu Yao Shi Yong localhost, Celery worker need access after Duan Rong Qi
        if normalized and not _looks_like_localhost(normalized):
            return normalized
        return container_default

    return normalized or "http://localhost:8000"


# Rong Qi exterior default localhost, Rong Qi interior default docker-compose service, Yun Xu Xian Shi Fu Gai
settings.INTERNAL_BACKEND_URL = _resolve_internal_backend_url(
    settings.INTERNAL_BACKEND_URL
)

# Que Bao Shang Chuan Mu Lu Cun Zai
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
