from pydantic import BaseModel, UUID4


class CountryDetail(BaseModel):
    id: UUID4
    prefix: str
    name: str
    short_name: str | None
