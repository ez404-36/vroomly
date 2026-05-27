from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider


class TestCarInfoByVin:
	def test_is_worked(self):
		service = CarInfoByVinProvider()
		vin = 'XWEJC813DJ0003470'
		info = service.get_info(vin)

		assert info is not None
		assert info.vin == vin
