from datetime import date

from pydantic import BaseModel, UUID4


class UserDetail(BaseModel):
    id: UUID4
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None

    class Config:
        from_attributes = True
