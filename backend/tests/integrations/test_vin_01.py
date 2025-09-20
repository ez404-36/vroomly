from core.providers.vin01 import VinO1ApiProvider


class TestVinO1ApiProvider:
    def test_service_is_available(self):
        service = VinO1ApiProvider()
        response = service.get(is_json_response=False)

        assert response is not None
