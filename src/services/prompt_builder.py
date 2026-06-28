import json
from typing import List, Dict
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

class PromptBuilder:
    """Constructs prompts for the LLM."""

    @staticmethod
    def build_system_prompt() -> str:
        """Returns the system instruction."""
        return (
            "You are a restaurant recommendation assistant for a Zomato-like app.\n"
            "You will receive a user's preferences and a numbered list of real restaurants from our database.\n"
            "Rules:\n"
            "- ONLY recommend restaurants from the provided list (use restaurant_id).\n"
            "- Rank by best fit: location match, budget tier, cuisine, rating, and additional preferences.\n"
            "- Write concise, friendly explanations (1-2 sentences each).\n"
            "- Respond with valid JSON matching this schema:\n"
            "{\n"
            '  "recommendations": [\n'
            '    {\n'
            '      "rank": 1,\n'
            '      "restaurant_id": "...",\n'
            '      "explanation": "..."\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "- No markdown fences."
        )

    @staticmethod
    def build_user_prompt(preferences: UserPreferences, candidates: List[Restaurant]) -> str:
        """Returns the user prompt combining preferences and compact candidate JSON."""
        
        # Compact candidate JSON (id, name, location, cuisine, rating, cost_for_two, budget_tier)
        compact_candidates = []
        for r in candidates:
            compact_candidates.append({
                "restaurant_id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisine": r.cuisine,
                "rating": r.rating,
                "cost_for_two": r.cost_for_two,
                "budget_tier": r.budget_tier
            })
            
        candidates_json = json.dumps(compact_candidates, indent=2)
        
        return (
            "User preferences:\n"
            f"- Location: {preferences.location}\n"
            f"- Budget: {preferences.budget}\n"
            f"- Cuisine: {preferences.cuisine or 'any'}\n"
            f"- Minimum rating: {preferences.min_rating}\n"
            f"- Additional: {preferences.additional_preferences or 'none'}\n\n"
            "Restaurants (JSON array):\n"
            f"{candidates_json}\n\n"
            f"Return top {preferences.top_k} recommendations ranked best to worst."
        )
