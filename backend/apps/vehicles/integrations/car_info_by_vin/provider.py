from apps.vehicles.integrations.car_info_by_vin.schema import (
	CarInfoByVinDataSchema,
	CarInfoByVINSchema,
)
from common.providers.vin01 import Vin01ApiError, VinO1ApiProvider

HTTP_OK = 200


class CarInfoByVinProvider(VinO1ApiProvider):
	"""
	Провайдер доступа к сервису с информацией об автомобилях по их VIN номеру
	"""

	def get_info(self, vin: str) -> CarInfoByVinDataSchema:
		"""Получает информацию об автомобиле по VIN из vin-01.ru."""
		raw_response = self.get(
			endpoint_url='/v1/getBase/{vin}/1',
			path_params={'vin': vin},
		)
		response = CarInfoByVINSchema(**raw_response)
		if response.status != HTTP_OK or not response.success:
			raise Vin01ApiError(f'Ошибка получения данных из сервиса {self.base_url}')

		return response.data
