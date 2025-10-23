import asyncio

from core.db import database
from core.models import AutoSchemaBase
from default_data.csv_importers.countries import ImportCountriesCSV
from default_data.csv_importers.vehicle_brands import ImportVehicleBrandsCSV
from default_data.csv_importers.vehicle_concerns import ImportVehicleConcernsCSV
from default_data.csv_importers.vehicle_series import ImportVehicleSeriesCSV


async def seed_all():
    """
    Наполняет БД первичными данными о:
    - Странах
    - Автомобильных концернах
    - Автопроизводителях
    - Марках автомобилей
    """

    async with database.get_async_session() as session:
        await ImportCountriesCSV(session).run()
        await ImportVehicleConcernsCSV(session).run()
        await ImportVehicleBrandsCSV(session).run()
        await ImportVehicleSeriesCSV(session).run()

        await session.commit()
        await session.close()

    print("Наполнение БД первичными данными успешно завершено")


async def clean_data():
    """
    В AutoSchemaBase.metadata будут собраны только те модели,
    которые были явно импортированы в модуль default_data.
    Будьте осторожны !
    """

    async with database.get_async_session() as session:
        for tbl in reversed(AutoSchemaBase.metadata.sorted_tables):
            await session.execute(tbl.delete())

            await session.commit()
            await session.close()


async def main():
    await clean_data()
    await seed_all()


if __name__ == "__main__":
    asyncio.run(main())
