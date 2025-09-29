from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema
from core.models import AutoSchemaBase


def to_choice_field(instance: AutoSchemaBase) -> ChoiceFieldSchema:
	name_field = None
	for field in ('name', 'title'):
		if hasattr(instance, field):
			name_field = field
			break

	return ChoiceFieldSchema(id=instance.id, name=getattr(instance, name_field))


def to_choice_field_with_parent(instance: AutoSchemaBase, parent_attr: str) -> ChoiceFieldWithParentSchema:
	parent_field = getattr(instance, parent_attr, None)
	if parent_field:
		raise AttributeError(f'Модель {instance} не имеет атрибута {parent_attr}')

	return ChoiceFieldWithParentSchema(
		**to_choice_field(instance).model_dump(),
		parent=to_choice_field(parent_field),
	)


def to_choice_field_list(instances: list[AutoSchemaBase]) -> list[ChoiceFieldSchema]:
	return [
		to_choice_field(instance)
		for instance in instances
	]

def to_choice_field_with_parent_list(instances: list[AutoSchemaBase], parent_attr: str) -> list[ChoiceFieldWithParentSchema]:
	return [
		to_choice_field_with_parent(instance, parent_attr)
		for instance in instances
	]
