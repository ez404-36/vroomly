import asyncio

from config.db import get_async_session
from default_data.seeds.countries import ImportCountriesCSV
from default_data.seeds.vehicle_brands import ImportVehicleBrandsCSV


async def seed_all():
    async with get_async_session() as session:
        # ImportCountriesCSV.run(session)
        await ImportVehicleBrandsCSV.run(session)

        await session.commit()
        await session.close()


if __name__ == '__main__':
    asyncio.run(seed_all())
