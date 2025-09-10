import requests


class BaseApiProvider:
    """
    Провайдер для внешних API-запросов к сторонним сервисам
    """

    base_url: str
    endpoint_url: str = ''

    def get(
            self,
            path_params: dict | None = None,
            headers: dict = None,
            query_params: dict = None,
    ) -> dict:
        response = self.make_request(
            path_params=path_params,
            headers=headers,
            query_params=query_params,
        )
        response.raise_for_status()
        return response.json()

    def make_request(
            self,
            path_params: dict | None = None,
            headers: dict = None,
            query_params: dict = None
    ) -> requests.Response:
        path_params = path_params or {}
        response = requests.get(
            (self.base_url + self.endpoint_url).format(**path_params),
            headers=headers,
            params=query_params,
            timeout=10,
        )
        response.raise_for_status()
        return response
