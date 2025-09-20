from apps.vehicles.integrations.car_info_by_vin.schema import (
    CarInfoByVIN,
    CarInfoByVinData,
)
from common.providers.vin01 import Vin01ApiException, VinO1ApiProvider


class CarInfoByVinProvider(VinO1ApiProvider):
    """
    Провайдер доступа к сервису с информацией об автомобилях по их VIN номеру
    """

    def get_info(self, vin: str) -> CarInfoByVinData:
        raw_response = self.get(
            endpoint_url="/v1/getBase/{vin}/1",
            path_params={"vin": vin},
        )
        response = CarInfoByVIN(**raw_response)
        if response.status != 200 or not response.success:
            raise Vin01ApiException(
                f"Ошибка получения данных из сервиса {self.base_url}"
            )

        return response.data
