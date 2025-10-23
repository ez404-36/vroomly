import asyncio
import pickle
import re
import logging
from pathlib import Path
from typing import Any, Callable, Iterable, Literal

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select

from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.enums import (
	VehicleEngineGRMType,
	VehicleEnginePhaseRegulatorType,
	VehicleEngineType,
	VehicleTransmissionType,
)
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from common.utils.generators import generate_code
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from core.constants import BACKEND_DIR
from core.db import database

NUMBER_PATTERN = r'\d+'
VehicleNodeType = Literal['engine', 'transmission']

logger = logging.getLogger('OtobaRuHtmlParser')

def find_first_number_in_text(text: str) -> int | None:
	"""Находит первое число в строке и возвращает его"""
	search = re.search(NUMBER_PATTERN, text)
	return search and int(search[0])


class OtobaRuException(Exception): ...


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

	def __init__(self, tags_data: dict[str, str], page_uri: Path):
		"""
		:param tags_data: собранные в словарь данные из таблицы об агрегате;
		:param page_uri: URI страницы, которую парсим. Нужно для логирования
		"""

		self.tags_data = tags_data
		self.page_uri = page_uri

	def run(self) -> dict[str, Any]:
		output = {}

		for orig_key, orig_value in self.tags_data.items():
			output.update(self.run_for_field(orig_key, orig_value))

		return output

	def get_field(self, orig_key: str) -> str:
		return self.fields_map.get(orig_key)

	def run_for_field(self, orig_key: str, orig_value: str) -> dict[str, Any]:
		"""
		:param orig_key: Оригинальное название тега/поля из таблицы характеристик
		:param orig_value: Оригинальное значение тега/поля из таблицы характеристик

		:return: dict[поле, значение] для сохранения в БД
		"""
		field_data = {}

		field = self.get_field(orig_key)
		if not field:
			"""Игнорируем поля, не указанные в fields_map"""
			return field_data

		value = orig_value

		parse_method: Callable | None = getattr(self, f'parse_{field}')

		if parse_method:
			field_data.update(parse_method(value))
		elif field in self.int_fields:
			field_data.update({field: self.to_int(value)})
		elif value.lower() in self.bool_map:
			field_data.update({field: self.to_bool(value)})

		return field_data

	@classmethod
	def to_bool(cls, value: str) -> bool:
		return cls.bool_map.get(value.lower(), False)

	@staticmethod
	def to_int(value: str) -> int | None:
		return find_first_number_in_text(value)


class OtobaRuEngineValueTransformer(OtobaRuValueBaseTransformer):
	int_fields = ('volume', 'power', 'cylinders', 'valves', 'torque')
	fields_map = {
		'точный объем': 'volume',
		'мощность двс': 'power',
		'крутящий момент': 'torque',
		'блок цилиндров': 'cylinders',
		'головка блока': 'valves',
		'привод ГРМ': 'grm_drive_type',
		'фазорегулятор': 'phase_regulator',
		'экологич. класс': 'eco_class',
		'тип топлива': 'type',
	}

	def parse_phase_regulator(self, value: str):
		"""
		Данные о фазорегуляторе.
		Если на найдено значение из enum, возвращается значение для phase_regulator_str
		"""
		output = {}

		mapper = {
			'впуск': VehicleEnginePhaseRegulatorType.INPUT,
			'выпуск': VehicleEnginePhaseRegulatorType.OUTPUT,
		}

		if value.lower() in mapper:
			output['phase_regulator'] = mapper[value.lower()]
		else:
			logger.warning(f'Не опознан фазорегулятор на странице {self.page_uri}: {value}')
			output['phase_regulator_system'] = value

		return output

	def parse_grm_drive_type(self, value: str):
		output = {}

		mapper = {
			'ремень': VehicleEngineGRMType.BELT,
			'цепь': VehicleEngineGRMType.CHAIN,
			'шестерни': VehicleEngineGRMType.GEARS,
		}

		if value.lower() in mapper:
			output['grm_drive_type'] = mapper[value.lower()]
		else:
			logger.warning(f'Не опознан привод ГРМ на странице {self.page_uri}: {value}')

		return output

	def parse_type(self, value: str):
		"""
		Определяет тип двигателя по Типу топлива :)
		"""
		output = {}
		value = value.lower()

		if 'аи' in value:
			engine_type = VehicleEngineType.PETROL
		elif 'дизел' in value:
			engine_type = VehicleEngineType.DIESEL
		else:
			logger.warning(f'Не удалось определить тип двигателя по топливу на странице {self.page_uri}: {value}')
			engine_type = VehicleEngineType.PETROL

		has_turbo = self.to_bool(self.tags_data.get('турбонаддув'))
		if has_turbo:
			engine_type |= VehicleEngineType.TURBO
		else:
			engine_type |= VehicleEngineType.ATMOSPHERIC

		output['type'] = engine_type

		return output


