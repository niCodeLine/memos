"""Application settings loaded from environment variables.

This module keeps configuration in one place so the rest of the project does not
need to know whether values came from `.env`, Docker Compose, or the shell.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API and worker.

    Pydantic reads these fields from environment variables. The defaults are
    local-development friendly, while secrets and database values should come
    from `.env` or Docker Compose.
    """

    APP_NAME: str = "Memo"
    APP_ENV: str = "local"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ADMIN_BOOTSTRAP_TOKEN: str

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    WORKER_POLL_SECONDS: int = 30
    DEFAULT_TIMEZONE: str = "Europe/Berlin"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def postgres_dsn(self) -> str:
        """Build the connection string expected by psycopg2."""

        return (
            f"host={self.POSTGRES_HOST} "
            f"dbname={self.POSTGRES_DB} "
            f"user={self.POSTGRES_USER} "
            f"password={self.POSTGRES_PASSWORD} "
            f"port={self.POSTGRES_PORT}"
        )


# Imported by the API, services and worker so they all share the same config.
settings = Settings()
