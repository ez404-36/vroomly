from pydantic import BaseModel

from common.schemas.types import ID


class ChoiceFieldSchema(BaseModel):
	id: ID
	name: str


class ChoiceFieldWithParentSchema(ChoiceFieldSchema):
	parent: ChoiceFieldSchema
