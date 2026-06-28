from dataclasses import dataclass
from typing import Optional

@dataclass
class Restaurant:
    id: str
    name: str
    location: str           # city / locality
    cuisine: str            # may be comma-separated
    rating: float           # 0.0 – 5.0
    cost_for_two: int       # numeric, local currency
    budget_tier: str        # low | medium | high (derived)
    address: Optional[str] = None
    votes: Optional[int] = None
