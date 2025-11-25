import asyncio
import logging
import pickle
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Literal

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import ColumnElement, and_, or_, select, true

from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.enums import (
	VehicleEngineGRMType,
	VehicleEnginePhaseRegulatorType,
	VehicleEngineType,
	VehicleTransmissionType,
)
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import VehicleEnginePhaseRegulatorSystem
from common.utils.generators import generate_code
from core.constants import BACKEND_DIR
from core.db import database
from core.models import AutoSchemaBase

PARSED_DATA_DIR = BACKEND_DIR / 'default_data' / 'parsed'
NUMBER_PATTERN = r'\d+'
VehicleNodeType = Literal['engine', 'transmission']

logging.basicConfig(
	filename=PARSED_DATA_DIR / 'otoba_ru_parser.log',
	filemode='w',
	format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	level=logging.WARNING,
)

logger = logging.getLogger('OtobaRuHtmlParser')

phase_regulator_mapper = {
	'есть': VehicleEnginePhaseRegulatorType.INPUT,
	'впуск': VehicleEnginePhaseRegulatorType.INPUT,
	'на впуске': VehicleEnginePhaseRegulatorType.INPUT,
	'на впуске *': VehicleEnginePhaseRegulatorType.INPUT,
	'только на впуске': VehicleEnginePhaseRegulatorType.INPUT,
	'на впускном валу': VehicleEnginePhaseRegulatorType.INPUT,
	'на впускных валах': VehicleEnginePhaseRegulatorType.INPUT,
	'упр. натяжитель': VehicleEnginePhaseRegulatorType.INPUT,
	'выпуск': VehicleEnginePhaseRegulatorType.OUTPUT,
	'на выпуске': VehicleEnginePhaseRegulatorType.OUTPUT,
	'на выпускном валу': VehicleEnginePhaseRegulatorType.OUTPUT,
	'впуск + выпуск': VehicleEnginePhaseRegulatorType.DUAL,
	'впуск/выпуск': VehicleEnginePhaseRegulatorType.DUAL,
	'впуск / выпуск': VehicleEnginePhaseRegulatorType.DUAL,
	'на впуске и выпуске': VehicleEnginePhaseRegulatorType.DUAL,
	'на впуске и на выпуске': VehicleEnginePhaseRegulatorType.DUAL,
	'на всех валах': VehicleEnginePhaseRegulatorType.DUAL,
	'на обоих валах': VehicleEnginePhaseRegulatorType.DUAL,
	'на двух валах': VehicleEnginePhaseRegulatorType.DUAL,
	'гнц': VehicleEnginePhaseRegulatorType.COMPLEX,
	'с 2009 года': VehicleEnginePhaseRegulatorType.DUAL,
	'с 1999 года': VehicleEnginePhaseRegulatorType.DUAL,
	'опция': VehicleEnginePhaseRegulatorType.DUAL,
	'(опция)': VehicleEnginePhaseRegulatorType.DUAL,
}

phase_regulator_system_mapper: dict[str, str] = {
	# Honda
	'VTEC (на 150 л.с.)': 'VTEC',
	'VTEC (на 200 л.с.)': 'VTEC',
	'DVCT': 'DOHC_VTEC',
	'Dual-VCT': 'DOHC_VTEC',
	'Dual-VCT + VTEC': 'DOHC_VTEC',
	'Dual-VCT + i-VTEC': 'I_VTEC_AND_DOHC_VTEC',
	'Dual-VCT + i-VTEC *': 'I_VTEC_AND_DOHC_VTEC',
	'DVTC': 'DOHC_VTEC',
	'Dual-VTC': 'DOHC_VTEC',
	'Dual-VTC + VTEC': 'DOHC_VTEC',
	'Dual-VTC + i-VTEC': 'I_VTEC_AND_DOHC_VTEC',
	'Dual-VTC + i-VTEC *': 'I_VTEC_AND_DOHC_VTEC',
	'VCT + i-VTEC': 'I_VTEC_AND_VTC',
	'VCT и i-VTEC': 'I_VTEC_AND_VTC',
	'VTC + i-VTEC': 'I_VTEC_AND_VTC',
	# BMW
	'single VANOS': 'VANOS',
	'dual-VANOS': 'DOUBLE_VANOS',
	'double VANOS': 'DOUBLE_VANOS',
	# mitsubishi
	'MIVEC 2': 'MIVEC',
	'опция': 'MIVEC',
	'опция MIVEC': 'MIVEC',
	'опция AVCS': 'AVCS',
	'eVTC': 'E_VTC',
	# toyota
	'VVT-i с 2013 года': 'VVT_I',
}

