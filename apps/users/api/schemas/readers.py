from datetime import date

from pydantic import BaseModel


class UserDetail(BaseModel):
    id: str
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None
