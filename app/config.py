from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY") #type: ignore
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database.db")

class Defaults(BaseSettings):
    DEFAULT_CATEGORY_NAME: str = os.getenv("DEFAULT_CATEGORY_NAME", "Uncategorized")
    DEFAULT_CATEGORY_DESCRIPTION: str = os.getenv("DEFAULT_CATEGORY_DESCRIPTION", "All your uncategorized expenses")
    DEFAULT_CATEGORY_TAG: str = os.getenv("DEFAULT_CATEGORY_TAG", "Black")


default_categories = Defaults()
settings = Settings()