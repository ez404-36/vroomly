import pickle
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from core.constants import BACKEND_DIR

NUMBER_PATTERN = r'\d+'

def find_first_number_in_text(text: str) -> int | None:
	"""Находит первое число в строке и возвращает его"""
	search = re.search(NUMBER_PATTERN, text)
	return search and int(search[0])


map_otoba_engine_table_prop_to_field_name: dict[str, str] = {
	'Точный объем': 'volume',
	'Мощность': 'power',
	'Крутящий момент': ''
}


class OtobaRuHtmlParser:
	"""
	Парсер сайта https://otoba.ru.
	Сайт содержит информацию о двигателях и коробках передач самых популярных марок автомобилей.
	Результатом работы парсера будет созданный pickle-файл с объектами VehicleEngine, CarEngineSpec, CarTransmission.
	"""

	root_url = Path('https://otoba.ru')
	engines_url = root_url / 'dvigatel' / 'catalog.html'
	transmissions_url = root_url / 'transmissii' / 'catalog.html'

	def __init__(self):
		self.parsed_data = {
			'engines': [],
			'transmissions': []
		}

	def run(self):
		self.parse_engines()
		self.parse_transmissions()

		file_path = BACKEND_DIR / 'default_data' / 'parsed' / 'otoba.pickle'
		pickle.dump(self.parsed_data, file_path)

	def parse_engines(self):
		brand_links = self._parse_brand_list_links(self.engines_url)
		for link in brand_links:
			full_brand_link = self.engines_url.parent / link
			node_links = self._parse_all_engine_or_transmission_links(full_brand_link)
			for node_link in node_links:
				self._parse_engine_page(node_link)

	def parse_transmissions(self):
		pass

	def _get_soup(self, page_url: Path) -> BeautifulSoup:
		page = requests.get(str(page_url))
		return BeautifulSoup(str(page), 'html.parser')

	def _parse_brand_list_links(self, page_url: Path) -> list[Path]:
		"""
		Парсит список ссылок автопроизводителей с корневой страницы с двигателями или КПП
		"""
		soup = self._get_soup(page_url)
		brand_list_root = soup.find('div.auto-model')
		brand_list_links = brand_list_root.find_all('a')

		return brand_list_links

	def _parse_all_engine_or_transmission_links(self, brand_page_url: Path) -> list[Path]:
		"""
		Парсит список двигателей или КПП со страницы конкретного бренда
		"""
		soup = self._get_soup(brand_page_url)
		links = soup.find_all('a.rubr-s')

		return links

	def _parse_engine_page(self, engine_page_url: Path):
		soup = self._get_soup(engine_page_url)
		engine_tables = soup.find_all('div.table-tth')

		for engine_table in engine_tables:
			data = {}

			for column in engine_table.find_all('div.tab-tth'):
				for prop in column.find_all('tr'):
					key_orig, value = prop.find_all('td')
					key = map_otoba_engine_table_prop_to_field_name.get(key_orig)
					# TODO: трансформация числовых значений в строковые для определенных колонок
					data[key] = value

			engine = VehicleEngine(**data)
			self.parsed_data['engines'].append(engine)
