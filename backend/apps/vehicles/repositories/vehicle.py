"""Репозиторий доступа к данным ``Vehicle`` (ТС каталога)."""

from apps.vehicles.models.vehicle.vehicle import Vehicle
from apps.vehicles.repositories.base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
	"""Доступ к ТС каталога. Методы поиска возвращают объект или ``None``."""

	model = Vehicle
