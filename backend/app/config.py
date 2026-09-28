from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Ticket Triage Agent"

    database_url: str = "sqlite:///./ticket_triage.db"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    confidence_threshold: float = 0.60
    duplicate_threshold: float = 0.85

    chroma_path: str = "./chroma_data"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
