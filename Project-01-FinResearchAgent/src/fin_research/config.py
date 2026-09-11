from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    data_mode: Literal["demo", "live"] = "demo"
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./finresearch.db"
    qdrant_url: str = "http://localhost:6333"
    fred_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    llm_api_key: str | None = None
    sec_user_agent: str = Field(
        default="FinResearchAgent research@example.com",
        description="SEC asks automated clients to identify themselves.",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

