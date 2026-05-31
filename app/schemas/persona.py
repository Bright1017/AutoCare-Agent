from pydantic import BaseModel, Field
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
    """
    The data contract model that maps live frontend complaints to Task B landmarks.
    """
    user_name: str = Field(default="Driver", description="Name of the stranded vehicle owner", example="Chioma")
    user_mood: str = Field(..., description="The driver's current emotional stress tier", example="anxious")
    vehicle_issue: str = Field(..., description="The localized mechanical failure string", example="Brakes failing")
    sector_name: str = Field(..., description="The structural Lagos neighborhood axis marker", example="Yaba")