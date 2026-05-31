from fastapi import APIRouter, Security, status, HTTPException
from fastapi.security import APIKeyHeader
from app.config import settings
from app.schemas.persona import TaskASimulationPayload
from app.agents.user_simulator import simulate_user_review

# router setup for all simulation-related endpoints, including Task A's digital user behavior simulation and Task B's master concierge planner. This modular design allows us to cleanly separate the core logic of spinning up user digital twins from the API layer, while also enforcing strict security protocols using custom API keys.
router = APIRouter(prefix="/api/simulation", tags=[" Digital User Simulation"])

# Setup the exact custom API key header expected by middleware layout
api_key_header = APIKeyHeader(name="AutoCare", auto_error=False)

def validate_key(api_key: str = Security(api_key_header)):
    """
    Enforces secure access using your custom platform tokens.
    """
    if not settings.APP_API_KEY:
        raise HTTPException(status_code=500, detail="Application API security key is unconfigured.")
    if api_key != settings.APP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AutoCare API-Key header.")
    return api_key

@router.post("/evaluate", status_code=status.HTTP_200_OK)
def evaluate_custom_shop(payload: TaskASimulationPayload, token: str = Security(validate_key)):
    """
    Creates a fictional driver—like someone panicked over a broken CAR or ANY CAR ISSUE—pair them with a real workshop's data.
    The AGENT steps into that driver's shoes and predicts exactly what star rating and written review they would leave.
    """
    # this will return a dictionary with "predicted_rating" and "simulated_review" keys as defined in Task A template
    simulation_result = simulate_user_review(payload)
    
    # Structural verification check to guarantee keys are never missing from response payload
    if "predicted_rating" not in simulation_result or "simulated_review" not in simulation_result:
        raise HTTPException(
            status_code=500, 
            detail="The simulation engine failed to return the exact parseable JSON schema keys."
        )
        
    return simulation_result