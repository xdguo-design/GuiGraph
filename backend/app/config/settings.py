"""全局配置管理（基于 pydantic-settings）。"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file() -> str:
    """根据 APP_ENV 环境变量确定配置文件（使用绝对路径）。"""
    env = os.getenv("APP_ENV", "dev").lower()
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if env == "prod":
        filename = ".env.prod"
    elif env == "test":
        filename = ".env.test"
    else:
        filename = ".env.dev"
    return os.path.join(backend_dir, filename)


class Settings(BaseSettings):
    """应用全局配置。"""

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== 应用基础 =====
    APP_NAME: str = "GuiGraph"
    APP_ENV: str = "dev"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # ===== 数据库 =====
    DATABASE_URL: str = "sqlite+aiosqlite:///./guigraph.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ===== JWT =====
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # ===== 微信 OAuth =====
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_REDIRECT_URI: str = "http://localhost:10011/api/v1/auth/wechat/callback"

    # ===== MinIO =====
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False

    # ===== RAGFlow =====
    RAGFLOW_URL: str = "http://localhost:8080"
    RAGFLOW_API_KEY: Optional[str] = None

    # ===== GraphRAG =====
    GRAPH_RAG_URL: str = "http://localhost:8081"

    # ===== Jenkins =====
    JENKINS_DEFAULT_URL: str = "http://localhost:8080/jenkins"
    JENKINS_DEFAULT_TOKEN: Optional[str] = None

    # ===== CORS =====
    CORS_ORIGINS: list[str] = ["http://localhost:10010", "http://localhost:3000", "http://127.0.0.1:10010"]

    # ===== 日志 =====
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（缓存单例）。"""
    return Settings()


settings = get_settings()
