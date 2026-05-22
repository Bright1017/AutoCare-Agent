from pydantic import BaseModel, Field

class UserPersona(BaseModel):
    """
    Schema defining the dynamic behavioral profile state 
    used to hydrate the User Simulator / Digital Twin for ANY user.
    """
    name: str = Field(..., description="The name of the user being simulated (e.g., Tunde, Chioma, Chika)")
    persona_mood: str = Field(..., description="The user's current emotional state or service delivery expectations")
    vehicle_issue: str = Field(..., description="The explicit diagnostic trouble or complaint text input by the user")
    location: str = Field(default="Lagos, Nigeria", description="Primary operational location city context")