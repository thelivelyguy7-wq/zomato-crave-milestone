import json
from src.services.prompt_builder import PromptBuilder
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

def test_build_system_prompt():
    prompt = PromptBuilder.build_system_prompt()
    assert "You are a restaurant recommendation assistant" in prompt
    assert "ONLY recommend restaurants from the provided list" in prompt
    assert '"recommendations": [' in prompt
    assert "No markdown fences" in prompt

def test_build_user_prompt():
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        min_rating=4.0,
        cuisine="Indian",
        additional_preferences="Spicy food",
        top_k=5
    )
    
    candidates = [
        Restaurant(
            id="123",
            name="Spice Route",
            location="Bangalore",
            cuisine="Indian, Mughlai",
            rating=4.5,
            cost_for_two=600,
            budget_tier="medium"
        )
    ]
    
    prompt = PromptBuilder.build_user_prompt(prefs, candidates)
    
    # Check preferences are included
    assert "Location: Bangalore" in prompt
    assert "Budget: medium" in prompt
    assert "Cuisine: Indian" in prompt
    assert "Minimum rating: 4.0" in prompt
    assert "Additional: Spicy food" in prompt
    assert "Return top 5 recommendations" in prompt
    
    # Extract JSON part
    json_str_start = prompt.find("Restaurants (JSON array):\n") + len("Restaurants (JSON array):\n")
    json_str_end = prompt.rfind("\n\nReturn top")
    
    json_str = prompt[json_str_start:json_str_end]
    parsed_json = json.loads(json_str)
    
    assert len(parsed_json) == 1
    assert parsed_json[0]["restaurant_id"] == "123"
    assert parsed_json[0]["name"] == "Spice Route"
    assert "address" not in parsed_json[0] # Excluded to save tokens
