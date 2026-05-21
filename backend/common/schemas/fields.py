from fastapi_utils.api_model import APIModel

from common.schemas.types import ID


class ChoiceFieldSchema(APIModel):
	id: ID
	name: str


class ChoiceFieldWithParentSchema(ChoiceFieldSchema):
	parent: ChoiceFieldSchema
