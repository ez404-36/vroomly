from fastapi_utils.api_model import APIModel


class CountryDetailSchema(APIModel):
	id: str
	name: str
	short_name: str | None
