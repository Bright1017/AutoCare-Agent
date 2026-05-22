from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.lifecycles import lifespan
from app.agents.recommender import generate_auto_recommendation

# 1. Initialize FastAPI, passing the external lifespan manager
app = FastAPI(
    title="AutoCare Agent Backend",
    description="Multi-Agent Simulation & Vector Recommendation Engine for Auto Care in Lagos",
    version="1.0.0",
    lifespan=lifespan
)

# 2. Strict JSON Input Schema
class UserComplaintRequest(BaseModel):
    vehicle_issue: str = Field(
        ..., 
        description="The explicit mechanical or electrical car problem statement.",
        example="My engine is making a loud knocking sound and overheating."
    )
    user_mood: str = Field(
        default="Anxious", 
        description="The emotional state or constraints of the user.",
        example="Stressed out, looking for quick reliable help without delays"
    )

# 3. Core Operational Endpoint
@app.post("/api/recommend", summary="Process complaint through Agent Pipeline")
async def analyze_and_recommend(payload: UserComplaintRequest):
    """
    Ingests user input complaints and triggers the two-tier agent pipeline.
    """
    if not payload.vehicle_issue.strip():
        raise HTTPException(status_code=400, detail="Vehicle issue text cannot be empty, abeg.")

    try:
        recommendation_plan = generate_auto_recommendation(
            vehicle_issue=payload.vehicle_issue,
            user_mood=payload.user_mood
        )
        
        return {
            "status": "success",
            "user_issue_processed": payload.vehicle_issue,
            "user_mood_captured": payload.user_mood,
            "recommendation": recommendation_plan
        }
        
    except Exception as e:
        print(f"Critical error routing request through agents: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Wahala encountered while compiling your recommendation plan. Please try again."
        )

# 4. Root Health Check Endpoint
@app.get("/", summary="Root health status check")
def read_root():
    return {"message": "AutoCare Agent Backend is running active on top gear!"}