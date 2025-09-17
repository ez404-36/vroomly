import asyncio

from core.db import database
from default_data.csv_importers.countries import ImportCountriesCSV
from default_data.csv_importers.vehicle_brands import ImportVehicleBrandsCSV
from default_data.csv_importers.vehicle_models import ImportVehicleModelsCSV


async def seed_all():
    async with database.get_async_session() as session:
        await ImportCountriesCSV(session).run()
        await ImportVehicleBrandsCSV(session).run()
        await ImportVehicleModelsCSV(session).run()

        await session.commit()
        await session.close()

    print('Наполнение БД первичными данными успешно завершено')


if __name__ == '__main__':
    asyncio.run(seed_all())
