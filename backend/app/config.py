from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Supply Chain Risk Assistant"
    frontend_origin: str = "http://localhost:5173"

    openai_api_key: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    news_api_key: str | None = None
    openweather_api_key: str | None = None
    un_comtrade_api_key: str | None = None
    kaggle_username: str | None = None
    kaggle_key: str | None = None
    port_data_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
