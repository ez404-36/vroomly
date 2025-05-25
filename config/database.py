from typing import Iterable, Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config.settings import settings


def get_db_url():
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

def get_async_session() -> AsyncSession:
    return async_session_maker()


async def fetch_one(session: AsyncSession, query: Select) -> Any:
    return (await session.scalars(query)).one()


async def fetch_all(session: AsyncSession, query: Select) -> Iterable[Any]:
    return (await session.scalars(query)).all()