from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Zynapse"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_change_me") # CHANGE THIS!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    class Config:
        case_sensitive = True

settings = Settings()

