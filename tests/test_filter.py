import pytest
from src.models.restaurant import Restaurant
from src.models.preferences import UserPreferences
from src.services.filter import RestaurantFilter
from src.config import Settings

@pytest.fixture
def sample_restaurants():
    return [
        Restaurant(id="1", name="Cheap Eats", location="Bangalore", cuisine="Indian", rating=3.5, cost_for_two=200, budget_tier="low"),
        Restaurant(id="2", name="Fancy Italian", location="Bangalore", cuisine="Italian", rating=4.5, cost_for_two=1500, budget_tier="high"),
        Restaurant(id="3", name="Good Chinese", location="Delhi", cuisine="Chinese", rating=4.0, cost_for_two=600, budget_tier="medium"),
        Restaurant(id="4", name="Okay Indian", location="Bangalore", cuisine="North Indian", rating=3.0, cost_for_two=600, budget_tier="medium"),
        Restaurant(id="5", name="Great Indian", location="Bangalore", cuisine="South Indian", rating=4.8, cost_for_two=500, budget_tier="medium"),
    ]

@pytest.fixture
def filter_service(monkeypatch):
    monkeypatch.setenv("MAX_CANDIDATES", "3")
    return RestaurantFilter()

def test_filter_location(sample_restaurants, filter_service):
    prefs = UserPreferences(location="Delhi", budget="medium")
    filtered = filter_service.filter_candidates(prefs, sample_restaurants)
    assert len(filtered) == 1
    assert filtered[0].id == "3"

def test_filter_budget(sample_restaurants, filter_service):
    prefs = UserPreferences(location="Bangalore", budget="medium")
    filtered = filter_service.filter_candidates(prefs, sample_restaurants)
    # Should find 'Okay Indian' and 'Great Indian'
    assert len(filtered) == 2
    assert {r.id for r in filtered} == {"4", "5"}

def test_filter_rating(sample_restaurants, filter_service):
    prefs = UserPreferences(location="Bangalore", budget="medium", min_rating=4.5)
    filtered = filter_service.filter_candidates(prefs, sample_restaurants)
    # Only 'Great Indian' has rating >= 4.5 in medium budget
    assert len(filtered) == 1
    assert filtered[0].id == "5"

def test_filter_cuisine(sample_restaurants, filter_service):
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="south indian")
    filtered = filter_service.filter_candidates(prefs, sample_restaurants)
    assert len(filtered) == 1
    assert filtered[0].id == "5"

def test_filter_cap_and_sort(sample_restaurants, filter_service):
    # Add more restaurants to trigger cap
    more_restaurants = sample_restaurants + [
        Restaurant(id="6", name="A Indian", location="Bangalore", cuisine="Indian", rating=4.1, cost_for_two=500, budget_tier="medium"),
        Restaurant(id="7", name="B Indian", location="Bangalore", cuisine="Indian", rating=4.2, cost_for_two=500, budget_tier="medium"),
    ]
    prefs = UserPreferences(location="Bangalore", budget="medium")
    filtered = filter_service.filter_candidates(prefs, more_restaurants)
    
    # We set MAX_CANDIDATES to 3 in fixture
    assert len(filtered) == 3
    # Should be sorted by rating desc: 4.8 (id 5), 4.2 (id 7), 4.1 (id 6)
    assert filtered[0].id == "5"
    assert filtered[1].id == "7"
    assert filtered[2].id == "6"

def test_filter_zero_matches(sample_restaurants, filter_service):
    prefs = UserPreferences(location="Mumbai", budget="high")
    filtered = filter_service.filter_candidates(prefs, sample_restaurants)
    assert len(filtered) == 0
