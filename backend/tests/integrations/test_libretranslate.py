import pytest

from common.providers.translators.libre_translate import LibreTranslate


class TestLibreTranslate:
	@pytest.mark.parametrize(
		'brand_ru, brand_en',
		[
			('Хонда', 'Honda'),
			('Лада', 'Lada'),
			('Киа', 'Kia'),
			('БМВ', 'BMW'),
			('Хёндай', 'Hyundai'),
			('Шевроле', 'Chevrolet'),
		],
	)
	def test_vehicle_brands(self, brand_ru, brand_en):
		client = LibreTranslate()
		assert client.translate(brand_ru) == brand_en
