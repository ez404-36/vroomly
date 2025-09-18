from datetime import date

from pydantic import UUID4, BaseModel


class UserDetail(BaseModel):
    id: UUID4
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None

    class Config:
        from_attributes = True
