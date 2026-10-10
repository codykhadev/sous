from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOUS_")

    database_url: str = "postgresql+psycopg://sous:sous@localhost:5432/sous"
    static_dir: Path | None = None


settings = Settings()
