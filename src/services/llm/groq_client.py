import json
import logging
from typing import List, Dict, Any

from openai import OpenAI

from src.config import get_settings
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.models.recommendation import RecommendationResult
from src.services.llm.base import LLMClient
from src.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

class GroqClient(LLMClient):
    """Groq API client (Llama 3 70B) for restaurant recommendations."""

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.has_api_key:
            raise ValueError("GROQ_API_KEY is missing. Cannot initialize GroqClient.")
            
        # Using OpenAI Python client pointing to Groq's API
        self.client = OpenAI(
            api_key=self.settings.groq_api_key,
            base_url=self.settings.llm_base_url
        )

    def get_recommendations(
        self, 
        preferences: UserPreferences, 
        candidates: List[Restaurant]
    ) -> List[RecommendationResult]:
        """Calls Groq API to rank candidates and generate explanations."""
        if not candidates:
            return []

        sys_prompt = PromptBuilder.build_system_prompt()
        user_prompt = PromptBuilder.build_user_prompt(preferences, candidates)

        try:
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.settings.llm_temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty response from Groq API")
                return []
                
            return self._parse_response(content, candidates)
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise

    def _parse_response(self, content: str, candidates: List[Restaurant]) -> List[RecommendationResult]:
        """Parses JSON response and maps back to Restaurant objects."""
        # Fast lookup map
        candidate_map = {r.id: r for r in candidates}
        
        try:
            # Sometimes LLMs wrap JSON in markdown fences even with json_object format
            if content.strip().startswith("```json"):
                content = content.strip()[7:]
                if content.endswith("```"):
                    content = content[:-3]
            
            data = json.loads(content)
            recs_data = data.get("recommendations", [])
            
            results = []
            for item in recs_data:
                rest_id = item.get("restaurant_id")
                rank = item.get("rank")
                explanation = item.get("explanation", "Matches your preferences.")
                
                # Validation
                if not rest_id or rest_id not in candidate_map:
                    logger.warning(f"LLM hallucinated or returned invalid restaurant_id: {rest_id}")
                    continue
                    
                restaurant = candidate_map[rest_id]
                try:
                    rank = int(rank) if rank else len(results) + 1
                except ValueError:
                    rank = len(results) + 1
                    
                results.append(
                    RecommendationResult(
                        rank=rank,
                        restaurant=restaurant,
                        explanation=explanation
                    )
                )
                
            # Sort by rank to ensure correctness
            results.sort(key=lambda x: x.rank)
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}\nContent: {content}")
            raise ValueError("Invalid JSON response from LLM") from e
