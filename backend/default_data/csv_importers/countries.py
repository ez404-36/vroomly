from apps.geo.models.country import Country

from .base import ImportObjectsFromCSVBase


# TODO: не все названия стран на английском языке в csv-файле
class ImportCountriesCSV(ImportObjectsFromCSVBase):
    """
    Импорт стран
    """

    model = Country
    source_filename = 'country.csv'
