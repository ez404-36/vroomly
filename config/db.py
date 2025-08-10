from typing import Any, Iterable

from databases import Database
from sqlalchemy import MetaData, create_engine, Select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings


def get_db_url():
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

DATABASE_URL = get_db_url()
metadata = MetaData()
database = Database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)

async_engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


def get_session() -> Session:
    return session_maker()

def get_async_session() -> AsyncSession:
    return async_session_maker()


async def session_fetch_one(session: AsyncSession, query: Select) -> Any:
    return (await session.scalars(query)).one()


async def session_fetch_all(session: AsyncSession, query: Select) -> Iterable[Any]:
    return (await session.scalars(query)).all()