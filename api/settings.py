'''
Best way I found to deal with the env variables.
'''
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432 # PostgreSQL default
    
    REDIS_PORT: int = 6379 # Redis default
    REDIS_HOST: str
    REDIS_PASSWORD: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore',
    )


settings = Settings()