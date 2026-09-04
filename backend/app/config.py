from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Forex Monitor"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/forex.db"

    # Exchange Rate APIs (free tiers)
    exchangerate_api_key: str = ""  # https://www.exchangerate-api.com/ - 1500 req/month free
    openexchange_api_key: str = ""  # https://openexchangerates.org/ - 1000 req/month free

    # News APIs (free tiers)
    gnews_api_key: str = ""  # https://gnews.io/ - 100 req/day free
    newsdata_api_key: str = ""  # https://newsdata.io/ - 200 req/day free

    # Scheduling
    exchange_rate_interval_minutes: int = 30
    news_fetch_interval_minutes: int = 60

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
