from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.vector_store import seed_vector_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles background application startup and shutdown tasks,
    keeping main.py free of non-routing logic.
    """
    print("Initializing application dependencies...")
    try:
        seed_vector_db()
    except Exception as e:
        print(f"Initial database seeding skipped or failed: {e}")
        
    yield
    
    print("Shutting down application dependencies safely...")