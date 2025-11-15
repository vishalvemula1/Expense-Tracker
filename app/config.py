from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore",
)
class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=1)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///database.db"
    
    model_config = model_config

class Defaults(BaseSettings):
    DEFAULT_CATEGORY_NAME: str = "Uncategorized"
    DEFAULT_CATEGORY_DESCRIPTION: str = "All your uncategorized expenses"
    DEFAULT_CATEGORY_TAG: str = "Black"
    
    model_config = model_config

settings = Settings() #type: ignore
default_categories = Defaults()