from common.providers.base_api_provider import BaseApiProvider


class Vin01ApiException(Exception):
    pass


class VinO1ApiProvider(BaseApiProvider):
    base_url = "https://vin-01.ru"
