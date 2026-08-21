from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Autonomous Quantitative Research Copilot"
    research_copilot_home: Path = Path("research_projects")
    database_url: str | None = None
    qdrant_url: str | None = None
    mlflow_tracking_uri: str | None = None
    execution_timeout_seconds: int = 300


settings = Settings()