class OtobaRuTransmissionValueTransformer(OtobaRuValueBaseTransformer):
	int_fields = ('gears',)
	fields_map = {
		'тип': 'type',
		'количество передач': 'gears',
		'крутящий момент': 'torque',
		'для привода': 'drive_types',
	}

	def parse_type(self, value: str):
		output = {}

		mapper = {
			'механика': VehicleTransmissionType.MANUAL,
			'МКПП': VehicleTransmissionType.MANUAL,
			'автомат': VehicleTransmissionType.AUTO,
			'гидроавтомат': VehicleTransmissionType.AUTO,
			'АКПП': VehicleTransmissionType.AUTO,
			'вариатор': VehicleTransmissionType.VARIATOR,
			'CVT': VehicleTransmissionType.VARIATOR,
			'робот': VehicleTransmissionType.ROBOT,
			'роботизированная': VehicleTransmissionType.ROBOT,
			'DCT': VehicleTransmissionType.ROBOT,
		}

		if value.lower() in mapper:
			output['type'] = mapper[value.lower()]
		else:
			logger.warning(f'Не опознан тип коробки передач на странице {self.page_uri}: {value}')

		return output

	def parse_drive_types(self, value: str):
		mapper = {
			'передний': CarDriveType.FRONT,
			'задний': CarDriveType.BACK,
			'полный': CarDriveType.FULL,
		}

		drive_types: list[CarDriveType] = []

		if '/' in value:
			values = value.split('/')
		elif ',' in value:
			values = value.split(',')
		else:
			values = [value]

		for val in values:
			if val.lower() in mapper:
				drive_types.append(mapper[val.lower()])
			else:
				logger.warning(f'Не опознан тип привода на странице {self.page_uri}: {value}')

		return {
			'drive_types': drive_types,
		}


