from pydantic import BaseModel


class CountryDetailSchema(BaseModel):
    id: str
    name: str
    short_name: str | None
