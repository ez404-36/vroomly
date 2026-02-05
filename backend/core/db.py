from typing import Any, Iterable

from core.settings import settings
from sqlalchemy import MetaData, Select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

DATABASE_URL = settings.db.url
metadata = MetaData()


class OrmDatabase:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.async_engine: AsyncEngine = create_async_engine(self.db_url)
        self.async_session_maker = async_sessionmaker(
            self.async_engine, expire_on_commit=False
        )

    async def fetch_one(self, query: Select, raise_exc=False) -> Any:
        async with self.get_async_session() as session:
            return await self.session_fetch_one(session, query, raise_exc)

    async def fetch_first(self, query: Select) -> Any:
        async with self.get_async_session() as session:
            return await self.session_fetch_first(session, query)

    async def fetch_all(self, query: Select) -> Any:
        async with self.get_async_session() as session:
            return await self.session_fetch_all(session, query)

    @staticmethod
    async def session_fetch_one(session: AsyncSession, query: Select, raise_exc=False) -> Any:
        result = await session.scalars(query)
        if raise_exc:
            return result.one()
        else:
            return result.one_or_none()

    @staticmethod
    async def session_fetch_first(session: AsyncSession, query: Select) -> Any:
        result = await session.scalars(query)
        return result.first()

    @staticmethod
    async def session_fetch_all(session: AsyncSession, query: Select) -> Iterable[Any]:
        return (await session.scalars(query)).all()

    def get_async_session(self) -> AsyncSession:
        return self.async_session_maker()


database = OrmDatabase(DATABASE_URL)
