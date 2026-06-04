"""Представление подобранных по VIN данных ТС.

Слой представления: человекочитаемые метки (двигатель/КПП/привод/кузов) и сборка
``TrimChoiceSchema`` с готовой строкой ``description`` для опции селектора.
Не содержит ни доступа к данным, ни оркестрации подбора.
"""

from typing import TYPE_CHECKING

from apps.vehicles.api.user_vehicle.schemas import GuessByVinResponseSchema
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.enums import CarBodyType, CarDriveType
from apps.vehicles.models.node.body_node import CarBodyNode
from apps.vehicles.models.node.engine_node import EngineNode
from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from apps.vehicles.models.vehicle.enums import VehicleEngineType, VehicleTransmissionType
from common.schemas.choices_utils import to_choice_field
from common.schemas.fields import (
	TrimChoiceSchema,
	TrimEngineSchema,
	TrimTransmissionSchema,
)

if TYPE_CHECKING:
	from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfoSchema

_ENGINE_TYPE_LABELS: dict[VehicleEngineType, str] = {
	VehicleEngineType.PETROL: 'Бензин',
	VehicleEngineType.DIESEL: 'Дизель',
	VehicleEngineType.ELECTRO: 'Электро',
	VehicleEngineType.GAS: 'Газ',
	VehicleEngineType.ATMOSPHERIC: 'Атмосферный',
	VehicleEngineType.TURBO: 'Турбо',
}

_TRANSMISSION_TYPE_LABELS: dict[VehicleTransmissionType, str] = {
	VehicleTransmissionType.MANUAL: 'МКПП',
	VehicleTransmissionType.AUTO: 'АКПП',
	VehicleTransmissionType.ROBOT: 'Робот',
	VehicleTransmissionType.VARIATOR: 'Вариатор',
}

_DRIVE_TYPE_LABELS: dict[CarDriveType, str] = {
	CarDriveType.FRONT: 'Передний',
	CarDriveType.BACK: 'Задний',
	CarDriveType.FULL: 'Полный',
}

_BODY_TYPE_LABELS: dict[CarBodyType, str] = {
	CarBodyType.SEDAN: 'Седан',
	CarBodyType.HATCHBACK: 'Хэтчбек',
	CarBodyType.SW: 'Универсал',
	CarBodyType.COUPE: 'Купе',
	CarBodyType.CUV: 'Кроссовер',
	CarBodyType.SUV: 'Внедорожник',
	CarBodyType.LIFTBACK: 'Лифтбек',
	CarBodyType.ROADSTER: 'Родстер',
	CarBodyType.VAN: 'Фургон',
	CarBodyType.MINIVAN: 'Минивэн',
	CarBodyType.PICKUP_TRUCK: 'Пикап',
	CarBodyType.MINIBUS: 'Микроавтобус',
	CarBodyType.TARGA: 'Тарга',
	CarBodyType.FASTBACK: 'Фастбэк',
	CarBodyType.LANDAU: 'Ландо',
	CarBodyType.CUV_COUPE: 'Кросс-купе',
	CarBodyType.SHOOTING_BRAKE: 'Шутинг-брейк',
}


def engine_type_label(engine_type: VehicleEngineType | None) -> str | None:
	"""Собрать человекочитаемую строку из IntFlag-типа двигателя."""
	if not engine_type:
		return None
	parts = [label for flag, label in _ENGINE_TYPE_LABELS.items() if flag in engine_type]
	return ', '.join(parts) if parts else None


def drive_type_label(drive_types: CarDriveType | list[CarDriveType] | None) -> str | None:
	"""Собрать строку из (возможно множественного) типа привода."""
	if not drive_types:
		return None
	values = drive_types if isinstance(drive_types, list) else [drive_types]
	parts = [_DRIVE_TYPE_LABELS[value] for value in values if value in _DRIVE_TYPE_LABELS]
	return ', '.join(parts) if parts else None


def _build_engine_schema(
	engine: EngineNode,
	engine_type_text: str | None,
) -> TrimEngineSchema:
	"""Собрать структурированные данные о двигателе для схемы комплектации."""
	return TrimEngineSchema(
		name=engine.name,
		volume=engine.volume,
		power=engine.power,
		type=engine_type_text,
		torque=engine.torque,
	)