grm_drive_type_mapper = {
	'ремень': VehicleEngineGRMType.BELT,
	'зубчатый ремень': VehicleEngineGRMType.BELT,
	'ременной': VehicleEngineGRMType.BELT,
	'два ремня': VehicleEngineGRMType.TWO_BELTS,
	'цепь': VehicleEngineGRMType.CHAIN,
	'цепной': VehicleEngineGRMType.CHAIN,
	'шестерни': VehicleEngineGRMType.GEARS,
	'шестеренчатый': VehicleEngineGRMType.GEARS,
	'однорядная цепь': VehicleEngineGRMType.CHAIN,
	'цепь морзе': VehicleEngineGRMType.CHAIN,
	'двухрядная цепь': VehicleEngineGRMType.TWO_CHAINS,
	'пара цепей': VehicleEngineGRMType.TWO_CHAINS,
	'цепь двухрядная': VehicleEngineGRMType.TWO_CHAINS,
	'ремень и цепь': VehicleEngineGRMType.BELT | VehicleEngineGRMType.CHAIN,
	'ремень плюс цепь': VehicleEngineGRMType.BELT | VehicleEngineGRMType.CHAIN,
	'ремень + цепь': VehicleEngineGRMType.BELT | VehicleEngineGRMType.CHAIN,
	'цепь и ремень': VehicleEngineGRMType.BELT | VehicleEngineGRMType.CHAIN,
	'ремень и цепи': VehicleEngineGRMType.BELT | VehicleEngineGRMType.TWO_CHAINS,
	'ремень и 2 цепи': VehicleEngineGRMType.BELT | VehicleEngineGRMType.TWO_CHAINS,
	'ремень и две цепи': VehicleEngineGRMType.BELT | VehicleEngineGRMType.TWO_CHAINS,
	'ремень и пара цепей': VehicleEngineGRMType.BELT | VehicleEngineGRMType.TWO_CHAINS,
	'две цепи': VehicleEngineGRMType.TWO_CHAINS,
	'три цепи': VehicleEngineGRMType.THREE_CHAINS,
	'цепь и шестерни': VehicleEngineGRMType.CHAIN | VehicleEngineGRMType.GEARS,
	'цепь/шестерни': VehicleEngineGRMType.CHAIN | VehicleEngineGRMType.GEARS,
	'ремень и шестерни': VehicleEngineGRMType.BELT | VehicleEngineGRMType.GEARS,
	'4 цепи': VehicleEngineGRMType.FOUR_CHAINS,
	'четыре цепи': VehicleEngineGRMType.FOUR_CHAINS,
}

transmission_type_mapper = {
	'механика': VehicleTransmissionType.MANUAL,
	'механическая коробка': VehicleTransmissionType.MANUAL,
	'МКПП': VehicleTransmissionType.MANUAL,
	'автомат': VehicleTransmissionType.AUTO,
	'гибридный автомат': VehicleTransmissionType.AUTO,
	'гидроавтомат': VehicleTransmissionType.AUTO,
	'АКПП': VehicleTransmissionType.AUTO,
	'вариатор': VehicleTransmissionType.VARIATOR,
	'CVT': VehicleTransmissionType.VARIATOR,
	'робот': VehicleTransmissionType.ROBOT,
	'роботизированная': VehicleTransmissionType.ROBOT,
	'роботизированная коробка': VehicleTransmissionType.ROBOT,
	'DCT': VehicleTransmissionType.ROBOT,
	'однодисковый робот': VehicleTransmissionType.ROBOT,
	'преселективный робот': VehicleTransmissionType.ROBOT,
}

