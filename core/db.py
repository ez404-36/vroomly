from typing import Any, Iterable

from sqlalchemy import MetaData
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.settings import settings

DATABASE_URL = settings.db.url
metadata = MetaData()


class OrmDatabase:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.async_engine = create_async_engine(self.db_url)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False)

    async def fetch_one(self, query: Select) -> Any:
        async with self.get_async_session() as session:
            return await self.session_fetch_one(session, query)

    async def fetch_all(self, query: Select) -> Any:
        async with self.get_async_session() as session:
            return await self.session_fetch_all(session, query)

    @staticmethod
    async def session_fetch_one(session: AsyncSession, query: Select) -> Any:
        return (await session.scalars(query)).one()

    @staticmethod
    async def session_fetch_all(session: AsyncSession, query: Select) -> Iterable[Any]:
        return (await session.scalars(query)).all()

    def get_async_session(self) -> AsyncSession:
        return self.async_session_maker()


database = OrmDatabase(DATABASE_URL)
