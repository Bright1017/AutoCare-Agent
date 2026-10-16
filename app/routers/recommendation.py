import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config import settings
from app.schemas.persona import RecommendationRequest
from app.agents.recommender import generate_auto_recommendation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommend", tags=["AutoCare Recommendation Engine"])

# These are public Supabase client settings. Environment variables can override
# them for staging or a future project; the publishable key is not a secret.
SUPABASE_URL = settings.SUPABASE_URL or "https://riikxvssyacpotgxmrhs.supabase.co"
SUPABASE_PUBLIC_KEY = settings.SUPABASE_ANON_KEY or "sb_publishable_RdzzwB82RXjOKexUtJuvbg_4dnWjWFg"


def validate_supabase_user(authorization: str | None = Header(default=None)) -> dict:
    """Verify the driver's Supabase access token before running a recommendation."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in to get recommendations.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request = Request(
        f"{SUPABASE_URL.rstrip('/')}/auth/v1/user",
        headers={
            "apikey": SUPABASE_PUBLIC_KEY,
            "Authorization": authorization,
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=8) as response:
            user = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in (401, 403):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your sign-in session has expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from error
        logger.warning("Supabase token verification returned HTTP %s", error.code)
        raise HTTPException(status_code=502, detail="Could not verify your sign-in session.") from error
    except (URLError, TimeoutError) as error:
        logger.warning("Supabase token verification is unavailable: %s", error)
        raise HTTPException(status_code=503, detail="Sign-in verification is temporarily unavailable.") from error
    except (ValueError, OSError) as error:
        logger.warning("Could not read Supabase token verification response: %s", error)
        raise HTTPException(status_code=502, detail="Could not verify your sign-in session.") from error

    if not isinstance(user, dict) or not user.get("id"):
        raise HTTPException(status_code=401, detail="Your sign-in session is invalid.")
    return user


@router.post("/sector", status_code=status.HTTP_200_OK)
def get_localized_recommendations(
    payload: RecommendationRequest,
    user: dict = Depends(validate_supabase_user),
):
    """Return Lagos demo recommendations for a signed-in driver."""
    try:
        recommendation_plan = generate_auto_recommendation(
            vehicle_issue=payload.vehicle_issue,
            user_mood=payload.user_mood,
            sector_name=payload.sector_name,
            user_name=payload.user_name,
        )
        return {
            "recommendation_plan": recommendation_plan,
            "notice": "Demo catalog only: provider identities and Lagos locations are not verified.",
        }
    except Exception:
        logger.exception("Recommendation request failed for user %s", user.get("id"))
        raise HTTPException(
            status_code=503,
            detail="The recommendation engine is temporarily unavailable. Please try again.",
        )
