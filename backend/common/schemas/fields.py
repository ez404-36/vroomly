from uuid import UUID

from pydantic import BaseModel


class ChoiceFieldSchema(BaseModel):
	id: UUID | str
	name: str


class ChoiceFieldWithParentSchema(ChoiceFieldSchema):
	parent: ChoiceFieldSchema
