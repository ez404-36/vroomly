from fastapi import Query
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import router
from apps.vehicles.api.user_vehicle.schemas import GuessByVinResponseSchema
from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfo
from common.orm.views.mixins import BaseAPI

VIN_LENGTH = 17


@cbv(router)
class CarInfoByVinAPI(
	BaseAPI,
):
	@router.get(
		'/by_vin',
		summary='Информация об автомобиле по ВИН-номеру',
		response_model=CarInfoByVinDataSchema,
	)
	async def get_by_vin(self, vin: str) -> CarInfoByVinDataSchema:
		"""Возвращает сырые данные о ТС от провайдера vin-01.ru."""
		service = CarInfoByVinProvider()
		return service.get_info(vin=vin)

	@router.get(
		'/guess_by_vin/',
		summary='Подобрать данные ТС по VIN для предзаполнения формы',
		response_model=GuessByVinResponseSchema,
	)
	async def guess_by_vin(
		self,
		vin: str = Query(..., min_length=VIN_LENGTH, max_length=VIN_LENGTH, description='VIN-номер'),
	) -> GuessByVinResponseSchema:
		"""
		Подбирает варианты бренда/модели/поколений/комплектаций по VIN.

		Read-only: ничего не сохраняет в БД, только возвращает фронту
		данные для предзаполнения формы добавления ТС.
		"""
		vin_provider = CarInfoByVinProvider()
		car_info = vin_provider.get_info(vin)

		guess_service = GuessCommonCarInfo()
		guess_result = await guess_service.get_from_vin01(car_info)

		return GuessByVinResponseSchema(
			brand=guess_result.brand,
			model=guess_result.model,
			generations=guess_result.generations,
			trims=guess_result.trims,
			vin=car_info.vin,
			year=car_info.year,
			color=car_info.color,
		)
