import os
from fastapi import FastAPI, HTTPException, Depends, Body, Security 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import settings
from app.lifecycles import lifespan
from app.agents.recommender import generate_auto_recommendation
from app.core.security import validate_api_key


app = FastAPI(
    title="AutoCare Agent Backend",
    description="Multi-Agent Simulation & Vector Recommendation Engine for Auto Care in Lagos",
    version="1.0.0",
    lifespan=lifespan
)

# 2. Global CORS Policy Setup
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Injecting API Key Input Box into Swagger Docs natively
def custom_openapi():
    """Generates a custom OpenAPI schema adding the API-Key form to Swagger."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Define the security scheme structure natively
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "AutoCare",
            "description": "Enter your application secret key to unlock the endpoints."
        }
    }
    
    # This array forces Swagger to attach the key to the requests when made
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi


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
    api_key: str = Security(validate_api_key) 
):
    if not complaint.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty, abeg.")

    try:
        recommendation_plan = generate_auto_recommendation(
            vehicle_issue=complaint,
            user_mood="Anxious/Stressed"  
        )
        
        return {
            "status": "success",
            "user_issue_processed": complaint,
            "recommendation": recommendation_plan
        }
        
    except Exception as e:
        print(f"Critical error sending request to the agents: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Wahala encountered while compiling your recommendation plan. Please try again."
        )

@app.get("/", summary="Root health status check")
def read_root():
    return {"message": "AutoCare Agent Backend is running active on top gear!"}