from fastapi import APIRouter, Security, status, HTTPException
from fastapi.security import APIKeyHeader
from app.config import settings
from app.schemas.persona import RecommendationRequest
from app.agents.recommender import generate_auto_recommendation

# router setup for all recommendation-related endpoints, including the full multi-agent pipeline that ingests user complaints and location to produce localized mechanic recommendations. This modular design allows us to cleanly separate the core logic of the recommendation engine from the API layer, while also enforcing strict security protocols using custom API keys.
router = APIRouter(prefix="/api/recommend", tags=["AutoCare Recommendation Engine"])

# Setup the exact custom API key header expected by your middleware layout
api_key_header = APIKeyHeader(name="AutoCare", auto_error=False)

def validate_key(api_key: str = Security(api_key_header)):
    """
    Enforces secure access using the CUSTOM PLATFORM TOKEN.
    """
    if not settings.APP_API_KEY:
        raise HTTPException(status_code=500, detail="Application API security key is unconfigured.")
    if api_key != settings.APP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AutoCare API-Key header.")
    return api_key

@router.post("/sector", status_code=status.HTTP_200_OK)
def get_localized_recommendations(payload: RecommendationRequest, token: str = Security(validate_key)):
    """
    this takes stranded Lagos driver typing, "My car is overheating." The RECOMMENDATION Agent finds nearby mechanics.
    Then, the Digital Twin (USER-SIMULATOR) steps in, mimicking that exact driver(USER) to text-test each workshop first.
    The Concierge reviews the simulated results, picks the perfect fit, and drops an instant rescue plan.
    """
    try:
        # Executes the fully-wired two-stage pipeline function
        action_plan_markdown = generate_auto_recommendation(
            vehicle_issue=payload.vehicle_issue,
            user_mood=payload.user_mood,
            sector_name=payload.sector_name,
            user_name=payload.user_name
        )
        
        # Return the final markdown text wrapped in a clean response object
        return {"recommendation_plan": action_plan_markdown}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing multi-turn concierge coordination layer: {str(e)}"
        )