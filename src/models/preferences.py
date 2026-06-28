from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

BudgetTier = Literal["low", "medium", "high"]

class UserPreferences(BaseModel):
    location: str = Field(..., min_length=1)
    budget: BudgetTier
    cuisine: Optional[str] = None
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: Optional[str] = None
    top_k: int = Field(default=5, gt=0)

    @field_validator("location")
    @classmethod
    def strip_location(cls, v: str) -> str:
        return v.strip()

    @field_validator("additional_preferences")
    @classmethod
    def sanitize_preferences(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        # Truncate to 500 characters
        v = v[:500]
        # Basic tag stripping could be added here if needed, but Streamlit escapes by default
        return v

    @field_validator("top_k", mode="before")
    @classmethod
    def cap_top_k(cls, v: int) -> int:
        if v <= 0:
            return 5
        return min(v, 50)
