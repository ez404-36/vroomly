from apps.geo.models.country import Country

from .base import ImportFromCSVBase


class ImportCountriesCSV(ImportFromCSVBase):
    model = Country
    filename = 'country.csv'
    mapper = {
        'value': 'name',
    }
