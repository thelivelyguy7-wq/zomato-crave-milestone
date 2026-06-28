from typing import List, Optional
from pydantic import BaseModel
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResult

class HealthResponse(BaseModel):
    status: str
    version: str

class LocationsResponse(BaseModel):
    locations: List[str]

class CuisinesResponse(BaseModel):
    cuisines: List[str]

# Reusing UserPreferences for Request
class RecommendationRequest(UserPreferences):
    pass

class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    fallback_used: bool = False
    recommendations: List[RecommendationResult]
