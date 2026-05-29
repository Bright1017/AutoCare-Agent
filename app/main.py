import os
from fastapi import FastAPI, HTTPException, Body, Security 
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.agents.recommender import generate_auto_recommendation
from app.core.security import validate_api_key
from app.core.cache import AutoCareCacheService, generate_cache_key
from app.core.location import identify_closest_lagos_sector

# dotenv is loaded in app/config.py, so we can directly access settings from there
app = FastAPI(
    title="AutoCare Agent Backend",
    description="Multi-Agent Simulation & Vector Recommendation Engine for Auto Care in Lagos",
    version="1.0.0"
)

# Global CORS Policy Setup
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Operational Endpoint
@app.post(
    "/api/recommend", 
    summary="Process complaint through Agent Pipeline"
)
async def analyze_and_recommend(
    complaint: str = Body(
        ..., 
        embed=True, 
        description="The raw vehicle issue or text complaint from the user.",
        example="My engine is making a loud knocking sound and overheating, and I am stressed out."
    ),
    latitude: float = Body(0.0, embed=True),
    longitude: float = Body(0.0, embed=True),
    authenticated_key: str = Security(validate_api_key) 
):
    if not complaint.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty, abeg.")

    # 1. Spatial router mapping (Maps coordinates to Yaba, Lekki Phase 1, or Ikeja)
    sector_name, _ = identify_closest_lagos_sector(latitude, longitude)

    # 2. Key Generation for Cache tracking
    cache_key = generate_cache_key("recommend", vehicle_issue=complaint, sector=sector_name)
    
    # 3. High-speed RAM Interceptor Check
    cached_plan = AutoCareCacheService.get(cache_key)
    if cached_plan:
        print(f"Serving instant resolution blueprint for: {cache_key}")
        return {
            "status": "success",
            "cached": True,
            "sector_routed": sector_name,
            "user_issue_processed": complaint,
            "recommendation": cached_plan
        }

    # 4. Fallback execution on cache miss
    try:
        print(f"Computing live recommendations bounded to sector: {sector_name}")
        
        # generate the recommendation plan through the multi-agent pipeline
        recommendation_plan = generate_auto_recommendation(
            vehicle_issue=complaint,
            user_mood="Anxious/Stressed",
            sector_name=sector_name
        )
        
        # just-in-time cache population for future identical requests
        AutoCareCacheService.set(cache_key, recommendation_plan)
        
        return {
            "status": "success",
            "cached": False,
            "sector_routed": sector_name,
            "user_issue_processed": complaint,
            "recommendation": recommendation_plan
        }
        
    except Exception as e:
        print(f"Critical error sending request to the agents: {e}")
        raise HTTPException(
            status_code=500, 
            detail="i encountered one wahala while compiling your recommendation plan. Please try again later."
        )

@app.get("/", summary="Root health status check")
def read_root():
    return {"message": "Welcome To AutoCare, Your Go-To Auto Repair Agent in Lagos!"}