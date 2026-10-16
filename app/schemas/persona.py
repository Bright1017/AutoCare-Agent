from pydantic import BaseModel, Field
from typing import Literal
from app.schemas.shop import MechanicShop

class UserPersona(BaseModel):
    """
    Represents the digital twin driver profile structure for Task A simulation scoring.
    """
    name: str = Field(..., description="Name of the driver", example="Tunde")
    persona_mood: str = Field(..., description="The driver's current emotional state", example="panicked")
    vehicle_issue: str = Field(..., description="The raw automotive complaint", example="Engine knocking")
    location: str = Field(default="Lagos, Nigeria", description="E.g., Yaba, Lekki Phase 1, Ikeja")


class TaskASimulationPayload(BaseModel):
    """
    here is rigid container payload required strictly by Task A's isolated endpoints.
    """
    user_persona: UserPersona
    shop_data: MechanicShop


class RecommendationRequest(BaseModel):
    """Validated request contract for the Lagos mechanic recommendation demo."""
    user_name: str = Field(default="Driver", max_length=100)
    user_mood: str = Field(default="concerned", max_length=40)
    vehicle_issue: str = Field(..., min_length=5, max_length=500)
    sector_name: Literal["Yaba", "Lekki Phase 1", "Ikeja"]
