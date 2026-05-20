import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- APPLICATION SETTINGS ---
    APP_NAME: str = "AutoCare-Agent"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # --- LLM ENGINE SETTINGS ---
    # The OpenAI API key will be pulled automatically from your .env file
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4-turbo"
    TEMPERATURE: float = 0.6
    
    # --- DATABASE CONFIGURATIONS ---
    # Path where ChromaDB will persist its vector collections locally
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    YELP_DATA_PATH: str = "./data/filtered_yelp_auto_shops.json"
    
    # Enable reading from a .env file located in the project root folder
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Prevents crashing if extra variables exist in the system
    )

# Instantiate a singleton settings object to import across modules
settings = Settings()