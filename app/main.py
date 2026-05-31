import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import simulation, recommendation 

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
# Registers both routers with the main application instance to activate their endpoints
app.include_router(simulation.router)      
app.include_router(recommendation.router) 

@app.get("/HOME", summary="Root health status check", tags=["Root Health Check"])
def read_root():
    return {"message": "Welcome To AutoCare, Your Go-To Auto Repair Agent in Lagos!"}