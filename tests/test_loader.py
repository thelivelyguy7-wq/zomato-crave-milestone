import pytest
from src.data.loader import parse_rating, parse_cost, get_budget_tier

def test_parse_rating():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("NEW") == 0.0
    assert parse_rating("-") == 0.0
    assert parse_rating("") == 0.0
    assert parse_rating(None) == 0.0
    assert parse_rating("3.5") == 3.5

def test_parse_cost():
    assert parse_cost("800") == 800
    assert parse_cost("1,200") == 1200
    assert parse_cost("1,000,000") == 1000000
    assert parse_cost("") == 0
    assert parse_cost(None) == 0

def test_get_budget_tier():
    assert get_budget_tier(200) == "low"
    assert get_budget_tier(300) == "low"
    assert get_budget_tier(301) == "medium"
    assert get_budget_tier(500) == "medium"
    assert get_budget_tier(700) == "medium"
    assert get_budget_tier(701) == "high"
    assert get_budget_tier(1500) == "high"
