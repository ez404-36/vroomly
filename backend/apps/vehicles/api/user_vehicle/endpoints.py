from typing import Any
from uuid import UUID

from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.vehicles.api.routers import user_vehicle_router
from apps.vehicles.api.user_vehicle.schemas import (
    CreateUserVehicleByChoiceSchema,
    CreateUserVehicleByVinSchema,
    CreateUserVehicleManualSchema,
    UserVehicleChoiceSchema,
    UserVehicleDetailSchema,
    UserVehicleListSchema,
    UserVehicleWithChoicesSchema,
)
from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfo
from common.orm.views.mixins import BaseAPI
from core.db import database


def _to_float(value: Any) -> float | None:
    """Convert to float or return None."""
    if value is None:
        return None
    return float(value)


@cbv(user_vehicle_router)
class UserVehicleAPI(BaseAPI):
    """API для управления транспортными средствами пользователя."""

    @user_vehicle_router.post(
        '/user-vehicles/',
        response_model=UserVehicleDetailSchema | UserVehicleWithChoicesSchema,
        summary='Добавить ТС в гараж',
    )
    async def create_by_vin(
        self,
        data: CreateUserVehicleByVinSchema,
    ) -> UserVehicleDetailSchema | UserVehicleWithChoicesSchema:
        """
        Добавить ТС в гараж по VIN-номеру.

        Если найдена одна комплектация — создает ТС сразу.
        Если несколько — возвращает варианты для выбора.
        """
        vin_provider = CarInfoByVinProvider()
        car_info = vin_provider.get_info(data.vin)

        guess_service = GuessCommonCarInfo()
        guess_result = await guess_service.get_from_vin01(car_info)

        # Если одно поколение — создаем сразу
        if len(guess_result.generation) == 1:
            generation_id = guess_result.generation[0].id
            user_vehicle = await self._create_user_vehicle(
                user_id=str(self.user.id),
                generation_id=str(generation_id),
            )
            return UserVehicleDetailSchema(
                id=str(user_vehicle.id),
                vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
                user_id=str(user_vehicle.user_id),
                mileage=user_vehicle.mileage,
                is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
                avg_fuel_consumption=_to_float(user_vehicle.avg_fuel_consumption),
                brand=guess_result.brand.name,
                series=guess_result.model.name,
                generation=guess_result.generation[0].name if guess_result.generation else None,
                trim=None,
                production_year=car_info.year,
                color=car_info.color,
            )

        # Несколько вариантов — возвращаем для выбора
        return UserVehicleWithChoicesSchema(
            choices=[
                UserVehicleChoiceSchema(
                    brand=guess_result.brand,
                    model=guess_result.model,
                    generation=guess_result.generation,
                    configuration=guess_result.configuration,
                ),
            ],
            vin=data.vin,
            year=car_info.year,
            color=car_info.color,
        )

    @user_vehicle_router.post(
        '/user-vehicles/by-choice/',
        response_model=UserVehicleDetailSchema,
        summary='Добавить ТС по выбранной комплектации',
    )
    async def create_by_choice(
        self,
        data: CreateUserVehicleByChoiceSchema,
    ) -> UserVehicleDetailSchema:
        """
        Создать ТС после выбора комплектации пользователем.
        """
        user_vehicle = await self._create_user_vehicle(
            user_id=str(self.user.id),
            generation_id=data.generation_id,
        )

        return UserVehicleDetailSchema(
            id=str(user_vehicle.id),
            vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
            user_id=str(user_vehicle.user_id),
            mileage=user_vehicle.mileage,
            is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
            avg_fuel_consumption=_to_float(user_vehicle.avg_fuel_consumption),
            brand=None,
            series=None,
            generation=None,
            trim=None,
            production_year=None,
            color=None,
        )

    @user_vehicle_router.post(
        '/user-vehicles/manual/',
        response_model=UserVehicleDetailSchema,
        summary='Добавить ТС вручную',
    )
    async def create_manual(
        self,
        data: CreateUserVehicleManualSchema,
    ) -> UserVehicleDetailSchema:
        """
        Добавить ТС в гараж вручную (без VIN).
        """
        user_vehicle = await self._create_user_vehicle(
            user_id=str(self.user.id),
            generation_id=data.generation_id,
            trim_id=data.trim_id,
            mileage=data.mileage,
            is_mileage_in_miles=data.is_mileage_in_miles,
            avg_fuel_consumption=data.avg_fuel_consumption,
        )

        return UserVehicleDetailSchema(
            id=str(user_vehicle.id),
            vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
            user_id=str(user_vehicle.user_id),
            mileage=user_vehicle.mileage,
            is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
            avg_fuel_consumption=_to_float(user_vehicle.avg_fuel_consumption),
            brand=None,
            series=None,
            generation=None,
            trim=None,
            production_year=data.production_year,
            color=data.color,
        )

    @user_vehicle_router.get(
        '/user-vehicles/',
        response_model=list[UserVehicleListSchema],
        summary='Получить список ТС пользователя',
    )
    async def list_user_vehicles(
        self,
    ) -> list[UserVehicleListSchema]:
        """
        Получить список всех транспортных средств текущего пользователя (минимальный набор данных).
        """

        query = (
            select(UserVehicle)
            .where(UserVehicle.user_id == self.user.id)
            .options(
                selectinload(UserVehicle.vehicle)
            )
        )
        return await database.fetch_all(query)

    @user_vehicle_router.get(
        '/user-vehicles/{user_vehicle_id}/',
        response_model=UserVehicleDetailSchema,
        summary='Детальная информация о ТС пользователя',
    )
    async def get_user_vehicle(
        self,
        user_vehicle_id: str,
    ) -> UserVehicleDetailSchema:
        """
        Получить детальную информацию о транспортном средстве пользователя.
        """
        query = (
            select(UserVehicle)
            .where(
                UserVehicle.id == UUID(user_vehicle_id),
                UserVehicle.user_id == self.user.id,
            )
            .options(
                selectinload(UserVehicle.generation).selectinload(
                    UserVehicle.__mapper__.relationships['generation'].entity.class_.series
                ),
                selectinload(UserVehicle.generation).selectinload(
                    UserVehicle.__mapper__.relationships['generation'].entity.class_.series
                ).selectinload(
                    UserVehicle.__mapper__.relationships['generation'].entity.class_.series.entity.class_.brand
                ),
            )
        )
        user_vehicle = await database.fetch_one(query)

        if user_vehicle is None:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Транспортное средство не найдено',
            )

        brand_name = None
        series_name = None
        generation_name = None

        if hasattr(user_vehicle, 'generation') and user_vehicle.generation:
            generation_name = user_vehicle.generation.name
            if hasattr(user_vehicle.generation, 'series') and user_vehicle.generation.series:
                series_name = user_vehicle.generation.series.name
                if hasattr(user_vehicle.generation.series, 'brand') and user_vehicle.generation.series.brand:
                    brand_name = user_vehicle.generation.series.brand.name

        return UserVehicleDetailSchema(
            id=str(user_vehicle.id),
            vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
            user_id=str(user_vehicle.user_id),
            mileage=user_vehicle.mileage,
            is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
            avg_fuel_consumption=_to_float(user_vehicle.avg_fuel_consumption),
            brand=brand_name,
            series=series_name,
            generation=generation_name,
            trim=None,
            production_year=None,
            color=None,
        )

    @staticmethod
    async def _create_user_vehicle(  # noqa: PLR0913
        user_id: str,
        generation_id: str | None = None,
        trim_id: str | None = None,
        mileage: int | None = None,
        is_mileage_in_miles: bool = False,
        avg_fuel_consumption: float | None = None,
    ) -> UserVehicle:
        """
        Создать запись UserVehicle в БД.
        """
        user_vehicle = UserVehicle(
            user_id=UUID(user_id),
            vehicle_id=None,
            generation_id=UUID(generation_id) if generation_id else None,
            trim_id=UUID(trim_id) if trim_id else None,
            mileage=mileage,
            is_mileage_in_miles=is_mileage_in_miles,
            avg_fuel_consumption=avg_fuel_consumption,
        )
        async with database.get_async_session() as session:
            session.add(user_vehicle)
            await session.commit()
            await session.refresh(user_vehicle)

        return user_vehicle
