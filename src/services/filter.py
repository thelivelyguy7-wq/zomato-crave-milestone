import logging
from typing import List

from src.config import get_settings
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

class RestaurantFilter:
    """Filters a list of restaurants based on user preferences."""

    def __init__(self):
        self.settings = get_settings()

    def filter_candidates(
        self,
        preferences: UserPreferences,
        restaurants: List[Restaurant],
    ) -> List[Restaurant]:
        """Apply deterministic filtering to candidates."""
        
        filtered = restaurants

        # 1. Location match (case-insensitive substring or exact match)
        # Assuming location might contain city and locality, we check if pref location is in it
        location_lower = preferences.location.lower()
        filtered = [
            r for r in filtered
            if location_lower in r.location.lower()
        ]

        # 2. Minimum rating
        if preferences.min_rating > 0.0:
            filtered = [
                r for r in filtered
                if r.rating >= preferences.min_rating
            ]

        # 3. Cuisine match (if specified)
        if preferences.cuisine:
            cuisine_lower = preferences.cuisine.lower()
            filtered = [
                r for r in filtered
                if cuisine_lower in r.cuisine.lower()
            ]

        # 4. Budget match
        filtered = [
            r for r in filtered
            if r.budget_tier == preferences.budget
        ]

        # 5. Cap and Sort
        # First sort by rating descending, then by name for stable sort
        filtered.sort(key=lambda r: (-r.rating, r.name))

        # Deduplicate by name (keep highest rated)
        seen_names = set()
        deduped = []
        for r in filtered:
            name_key = r.name.strip().lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                deduped.append(r)
        
        filtered = deduped
        
        # Apply cap (default 20 before LLM processing)
        # Use top_k if it's less than max_candidates, otherwise cap at max_candidates
        # Wait, architecture says "if results > MAX_CANDIDATES (e.g. 20), sort by rating desc and truncate"
        # The prompt builder takes up to MAX_CANDIDATES to pass to LLM, and LLM returns top_k.
        cap = self.settings.max_candidates
        capped_results = filtered[:cap]

        logger.info(
            f"Filter matched {len(filtered)} candidates. "
            f"Capped to {len(capped_results)} before LLM."
        )

        return capped_results
