"""Application configuration."""
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Glyph"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./glyph.db"
    )

    # JWT
    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OAuth Providers
    google_client_id: str = ""
    google_client_secret: str = ""
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    x_client_id: str = ""
    x_client_secret: str = ""

    # WebAuthn
    webauthn_rp_id: str = "localhost"
    webauthn_rp_name: str = "Glyph"
    webauthn_origin: str = "http://localhost:8000"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Assurance Levels
    assurance_level_alpha: int = 40
    assurance_level_beta: int = 70
    assurance_level_gamma: int = 85


settings = Settings()
