from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    ENCODING: str = 'utf-8'

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / '.env',
    )


settings = Settings()   # noqa
