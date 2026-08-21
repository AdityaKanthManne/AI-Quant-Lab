from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./data/forecasts.db"
    duckdb_path: Path = Path("data/analytics.duckdb")
    mlflow_tracking_uri: str = "./mlruns"
    polymarket_base_url: str = "https://gamma-api.polymarket.com"
    fred_api_key: str | None = None
    llm_provider: str = "deterministic"
    model_version: str = "multi-agent-v0.1.0"
    request_timeout_seconds: float = Field(default=15.0, gt=0)
    probability_epsilon: float = Field(default=1e-6, gt=0, lt=0.01)


@lru_cache
def get_settings() -> Settings:
    return Settings()