transmission_drive_type_mapper = {
	'передний': CarDriveType.FRONT,
	'задний': CarDriveType.BACK,
	'полный': CarDriveType.FULL,
}

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

		self.tags_data = tags_data
		self.page_uri = page_uri
		self.brand = brand
		self.concern = concern

	async def run(self) -> dict[str, Any]:
		output = {}

		for orig_key, orig_value in self.tags_data.items():
			output.update(await self.run_for_field(orig_key, orig_value))

		return output

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
			return or_(
				model.brand_id == self.brand.id,
				model.concern_id == self.concern.id
			)
		elif self.brand:
			return model.brand_id == self.brand.id
		elif self.concern:
			return model.concern_id == self.concern.id
		else:
			return true()


class OtobaRuEngineValueTransformer(OtobaRuValueBaseTransformer):
	int_fields = ('volume', 'power', 'cylinders', 'valves', 'torque')
	fields_map = {
		'точный объем': 'volume',
		'мощность двс': 'power',
		'крутящий момент': 'torque',
		'блок цилиндров': 'cylinders',
		'головка блока': 'valves',
		'привод грм': 'grm_drive_type',
		'фазорегулятор': 'phase_regulator',
		'экологич. класс': 'eco_class',
		'тип топлива': 'type',
	}

	async def parse_phase_regulator(self, value: str):
		"""
		Данные о фазорегуляторе.
		Если на найдено значение из enum, возвращается значение для phase_regulator_str
		"""
		output = {}

		if system_regular_type := phase_regulator_mapper.get(value.lower()):
			output['phase_regulator_type'] = system_regular_type
		else:
			as_bool = self.to_bool(value)
			if as_bool is None:
				value = (
					value.removeprefix('на впуске ')
					.replace('Dual ', 'D')
					.replace('dual ', 'D')
				)

				code = phase_regulator_system_mapper.get(value, generate_code(value))

				phase_regulator_system = await database.fetch_one(
					select(VehicleEnginePhaseRegulatorSystem).where(
						and_(
							or_(
								VehicleEnginePhaseRegulatorSystem.code == code,
								VehicleEnginePhaseRegulatorSystem.code == value,
							),
							self.brand_or_concern_condition(VehicleEnginePhaseRegulatorSystem)
						)

					)
				)

				if phase_regulator_system:
					output['phase_regulator_system_id'] = phase_regulator_system.id
				else:
					logger.warning(f'Не опознан тип регулирования фаз странице {self.page_uri}: {value}')

		return output

	async def parse_grm_drive_type(self, value: str):
		output = {}

		if grm_drive_type := grm_drive_type_mapper.get(value.lower()):
			output['grm_drive_type'] = grm_drive_type
		else:
			logger.warning(f'Не опознан привод ГРМ на странице {self.page_uri}: {value}')

		return output

	async def parse_type(self, value: str):
		"""
		Определяет тип двигателя по Типу топлива :)
		"""
		output = {}
		value = value.lower()

		if 'аи' in value:
			engine_type = VehicleEngineType.PETROL
		elif 'дизел' in value:
			engine_type = VehicleEngineType.DIESEL
		elif value in ['метан', 'пропан-бутан']:
			engine_type = VehicleEngineType.GAS
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

	async def parse_type(self, value: str):
		output = {}

		if t_type := transmission_type_mapper.get(value.lower()):
			output['type'] = t_type
		else:
			logger.warning(f'Не опознан тип коробки передач на странице {self.page_uri}: {value}')

		return output

	async def parse_drive_types(self, value: str):
		drive_types: list[CarDriveType] = []

		if '/' in value:
			values = value.split('/')
		elif ',' in value:
			values = value.split(',')
		elif '+' in value:
			values = value.split('+')
		elif value == 'любой':
			values = [
				VehicleTransmissionType.MANUAL,
				VehicleTransmissionType.AUTO,
				VehicleTransmissionType.ROBOT,
				VehicleTransmissionType.VARIATOR,
			]
		else:
			values = [value]

		for val in values:
			if isinstance(val, str):
				drive_type = transmission_drive_type_mapper.get(val.strip().lower())
			else:
				drive_type = val

			if drive_type:
				drive_types.append(drive_type)
			else:
				logger.warning(f'Не опознан тип привода на странице {self.page_uri}: {value} ({val})')

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

	"""
	Маппер концернов, указанных на сайте, с кодом концерна в БД
	"""
	concern_map = {
		'HYUNDAI_KIA': 'HYUNDAI_MG',
	}

	"""
	Маппер брендов, указанных на сайте, с кодом бренда в БД
	"""
	brand_map = {
		'MERCEDES': 'MERCEDES_BENZ',
	}

	def __init__(self):
		self.parsed_data = {
			'engines': [],
			'transmissions': [],
		}

	async def run(self, output_path: Path, only: VehicleNodeType = None):
		parse_pages: tuple[VehicleNodeType] = ('engine', 'transmission')
		for page in parse_pages:
			if only is None or only == page:
				await self.parse_vehicle_node_page(page)

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
			brand_or_concern_code = generate_code(brand_uri.name)

			brand_mapped_code = self.brand_map.get(brand_or_concern_code, brand_or_concern_code)

			brand: VehicleBrand | None = await database.fetch_one(
				select(VehicleBrand)
				.where(
					or_(
						VehicleBrand.code == brand_mapped_code,
						VehicleBrand.abbreviation == brand_mapped_code,
					)
				)
			)

			concern_mapped_code = self.concern_map.get(brand_or_concern_code, brand_or_concern_code)

			concern: VehicleConcern | None = await database.fetch_one(
				select(VehicleConcern)
				.where(
					or_(
						VehicleConcern.code == concern_mapped_code,
						VehicleConcern.abbreviation == concern_mapped_code,
					)
				)
			)

			if brand and brand.concern_id and not concern:
				concern = await database.fetch_one(
					select(VehicleConcern).where(
						VehicleConcern.id == brand.concern_id
					)
				)

			if not brand and not concern:
				logger.error(f'Не удалось определить бренд/концерн по коду {brand_or_concern_code}. URI: {brand_uri}')
				continue

			nodes_uri = await self._parse_all_engine_or_transmissions_uri(brand_uri)
			for node_uri in nodes_uri:
				await self._parse_detail_page(node_uri, brand, concern, vehicle_node_type)

	def _get_soup(self, page_uri: str | Path) -> BeautifulSoup:
		str_page_uri = str(page_uri).removesuffix('.html').removeprefix("https://")

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
		brand_list_link_tags: list[Tag] = brand_list_root.select('a')
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
			brand: VehicleBrand | None,
			concern: VehicleConcern | None,
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

		if not breadcrumbs_tag:
			logger.error(f'Не найдены breadcrumbs на странице {detail_page_uri}, обработка пропущена')
			return

		last_breadcrumb = breadcrumbs_tag.select('li')[-1]
		base_name = last_breadcrumb.text.strip()

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
			for column in prop_table.select('table.tab-tth'): # type: Tag
				for prop in column.select('tr'):  # type: Tag
					key_orig_tag, value_tag = prop.select('td')
					tags_data[key_orig_tag.text.lower().strip()] = value_tag.text.strip()

			transformer = transform_class(tags_data, detail_page_uri, brand, concern)
			instance_data = await transformer.run()

			for modification in modifications:
				instance_data.update({
					'name': modification,
					'brand_id': brand.id if brand and not concern else None,
					'concern_id': concern.id if concern and not brand else None,
				})
				instance = model(**instance_data)
				self.parsed_data[parsed_data_key].append(instance)
				logger.info(f'Обработан {parsed_data_key}: {instance_data}')


async def create_from_pkl_file(pkl_file: str | Path):
	with open(pkl_file, 'rb') as f_obj:
		data = pickle.load(f_obj)

	engines = data.get('engines', [])
	transmissions = data.get('transmissions', [])

	# [it.type for it in transmissions if not isinstance(it.type, VehicleTransmissionType)] -> [None, None]

	async with database.get_async_session() as session:
		session.add_all(engines)
		session.add_all(transmissions)
		await session.commit()
		await session.close()


if __name__ == '__main__':
	parser = OtobaRuHtmlParser()
	file_path = PARSED_DATA_DIR / 'transmissions.pkl'
	# asyncio.run(parser.run(file_path, only='transmission'))
	asyncio.run(create_from_pkl_file(file_path))
