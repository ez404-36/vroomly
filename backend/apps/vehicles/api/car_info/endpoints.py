from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import router
from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinData
from common.orm.views.mixins import BaseAPI


@cbv(router)
class CarInfoByVinAPI(
	BaseAPI,
):
	@router.get(
		'/by_vin',
		summary='Информация об автомобиле по ВИН-номеру',
		response_model=CarInfoByVinData,
	)
	async def get_by_vin(self, vin: str):
		service = CarInfoByVinProvider()
		return service.get_info(vin=vin)
