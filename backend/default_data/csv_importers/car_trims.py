from apps.vehicles.models.car.car_trim import CarTrim

from .base import ImportObjectsFromCSVBase


class ImportCarTrimsCSV(ImportObjectsFromCSVBase):
    """
    Импорт комплектаций автомобилей.

    На момент сидинга справочник ``CarBody`` ещё не наполнен, поэтому
    ``body_id`` остаётся пустым, а исходное обозначение кузова сохраняется
    в ``body_str`` (см. ``CarTrim``).
    """

    model = CarTrim
    source_filename = 'car_trim.csv'
