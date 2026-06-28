from typing import Protocol, List
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.models.recommendation import RecommendationResult

class LLMClient(Protocol):
    """Protocol for LLM recommendation clients."""
    
    def get_recommendations(
        self, 
        preferences: UserPreferences, 
        candidates: List[Restaurant]
    ) -> List[RecommendationResult]:
        """
        Takes user preferences and candidate restaurants,
        returns ranked recommendations with explanations.
        Raises exceptions or returns empty/partial on failure.
        """
        ...
