from pydantic import BaseModel, UUID4


class CountryDetail(BaseModel):
    id: UUID4
    name: str
    full_name: str
