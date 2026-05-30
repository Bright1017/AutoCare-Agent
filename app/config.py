import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- APPLICATION SETTINGS ---
    APP_NAME: str = "AutoCare-Agent"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # --- SECURITY SETTINGS ---
    APP_API_KEY: Optional[str] = None
    
    # --- LLM ENGINE SETTINGS ---
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama3-8b-8192"
    TEMPERATURE: float = 0.2
    
    # --- DATABASE CONFIGURATIONS ---
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    YELP_DATA_PATH: str = "./data/filtered_yelp_auto_shops.json"
    
    # Enable reading from a .env file located in the project root folder
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )
    # pydantic's BaseSettings will automatically read the .env file and populate these fields based on the keys defined in the .env. The 'extra="ignore"' setting allows the application to ignore any additional environment variables that are not explicitly defined in this Settings class, preventing potential errors from unexpected variables.
    @property
    def IS_GROQ(self) -> bool:
        model = self.LLM_MODEL.lower()
        return "llama" in model or "groq" in model or "mixtral" in model

    @property
    def LLM_API_KEY(self) -> Optional[str]:
        return self.GROQ_API_KEY if self.IS_GROQ else self.OPENAI_API_KEY

    @property
    def LLM_BASE_URL(self) -> Optional[str]:
        if self.IS_GROQ:
            return "https://api.groq.com/openai/v1"
        return None

# Instantiate a singleton settings object to import across modules
settings = Settings()