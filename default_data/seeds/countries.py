from apps.geo.models.country import Country
from default_data.import_from_csv_base import ImportFromCSVBase


class ImportCountriesCSV(ImportFromCSVBase):
    model = Country
    filename = 'country.csv'
    mapper = {
        'id': 'prefix',
        'value': 'name',
    }
