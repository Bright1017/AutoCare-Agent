import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- APPLICATION SETTINGS ---
    APP_NAME: str = "AutoCare-Agent"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # --- LLM ENGINE SETTINGS ---
    # Made Optional so Pydantic doesn't throw a fit when using free alternatives like Groq
    OPENAI_API_KEY: Optional[str] = None
    
    # Groq Key so your agent environment recognizes it
    GROQ_API_KEY: Optional[str] = None
    
    # Updated default to Groq's high-speed open-source Llama model
    LLM_MODEL: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.2
    
    # --- DATABASE CONFIGURATIONS ---
    # Path where ChromaDB will persist its vector collections locally
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    YELP_DATA_PATH: str = "./data/filtered_yelp_auto_shops.json"
    
    # Enable reading from a .env file located in the project root folder
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignore any extra environment variables safely
    )

# Instantiate a singleton settings object to import across modules
settings = Settings()