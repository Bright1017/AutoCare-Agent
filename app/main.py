import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import simulation, recommendation

app = FastAPI(
    title="AutoCare Agent Backend",
    description="Recommendation engine for AutoCare AI drivers",
    version="1.1.0"
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "https://autocare-ai-site.onrender.com"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "AutoCare"],
)
app.include_router(simulation.router)
app.include_router(recommendation.router)

@app.get("/HOME", summary="Root health status check", tags=["Root Health Check"])
def read_root():
    return {"message": "AutoCare AI recommendation API is online."}
