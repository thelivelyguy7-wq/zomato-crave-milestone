import pytest
import json
from unittest.mock import MagicMock, patch

from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.services.llm.groq_client import GroqClient
from src.services.recommendation import RecommendationService
from src.config import Settings

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")
    return Settings()

@pytest.fixture
def mock_openai_client(monkeypatch, mock_settings):
    with patch("src.services.llm.groq_client.OpenAI") as mock_openai:
        # Patch get_settings to return our mock_settings that has the API key
        with patch("src.services.llm.groq_client.get_settings", return_value=mock_settings):
            yield mock_openai

@pytest.fixture
def sample_candidates():
    return [
        Restaurant(id="1", name="R1", location="L1", cuisine="C1", rating=4.5, cost_for_two=500, budget_tier="medium"),
        Restaurant(id="2", name="R2", location="L1", cuisine="C2", rating=4.0, cost_for_two=600, budget_tier="medium"),
    ]

@pytest.fixture
def sample_prefs():
    return UserPreferences(location="L1", budget="medium")

def test_groq_client_missing_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "   ") # Empty
    from src.config import get_settings
    get_settings.cache_clear() # Ensure it re-reads env
    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
        GroqClient()

def test_groq_client_success(mock_openai_client, sample_candidates, sample_prefs):
    # Setup mock response
    mock_instance = mock_openai_client.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "recommendations": [
                {"rank": 1, "restaurant_id": "2", "explanation": "Good C2"},
                {"rank": 2, "restaurant_id": "1", "explanation": "Best C1"}
            ]
        })))
    ]
    mock_instance.chat.completions.create.return_value = mock_response
    
    client = GroqClient()
    results = client.get_recommendations(sample_prefs, sample_candidates)
    
    assert len(results) == 2
    assert results[0].rank == 1
    assert results[0].restaurant.id == "2"
    assert results[0].explanation == "Good C2"
    
    assert results[1].rank == 2
    assert results[1].restaurant.id == "1"

def test_groq_client_filters_invalid_ids(mock_openai_client, sample_candidates, sample_prefs):
    # Setup mock response with hallucinated ID
    mock_instance = mock_openai_client.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "recommendations": [
                {"rank": 1, "restaurant_id": "999", "explanation": "Fake ID"},
                {"rank": 2, "restaurant_id": "1", "explanation": "Valid ID"}
            ]
        })))
    ]
    mock_instance.chat.completions.create.return_value = mock_response
    
    client = GroqClient()
    results = client.get_recommendations(sample_prefs, sample_candidates)
    
    # Should only return the valid one
    assert len(results) == 1
    assert results[0].restaurant.id == "1"

def test_groq_client_invalid_json(mock_openai_client, sample_candidates, sample_prefs):
    # Setup mock response with malformed JSON
    mock_instance = mock_openai_client.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="This is not json"))
    ]
    mock_instance.chat.completions.create.return_value = mock_response
    
    client = GroqClient()
    with pytest.raises(ValueError, match="Invalid JSON response"):
        client.get_recommendations(sample_prefs, sample_candidates)

def test_recommendation_service_fallback():
    # Test that RecommendationService falls back to rating sort when LLM fails or is missing
    repo_mock = MagicMock()
    repo_mock.get_all.return_value = [
        Restaurant(id="1", name="R1", location="L1", cuisine="C1", rating=4.0, cost_for_two=500, budget_tier="medium"),
        Restaurant(id="2", name="R2", location="L1", cuisine="C2", rating=4.5, cost_for_two=600, budget_tier="medium"),
    ]
    
    # 1. No LLM Client
    service = RecommendationService(repo_mock, llm_client=None)
    prefs = UserPreferences(location="L1", budget="medium")
    results = service.recommend(prefs)
    
    # Rating sort (R2 > R1)
    assert len(results) == 2
    assert results[0].restaurant.id == "2"
    assert results[0].explanation == "Matches your preferences based on rating and filters."
    
    # 2. LLM Client fails
    llm_mock = MagicMock()
    llm_mock.get_recommendations.side_effect = ValueError("LLM Error")
    service2 = RecommendationService(repo_mock, llm_client=llm_mock)
    results2 = service2.recommend(prefs)
    
    assert len(results2) == 2
    assert results2[0].restaurant.id == "2"
