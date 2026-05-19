import asyncio
import logging
import pickle
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import or_, select
from typing_inspect import get_args

from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from common.utils.generators import generate_code
from core.constants import BACKEND_DIR
from core.db import database
from default_data.parsers.html_parsers.otoba.types import VehicleNodeType
from default_data.parsers.html_parsers.otoba.utils import create_from_pkl_file
from .value_transformers.engine import OtobaRuEngineValueTransformer
from .value_transformers.transmission import OtobaRuTransmissionValueTransformer

PARSED_DATA_DIR = BACKEND_DIR / 'default_data' / 'parsed'

logger = logging.getLogger('OtobaRuHtmlParser')


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
		parse_pages: tuple[VehicleNodeType] = get_args(VehicleNodeType)
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
			print(f'Парсинг бренда {brand_uri}')
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
				instance_data['name'] = modification
				if brand:
					instance_data['brand_id'] = brand.id
				elif concern:
					instance_data['concern_id'] = concern.id

				instance = model(**instance_data)
				errors = instance.validate()
				if errors:
					logger.error(f'Ошибка валидации модели на странице {detail_page_uri}: {errors}')
				self.parsed_data[parsed_data_key].append(instance)
				logger.info(f'Обработан {parsed_data_key}: {instance_data}')


if __name__ == '__main__':
	parser = OtobaRuHtmlParser()
	file_path = PARSED_DATA_DIR / 'transmissions.pkl'
	# asyncio.run(parser.run(file_path, only='transmission'))
	asyncio.run(create_from_pkl_file(file_path))
