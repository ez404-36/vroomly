from pydantic import BaseModel


class CountryDetail(BaseModel):
    id: str
    name: str
    short_name: str | None
