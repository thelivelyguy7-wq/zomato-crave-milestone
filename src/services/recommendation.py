import logging
from typing import List, Optional

from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResult
from src.data.repository import RestaurantRepository
from src.services.filter import RestaurantFilter
from src.services.llm.base import LLMClient

logger = logging.getLogger(__name__)

class RecommendationService:
    """Orchestrates the recommendation process."""
    
    def __init__(self, repository: RestaurantRepository, llm_client: Optional[LLMClient] = None):
        self.repository = repository
        self.filter_service = RestaurantFilter()
        self.llm_client = llm_client

    def recommend(self, preferences: UserPreferences) -> List[RecommendationResult]:
        """
        Orchestrates filtering and LLM recommendation.
        Falls back to Phase 1 generic sorting if LLM fails or is unavailable.
        """
        all_restaurants = self.repository.get_all()
        candidates = self.filter_service.filter_candidates(preferences, all_restaurants)
        
        if not candidates:
            return []
            
        if self.llm_client:
            logger.info("Calling LLM client for ranking and explanations...")
            try:
                results = self.llm_client.get_recommendations(preferences, candidates)
                if results:
                    # Enforce top_k in case LLM returned more
                    return results[:preferences.top_k]
                else:
                    logger.warning("LLM returned empty results, falling back to rating sort.")
            except Exception as e:
                logger.error(f"LLM failed, falling back to rating sort. Error: {e}")
                
        # Phase 1 / Fallback: generic explanation and rating-based ordering
        logger.info("Using rating-based fallback for recommendations.")
        results = []
        for i, restaurant in enumerate(candidates):
            results.append(
                RecommendationResult(
                    rank=i + 1,
                    restaurant=restaurant,
                    explanation="Matches your preferences based on rating and filters."
                )
            )
            
        return results[:preferences.top_k]
