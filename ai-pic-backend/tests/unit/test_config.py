"""
Ce Shi Huan Jing configuration
"""

import tempfile
from pathlib import Path

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
 """Ce Shi Huan Jing configuration"""

 # Xiang Mu Pei Zhi
 PROJECT_NAME: str = "AITu Pian Sheng ChengAPI - Ce Shi Huan Jing"
 VERSION: str = "1.0.0"
 API_V1_STR: str = "/api/v1"

 # An Quan Pei Zhi
 SECRET_KEY: str = "test-secret-key-not-for-production"
 ALGORITHM: str = "HS256"
 ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

 # test database configuration
 TEST_DATABASE_URL: str = "sqlite:///./test.db"

 # Nei Cun database(Geng Kuai De test)
 MEMORY_DATABASE_URL: str = "sqlite:///:memory:"

 # Redisconfiguration(Ce Shi Yong)
 REDIS_URL: str = "redis://localhost:6379/1" # use Bu Tong De database

 # CORSconfiguration
 ALLOWED_HOSTS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

 # file upload configuration
 UPLOAD_DIR: str = tempfile.gettempdir()
 MAX_FILE_SIZE: int = 10485760
 ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif"]

 # AIFu Wu Pei Zhi(Ce Shi Yongmock)
 AI_SERVICE_URL: str = "http://localhost:8000/mock"
 AI_API_KEY: str = "test-api-key"

 # OpenAIconfiguration(Ce Shi Yong)
 OPENAI_API_KEY: str = "test-openai-key"

 # Stability AIconfiguration(Ce Shi Yong)
 STABILITY_API_KEY: str = "test-stability-key"

 # test Te Ding configuration
 TESTING: bool = True
 DEBUG: bool = True

 # You Jian Pei Zhi(Ce Shi Yong)
 SMTP_HOST: str = "localhost"
 SMTP_PORT: int = 587
 SMTP_USER: str = "test@example.com"
 SMTP_PASSWORD: str = "test-password"

 class Config:
 env_file = ".env.test"
 case_sensitive = True


# create test set Shi Li
test_settings = TestSettings()


def get_test_database_url(use_memory: bool = False) -> str:
 """get test databaseURL"""
 if use_memory:
 return test_settings.MEMORY_DATABASE_URL
 return test_settings.TEST_DATABASE_URL


def get_test_upload_dir() -> Path:
 """get test upload Mu Lu"""
 test_dir = Path(tempfile.gettempdir()) / "ai_pic_test_uploads"
 test_dir.mkdir(exist_ok=True)
 return test_dir


def cleanup_test_files():
 """clean up test file"""
 import shutil

 test_dir = get_test_upload_dir()
 if test_dir.exists():
 shutil.rmtree(test_dir)

 # clean up test database file
 test_db_path = Path("test.db")
 if test_db_path.exists():
 test_db_path.unlink()
