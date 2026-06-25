"""应用配置模块 — 基于 pydantic-settings，自动从 .env / 环境变量读取。"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- 数据库 ----
    database_url: str = "sqlite+aiosqlite:///./learnloop.db"

    # ---- LLM: DeepSeek ----
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # ---- LLM: OpenAI / PPIO ----
    openai_api_key: str = ""
    openai_base_url: str = "https://api.ppio.cloud/v1"

    # ---- LLM: 智谱 ----
    zhipu_api_key: str = ""
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"

    # ---- LLM: MiMo ----
    mimo_api_key: str = ""
    mimo_base_url: str = "https://api.mimo.xiaomi.com/v1"

    # ---- 默认模型 ----
    default_model: str = "deepseek-chat"

    # ---- 应用 ----
    app_env: str = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me-in-production"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