class OtobaRuHtmlParser:
	"""
	Парсер сайта https://otoba.ru.
	Сайт содержит информацию о двигателях и коробках передач самых популярных марок автомобилей.
	Результатом работы парсера будет созданный pickle-файл с объектами VehicleEngine и CarTransmission.
	"""

	root_uri = Path('otoba.ru')
	engines_uri = root_uri / 'dvigatel' / 'catalog'
	transmissions_uri = root_uri / 'transmissii' / 'catalog'

	def __init__(self):
		self.parsed_data = {
			'engines': [],
			'transmissions': [],
		}

	async def run(self, output_path: Path):
		await self.parse_vehicle_node_page('engine')
		await self.parse_vehicle_node_page('transmission')

		output_path.parent.mkdir(exist_ok=True, parents=True)
		with open(output_path, 'wb') as f_obj:
			pickle.dump(self.parsed_data, f_obj, protocol=pickle.HIGHEST_PROTOCOL)


	async def parse_vehicle_node_page(self, vehicle_node_type: VehicleNodeType):
		"""
		Парсит корневую страницу со списком производителей и сохраняет информацию в parsed_data
		"""
		if vehicle_node_type == 'engine':
			root_uri = self.engines_uri
			vehicle_node_title = 'двигателей'
		else:
			root_uri = self.transmissions_uri
			vehicle_node_title = 'трансмиссий'

		brands_uri = await self._parse_brands_uri(root_uri)
		logger.info(f'Обнаружено {len(brands_uri)} производителей {vehicle_node_title}: {brands_uri}')
		for brand_uri in brands_uri:
			brand_code = generate_code(brand_uri.name)
			brand: VehicleBrand = await database.fetch_one(
				select(VehicleBrand).where(VehicleBrand.code == brand_code)
			)

			if not brand:
				logger.error(f'Не удалось определить бренд по коду {brand_code}. URI: {brand_uri}')
				continue

			nodes_uri = await self._parse_all_engine_or_transmissions_uri(brand_uri)
			for node_uri in nodes_uri:
				await self._parse_detail_page(node_uri, brand, vehicle_node_type)

	def _get_soup(self, page_uri: str | Path) -> BeautifulSoup:
		str_page_uri = str(page_uri).removesuffix('.html')

		page = requests.get(f'https://{str_page_uri}.html')
		return BeautifulSoup(page.text, 'html.parser')

	async def _parse_brands_uri(self, page_uri: Path) -> list[Path]:
		"""
		Парсит список ссылок автопроизводителей с корневой страницы с двигателями или КПП.

		:param page_uri: URI страницы (без .html)
		:return: Список URI брендов (без .html)
		"""

		soup = self._get_soup(page_uri)
		brand_list_root: Tag = soup.select_one('div.auto-model')
		brand_list_link_tags: list[Tag] = brand_list_root.find_all('a')
		brand_names = [it.get('href').removesuffix('.html') for it in brand_list_link_tags]

		return [page_uri.parent / href for href in brand_names]

	async def _parse_all_engine_or_transmissions_uri(self, brand_page_url: Path) -> list[Path | str]:
		"""
		Парсит список ссылок на двигатели/трансмиссии со страницы конкретного бренда.

		:param brand_page_url: URL страницы бренда (без .html)
		:return: Список ссылки на подробную информацию всех двигателей/трансмиссий бренда.
		"""

		soup = self._get_soup(brand_page_url)
		link_tags: list[Tag] = soup.select('a.rubr-s')
		hrefs = []
		for link_tag in link_tags:
			href = link_tag.get('href').removesuffix('.html')
			if 'https://' in href:
				hrefs.append(href)	# Полная ссылка
			else:
				hrefs.append(brand_page_url.parent / href)	# Относительная ссылка

		return hrefs

	@staticmethod
	def _get_engine_or_transmission_modifications_pattern(base_name: str) -> str:
		"""
		Возвращает паттерн поиска по модификациям двигателя или трансмиссии
		"""
		return rf'{base_name}[^,\s]*(?:\s+[^,\s]+)*'

	async def _parse_detail_page(
			self,
			detail_page_uri: Path | str,
			brand: VehicleBrand,
			vehicle_node_type: VehicleNodeType,
	):
		"""
		Парсит детальную информацию об узле автомобиля и создаёт указанную модель из полученных данных
		"""

		soup = self._get_soup(detail_page_uri)
		prop_tables: list[Tag] = soup.select('div.table-tth')

		if not prop_tables:
			logger.error(f'Не найдена таблица с характеристиками на странице {detail_page_uri}, обработка пропущена')
			return

		breadcrumbs_tag: Tag = soup.select_one('nav.br-cr')

		if not breadcrumbs_tag:
			breadcrumbs_tag: Tag = soup.select_one('article').select_one('ul')

		# TODO: остановился здесь
		if not breadcrumbs_tag:
			logger.error(f'Не найдены breadcrumbs на странице {detail_page_uri}, обработка пропущена')
			return

		last_breadcrumb = breadcrumbs_tag.select('li')[-1]
		base_name = last_breadcrumb.text

		if vehicle_node_type == 'engine':
			model = VehicleEngine
			parsed_data_key = 'engines'
			transform_class = OtobaRuEngineValueTransformer
		else:
			model = CarTransmission
			parsed_data_key = 'transmissions'
			transform_class = OtobaRuTransmissionValueTransformer

		for prop_table in prop_tables:
			if table_sub_title_tag := prop_table.find('div.tab-prim-title'):  # type: Tag
				"""
				Здесь будут указаны названия модификаций двигателя/трансмиссии.
				Если модификаций несколько, они будут указаны через запятую
				"""
				regex = self._get_engine_or_transmission_modifications_pattern(base_name)
				modifications = set(re.findall(regex, table_sub_title_tag.text))
			else:
				modifications = {base_name}

			tags_data = {}
			for column in prop_table.find_all('div.tab-tth'): # type: Tag
				for prop in column.find_all('tr'):  # type: Tag
					key_orig_tag, value_tag = prop.find_all('td')
					tags_data[key_orig_tag.text.lower().strip()] = value_tag.text.strip()

			transformer = transform_class(tags_data, detail_page_uri)
			instance_data = transformer.run()

			for modification in modifications:
				instance_data.update({
					'name': modification,
					'brand_id': brand.id,
				})
				instance = model(**instance_data)
				self.parsed_data[parsed_data_key].append(instance)
				logger.info(f'Обработан {parsed_data_key}: {instance_data}')


if __name__ == '__main__':
	parser = OtobaRuHtmlParser()
	file_path = BACKEND_DIR / 'default_data' / 'parsed' / 'otoba.pkl'
	asyncio.run(parser.run(file_path))

	with open(file_path, 'rb') as f_obj:
		data = pickle.load(f_obj)
		print(data)
