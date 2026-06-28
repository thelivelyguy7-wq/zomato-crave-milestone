from dataclasses import dataclass
from .restaurant import Restaurant

@dataclass
class RecommendationResult:
    rank: int
    restaurant: Restaurant
    explanation: str
