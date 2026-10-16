import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.config import settings
from app.schemas.persona import RecommendationRequest
from app.agents.recommender import generate_auto_recommendation

router = APIRouter(prefix="/api/recommend", tags=["AutoCare Recommendation Engine"])

async def require_supabase_user(authorization: str | None = Header(default=None)):
    """Validate the signed-in user's Supabase access token without exposing a server secret."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Supabase authentication is not configured.")

    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Please log in to request recommendations.")

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {token.strip()}",
                },
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Could not verify your AutoCare AI session.")

    if response.status_code in (401, 403):
        raise HTTPException(status_code=401, detail="Your session expired. Please log in again.")
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Could not verify your AutoCare AI session.")
    return response.json()

@router.post("/sector", status_code=status.HTTP_200_OK)
def get_localized_recommendations(
    payload: RecommendationRequest,
    user: dict = Depends(require_supabase_user),
):
    try:
        plan = generate_auto_recommendation(
            vehicle_issue=payload.vehicle_issue,
            user_mood=payload.user_mood,
            sector_name=payload.sector_name,
            user_name=payload.user_name,
        )
        return {
            "recommendation_plan": plan,
            "demo_mode": True,
            "notice": (
                "Demo only: the current catalog is Yelp-derived and its Lagos locations "
                "are synthetic. Providers and addresses are not verified."
            ),
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The recommendation service could not complete this request. Please try again later.",
        )
