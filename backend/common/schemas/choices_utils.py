from common.schemas.choices_mixin import ChoicesMixin
from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema
from core.models import AutoSchemaBase


def to_choice_field(instance: AutoSchemaBase) -> ChoiceFieldSchema:
	def _get_name_field() -> str | None:
		for _field in ('name', 'title'):
			if hasattr(instance, _field):
				return _field
		return None

	name_field = _get_name_field() or '__str__'
	name: str = getattr(instance, name_field)
	return ChoiceFieldSchema(id=instance.id, name=name)


def to_choice_field_with_parent(instance: AutoSchemaBase, parent_attr: str) -> ChoiceFieldWithParentSchema:
	parent_field = getattr(instance, parent_attr, None)
	if not parent_field:
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

def to_choice_field_with_parent_list(
    instances: list[AutoSchemaBase],
    parent_attr: str,
) -> list[ChoiceFieldWithParentSchema]:
	return [
		to_choice_field_with_parent(instance, parent_attr)
		for instance in instances
	]


def enum_to_choices_list(enum_cls: type[ChoicesMixin]) -> list[ChoiceFieldSchema]:
	if not hasattr(enum_cls, 'choices'):
		return []

	return [
		ChoiceFieldSchema(id=el[0], name=el[1]) for el in enum_cls.choices()
	]
