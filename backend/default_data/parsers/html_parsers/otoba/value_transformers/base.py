from pathlib import Path
from typing import Any, Callable, Iterable

from sqlalchemy import ColumnElement, or_, true

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from core.models import AutoSchemaBase

from ..utils import find_first_number_in_text


class OtobaRuValueBaseTransformer:
	"""
	Преобразует данные на сайте в данные для объекта
	"""

	int_fields: Iterable[str] = []
	fields_map: dict[str, str] = {}

	bool_map = {
		'нет': False,
		'-': False,
		'да': True,
	}

	def __init__(
		self,
		tags_data: dict[str, str],
		page_uri: Path,
		brand: VehicleBrand | None,
		concern: VehicleConcern | None,
	):
		"""
		:param tags_data: собранные в словарь данные из таблицы об агрегате;
		:param page_uri: URI страницы, которую парсим. Нужно для логирования
		"""

		assert brand or concern, f'Не удалось опрелить бренд на странице {page_uri}'

		self.tags_data = tags_data
		self.page_uri = page_uri
		self.brand = brand
		self.concern = concern

	async def run(self) -> dict[str, Any]:
		output = {}

		for orig_key, orig_value in self.tags_data.items():
			output.update(await self.run_for_field(orig_key, orig_value))

		await self.set_default_values(output)

		return output

	async def set_default_values(self, output: dict[str, Any]):
		pass

	async def get_field(self, orig_key: str) -> str:
		return self.fields_map.get(orig_key)

	async def run_for_field(self, orig_key: str, orig_value: str) -> dict[str, Any]:
		"""
		:param orig_key: Оригинальное название тега/поля из таблицы характеристик
		:param orig_value: Оригинальное значение тега/поля из таблицы характеристик

		:return: dict[поле, значение] для сохранения в БД
		"""
		field_data = {}

		field = await self.get_field(orig_key)
		if not field:
			"""Игнорируем поля, не указанные в fields_map"""
			return field_data

		value = orig_value

		parse_method: Callable | None = getattr(self, f'parse_{field}', None)

		if parse_method:
			field_data.update(await parse_method(value))
		elif field in self.int_fields:
			field_data.update({field: self.to_int(value)})
		elif value.lower() in self.bool_map:
			field_data.update({field: self.to_bool(value)})

		return field_data

	@classmethod
	def to_bool(cls, value: str | None) -> bool | None:
		"""
		Преобразует строку в булево значение.
		:return True/False, если преобразование возможно, иначе None
		"""

		if value is None:
			return None
		return cls.bool_map.get(value.lower())

	@staticmethod
	def to_int(value: str) -> int | None:
		return find_first_number_in_text(value)

	def brand_or_concern_condition(self, model: type[AutoSchemaBase]) -> ColumnElement[bool]:
		if self.brand and self.concern:
			return or_(model.brand_id == self.brand.id, model.concern_id == self.concern.id)
		elif self.brand:
			return model.brand_id == self.brand.id
		elif self.concern:
			return model.concern_id == self.concern.id
		else:
			return true()
