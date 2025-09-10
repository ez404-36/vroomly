from core.integrations.vin01 import VinO1ApiProvider


class TestVinO1ApiProvider:
    def test_service_is_available(self):
        service = VinO1ApiProvider()
        response = service.make_request()
        print(response)

        assert response is not None
