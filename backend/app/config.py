from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOUS_", env_file=ENV_FILE, extra="ignore")

    database_url: str = "postgresql+psycopg://sous:sous@localhost:5432/sous"
    test_database_url: str = "postgresql+psycopg://sous:sous@localhost:5432/sous_test"
    static_dir: Path | None = None


settings = Settings()
