from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    name: str

    model_config = SettingsConfigDict(env_prefix="DB_")

    @property
    def url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class LibretranslateSettings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(env_prefix="LIBRETRANSLATE_")

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()   # noqa
    libretranslate: LibretranslateSettings = LibretranslateSettings()   # noqa

    encoding: str = 'utf-8'

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / '.env',
        extra='ignore',
    )


settings = Settings()   # noqa
