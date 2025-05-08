import uuid

from pydantic.v1 import UUID4
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID4] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower().split('model')[0] + 's'
