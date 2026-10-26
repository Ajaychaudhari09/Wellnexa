from typing import List, Union
from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "WellNexa AI"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "dev_wellnexa_secure_random_secret_key_minimum_32_chars_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173", "http://localhost:8000", "*"]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        elif isinstance(v, list):
            return v
        return ["*"]

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "wellnexa"
    POSTGRES_PASSWORD: str = "wellnexa_secure_password"
    POSTGRES_DB: str = "wellnexa_db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./wellnexa.db"
    SYNC_DATABASE_URL: str = "sqlite:///./wellnexa.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    # Storage
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "uploads")
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB

    # AI & Embeddings
    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # OCR
    OCR_ENGINE: str = "tesseract"
    ENCRYPTION_KEY: str = ""

    # SMTP
    SMTP_HOST: str = Field(default="localhost", validation_alias=AliasChoices("EMAIL_HOST", "SMTP_HOST"))
    SMTP_PORT: int = Field(default=587, validation_alias=AliasChoices("EMAIL_PORT", "SMTP_PORT"))
    SMTP_USER: str = Field(default="", validation_alias=AliasChoices("EMAIL_USER", "SMTP_USER"))
    SMTP_PASSWORD: str = Field(default="", validation_alias=AliasChoices("EMAIL_PASS", "SMTP_PASSWORD"))
    SMTP_FROM: str = Field(default="no-reply@wellnexa.ai", validation_alias=AliasChoices("EMAIL_FROM_ADDRESS", "SMTP_FROM"))
    SMTP_USE_TLS: bool = True
    EMAIL_SECURE: Union[bool, None] = None
    EMAIL_FROM_NAME: str = "WellNexa"
    SUPPORT_EMAIL: str = "support@wellnexa.ai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in the environment or .env file")
if settings.ENVIRONMENT.lower() in {"production", "prod"} and not settings.ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY must be configured in production")
