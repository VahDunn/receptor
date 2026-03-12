from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    database_url: str = Field(..., alias="DATABASE_URL")
    chad_api_key: str = Field(..., alias="CHAD_API_KEY")
    chad_url: str = Field(..., alias="CHAD_URL")
    yookassa_shop_id: str = Field(..., alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: str = Field(..., alias="YOOKASSA_SECRET_KEY")
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
