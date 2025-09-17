from core.providers.vin01 import VinO1ApiProvider


class CarInfoByVinProvider(VinO1ApiProvider):
    """
    Провайдер доступа к сервису с информацией об автомобилях по их VIN номеру
    """
    endpoint_url = '/v1/getBase/{vin}/1'

    def get_info(self, vin: str) -> dict:
        return self.get(
            path_params={'vin': vin},
        )
