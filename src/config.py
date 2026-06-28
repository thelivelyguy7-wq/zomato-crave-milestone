"""Application configuration loaded from environment variables."""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Runtime settings for the recommendation system.

    All settings are loaded from environment variables (or a `.env` file).
    See `.env.example` for the full list with documentation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Groq / LLM ---------------------------------------------------------
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    llm_model: str = Field(default="llama3-70b-8192", validation_alias="LLM_MODEL")
    llm_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        validation_alias="LLM_BASE_URL",
    )
    llm_temperature: float = Field(default=0.3, validation_alias="LLM_TEMPERATURE")

    # --- Filter / pipeline ---------------------------------------------------
    max_candidates: int = Field(default=20, validation_alias="MAX_CANDIDATES")

    # --- Validators ----------------------------------------------------------
    @field_validator("groq_api_key", mode="before")
    @classmethod
    def strip_api_key(cls, value: object) -> str | None:
        """Strip whitespace from the API key; treat blank as absent."""
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return str(value).strip() or None

    @field_validator("max_candidates")
    @classmethod
    def validate_max_candidates(cls, value: int) -> int:
        """Ensure MAX_CANDIDATES is between 1 and 50."""
        if value <= 0:
            return 20
        return min(value, 50)

    @field_validator("llm_temperature")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        """Clamp temperature to [0.0, 2.0]."""
        return max(0.0, min(2.0, value))

    # --- Convenience ---------------------------------------------------------
    @property
    def has_api_key(self) -> bool:
        """Return True if a Groq API key is configured."""
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    The result is cached so repeated calls within the same process
    always return the same instance.
    """
    settings = Settings()
    if not settings.has_api_key:
        logger.warning(
            "GROQ_API_KEY is not set. "
            "LLM-powered recommendations will be unavailable until Phase 2."
        )
    return settings
