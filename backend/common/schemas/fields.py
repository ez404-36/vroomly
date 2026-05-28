from fastapi_utils.api_model import APIModel

from common.schemas.types import ID


class ChoiceFieldSchema(APIModel):
	id: ID
	name: str


class ChoiceFieldWithParentSchema(ChoiceFieldSchema):
	parent: ChoiceFieldSchema


class TrimEngineSchema(APIModel):
	"""Краткие характеристики двигателя комплектации."""

	name: str
	volume: int | None = None
	power: int | None = None
	type: str | None = None
	torque: int | None = None


class TrimTransmissionSchema(APIModel):
	"""Краткие характеристики коробки передач комплектации."""

	name: str
	type: str | None = None
	gears: int | None = None


class TrimChoiceSchema(ChoiceFieldWithParentSchema):
	"""Комплектация с расширенными данными для понятного выбора в селекторе.

	Помимо ``id``/``name``/``parent`` (поколение) содержит структурированные
	сведения о двигателе, коробке передач, типе привода и кузове, а также
	готовую человекочитаемую строку ``description`` для отображения в опции.
	"""

	description: str
	engine: TrimEngineSchema | None = None
	transmission: TrimTransmissionSchema | None = None
	drive_type: str | None = None
	body_type: str | None = None