def _build_transmission_schema(
	transmission: CarTransmissionNode,
	transmission_type_text: str | None,
) -> TrimTransmissionSchema:
	"""Собрать структурированные данные о КПП для схемы комплектации."""
	return TrimTransmissionSchema(
		name=transmission.name,
		type=transmission_type_text,
		gears=transmission.gears,
	)


def _engine_description_part(engine: EngineNode, engine_type_text: str | None) -> str:
	"""Сформировать часть описания по двигателю (объём/мощность/тип)."""
	engine_part = f'{engine.volume / 1000:.1f}' if engine.volume else engine.name
	if engine.power:
		engine_part = f'{engine_part} ({engine.power} л.с.)'
	if engine_type_text:
		engine_part = f'{engine_part} {engine_type_text}'
	return engine_part


def _transmission_description_part(
	transmission: CarTransmissionNode,
	transmission_type_text: str | None,
) -> str:
	"""Сформировать часть описания по КПП (тип/число передач)."""
	transmission_part = transmission_type_text or transmission.name
	if transmission.gears:
		transmission_part = f'{transmission_part} {transmission.gears}'
	return transmission_part


def trim_to_choice(trim: CarTrim) -> TrimChoiceSchema:
	"""Собрать ``TrimChoiceSchema`` с расширенными данными о комплектации.

	Формирует структурированные данные о двигателе/КПП/приводе/кузове и
	готовую человекочитаемую строку ``description`` для опции селектора,
	например: ``1.6 (110 л.с.) Бензин · АКПП 6 · Передний · Седан``.
	"""
	engine: EngineNode | None = trim.engine
	transmission: CarTransmissionNode | None = trim.transmission
	body: CarBodyNode | None = trim.body

	engine_type_text = engine_type_label(engine.type) if engine is not None else None
	transmission_type_text = (
		_TRANSMISSION_TYPE_LABELS.get(transmission.type) if transmission is not None else None
	)
	drive_label = drive_type_label(transmission.drive_types) if transmission is not None else None
	body_label = _BODY_TYPE_LABELS.get(body.type) if body is not None else None

	engine_schema = _build_engine_schema(engine, engine_type_text) if engine is not None else None
	transmission_schema = (
		_build_transmission_schema(transmission, transmission_type_text) if transmission is not None else None
	)

	description_parts: list[str] = []
	if engine is not None:
		description_parts.append(_engine_description_part(engine, engine_type_text))
	if transmission is not None:
		description_parts.append(_transmission_description_part(transmission, transmission_type_text))
	if drive_label:
		description_parts.append(drive_label)
	if body_label:
		description_parts.append(body_label)

	description = ' · '.join(description_parts) if description_parts else trim.name

	return TrimChoiceSchema(
		id=trim.id,
		name=trim.name,
		parent=to_choice_field(trim.generation),
		description=description,
		engine=engine_schema,
		transmission=transmission_schema,
		drive_type=drive_label,
		body_type=body_label,
	)


def trims_to_choices(trims: list[CarTrim]) -> list[TrimChoiceSchema]:
	"""Конвертировать список ``CarTrim`` в список ``TrimChoiceSchema``."""
	return [trim_to_choice(trim) for trim in trims]


def to_guess_by_vin_response(
	guess: 'GuessCommonCarInfoSchema',
	car_info: CarInfoByVinDataSchema,
) -> GuessByVinResponseSchema:
	"""Собрать ответ ``GET /vehicles/guess_by_vin`` из подбора и сырых данных VIN.

	Подобранные из БД бренд/модель/поколения/комплектации берутся из ``guess``,
	а сам VIN/год/цвет — из сырых данных VIN-провайдера ``car_info``.
	"""
	return GuessByVinResponseSchema(
		brand=guess.brand,
		model=guess.model,
		generations=guess.generations,
		trims=guess.trims,
		vin=car_info.vin,
		year=car_info.year,
		color=car_info.color,
	)
