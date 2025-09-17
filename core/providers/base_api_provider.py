import requests

from common.utils.url import get_url


class BaseApiProvider:
    """
    Провайдер для API-запросов к внешним сервисам
    """

    base_url: str
    timeout: int = 10

    def get(
            self,
            endpoint_url: str | None = None,
            path_params: dict | None = None,
            headers: dict = None,
            query_params: dict = None,
    ) -> dict:
        path_params = path_params or {}
        url = get_url(self.base_url, endpoint_url)

        response = requests.get(
            url.format(**path_params),
            headers=headers,
            params=query_params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def post(
            self,
            endpoint_url: str | None = None,
            path_params: dict | None = None,
            payload: dict | None = None,
            headers: dict = None,
    ) -> dict:
        path_params = path_params or {}
        url = get_url(self.base_url, endpoint_url)
        response = requests.post(
            url.format(**path_params),
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
