from databases import Database
from sqlalchemy import MetaData

from config.settings import settings


def get_db_url():
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

DATABASE_URL = get_db_url()
metadata = MetaData()
database = Database(DATABASE_URL)
