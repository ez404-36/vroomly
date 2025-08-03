from databases import Database
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config.settings import settings


def get_db_url():
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL)
metadata = MetaData()
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

database = Database(DATABASE_URL)

def get_async_session() -> AsyncSession:
    return async_session_maker()
