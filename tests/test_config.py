"""Tests for application configuration."""

from src.config import Settings, get_settings


def test_settings_defaults():
    """Verify all defaults match the architecture spec (Groq / Llama 3 70B)."""
    settings = Settings(_env_file=None)
    assert settings.llm_model == "llama3-70b-8192"
    assert settings.llm_base_url == "https://api.groq.com/openai/v1"
    assert settings.llm_temperature == 0.3
    assert settings.max_candidates == 20
    assert settings.groq_api_key is None
    assert settings.has_api_key is False


def test_settings_strips_api_key():
    """API key should be trimmed of surrounding whitespace."""
    settings = Settings(GROQ_API_KEY="  gsk_test-key  ", _env_file=None)
    assert settings.groq_api_key == "gsk_test-key"
    assert settings.has_api_key is True


def test_empty_api_key_treated_as_none():
    """A blank or whitespace-only API key should be treated as absent."""
    settings = Settings(GROQ_API_KEY="   ", _env_file=None)
    assert settings.groq_api_key is None
    assert settings.has_api_key is False


def test_max_candidates_invalid_defaults_to_twenty():
    """Zero or negative MAX_CANDIDATES should fall back to 20."""
    settings = Settings(MAX_CANDIDATES=0, _env_file=None)
    assert settings.max_candidates == 20


def test_max_candidates_capped_at_fifty():
    """MAX_CANDIDATES above 50 should be capped."""
    settings = Settings(MAX_CANDIDATES=1000, _env_file=None)
    assert settings.max_candidates == 50


def test_temperature_clamped():
    """Temperature should be clamped to [0.0, 2.0]."""
    settings_low = Settings(LLM_TEMPERATURE=-1.0, _env_file=None)
    assert settings_low.llm_temperature == 0.0

    settings_high = Settings(LLM_TEMPERATURE=5.0, _env_file=None)
    assert settings_high.llm_temperature == 2.0


def test_get_settings_does_not_crash_without_api_key():
    """get_settings() must not raise when GROQ_API_KEY is unset."""
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.llm_model == "llama3-70b-8192"
