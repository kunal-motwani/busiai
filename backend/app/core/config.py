"""BusiAI application configuration using pydantic-settings."""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """BusiAI application settings."""

    # Application
    APP_NAME: str = "BusiAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # LLM
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"  # Backward-compatible legacy setting.
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    # Query limits
    QUERY_TIMEOUT_SECONDS: int = 30
    MAX_RESULT_ROWS: int = 10000

    model_config = {
        "env_file": (PROJECT_ROOT / ".env", ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
