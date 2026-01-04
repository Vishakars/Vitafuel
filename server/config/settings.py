from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_here_change_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Database - Local MongoDB
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "vitafuel")

    # App
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    
    # Nutrition API
    usda_api_key: str = os.getenv("USDA_API_KEY", "DEMO_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    spoonacular_api_key: str | None = os.getenv("SPOONACULAR_API_KEY")

    class Config:
        env_file = ".env"

# Global instance for direct imports
settings = Settings()

@lru_cache(maxsize=1)
def get_settings() -> "Settings":
    return Settings()