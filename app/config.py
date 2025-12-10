from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import secrets

model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore",
    env_file_ignore_missing=True,
) #type: ignore


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://postgres:changeme@localhost:5432/expense_db"
    TEST_DATABASE_URL: str = "postgresql://test_user:test_password@localhost:5433/test_db"

    model_config = model_config


class Defaults(BaseSettings):
    DEFAULT_CATEGORY_NAME: str = "uncategorized"
    DEFAULT_CATEGORY_DESCRIPTION: str = "All your uncategorized expenses"
    DEFAULT_CATEGORY_TAG: str = "Black"

    model_config = model_config


settings = Settings()  # type: ignore
default_categories = Defaults()
