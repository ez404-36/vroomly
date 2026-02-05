from apps.geo.models.country import Country

from .base import ImportObjectsFromCSVBase


# TODO: не все названия стран на английском языке в csv-файле
class ImportCountriesCSV(ImportObjectsFromCSVBase):
    model = Country
    source_filename = "country.csv"
    mapper = {
        "value": "name",
    }
