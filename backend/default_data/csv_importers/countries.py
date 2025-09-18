from apps.geo.models.country import Country

from .base import ImportFromCSVBase


# TODO: не все названия стран на английском языке в csv-файле
class ImportCountriesCSV(ImportFromCSVBase):
    model = Country
    filename = "country.csv"
    mapper = {
        "value": "name",
    }
