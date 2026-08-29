from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
        return (
            f"host={self.POSTGRES_HOST} "
            f"dbname={self.POSTGRES_DB} "
            f"user={self.POSTGRES_USER} "
            f"password={self.POSTGRES_PASSWORD} "
            f"port={self.POSTGRES_PORT}"
        )


settings = Settings()
