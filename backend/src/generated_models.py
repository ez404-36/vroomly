"""
Автоматически сгенерированный файл со всеми Pydantic моделями
Дата генерации: 2025-10-30 11:09:00.533101
Собрано из 91 файлов
Найдено 19 моделей
Сгенерировано автоматически
"""

from apps.vehicles.models.vehicle.enums import VehicleType
from datetime import date
from datetime import datetime, timedelta, timezone
from fastapi_utils.api_model import APIModel
from pydantic import BaseModel
from pydantic import BaseModel, Field
from pydantic import Field, ValidationError, model_validator
from typing import Annotated, TypeAlias
from typing import Literal
from typing import Union
from uuid import UUID


# ==================================================
# КАСТОМНЫЕ ТИПЫ
# ==================================================

# Тип: ID (из types.py)
type ID = Union[UUID, str, int]

# Модель: CountryDetailSchema (из readers.py)
class CountryDetailSchema(APIModel):
    id: str
    name: str
    short_name: str | None

#==================================================

# Модель: VehicleDetailSchema (из readers.py)
class VehicleDetailSchema(APIModel):
    id: UUID
    vehicle_type: VehicleType
    production_year: int
    color: str | None

#==================================================

# Модель: VehicleBrandFilterParams (из filters.py)
class VehicleBrandFilterParams(BaseModel):
    ordering: Literal["country_id", "code"] = Field(
        description="Сортировка", default="code"
    )
    search: str = Field(description="Поиск (по названию/коду)", default=None)
    country: str = Field(description="Фильтрация по коду страны", default=None)

#==================================================

# Модель: VehicleBrandDetailSchema (из readers.py)
class VehicleBrandDetailSchema(APIModel):
    id: UUID
    country_id: str
    code: str
    name: str
    original_name: str | None

#==================================================

# Модель: VehicleSeriesDetailSchema (из readers.py)
class VehicleSeriesDetailSchema(APIModel):
    id: UUID
    name: str
    brand: VehicleBrandDetailSchema

#==================================================

# Модель: VehicleSeriesFilterParams (из filters.py)
class VehicleSeriesFilterParams(BaseModel):
    brand: UUID = Field(description="ID бренда")
    search: str = Field(description="Поиск по названию модели", default=None)

#==================================================

# Модель: VehicleSeriesListSchema (из readers.py)
class VehicleSeriesListSchema(APIModel):
    id: UUID
    name: str
    brand_id: UUID

#==================================================

# Модель: CarInfoByVinDataSchema (из schema.py)
class CarInfoByVinDataSchema(BaseModel):
    model: str  # Бренд + Модель (на русском языке)
    year: int
    frame: str | None  # хз что это
    vin: str
    carplate: str  # хз что это
    color: str
    type: str
    volume: int
    power: int
    frame_id: int  # хз что это
    vehicle_type: str

#==================================================

# Модель: CarInfoByVINSchema (из schema.py)
class CarInfoByVINSchema(BaseModel):
    success: bool
    status: int
    data: CarInfoByVinDataSchema

#==================================================

# Модель: LibreTranslateDetectedLanguage (из libre_translate.py)
class LibreTranslateDetectedLanguage(BaseModel):
    """Определенный переводчиком язык"""

    confidence: int
    language: str

#==================================================

# Модель: LibreTranslateResponse (из libre_translate.py)
class LibreTranslateResponse(BaseModel):
    """Модель ответа LibreTranslate"""

    translatedText: str
    alternatives: list[str]
    detectedLanguage: LibreTranslateDetectedLanguage | None = None

#==================================================

# Модель: ChoiceFieldSchema (из fields.py)
class ChoiceFieldSchema(BaseModel):
    id: ID
    name: str

#==================================================

# Модель: ChoiceFieldWithParentSchema (из fields.py)
class ChoiceFieldWithParentSchema(ChoiceFieldSchema):
    parent: ChoiceFieldSchema

#==================================================

# Модель: GuessCommonCarInfoSchema (из guess_common_car_info.py)
class GuessCommonCarInfoSchema(BaseModel):
    """
    Данные об автомобиле, полученные в результате обработки
    информации по VIN-номеру, предоставленной внешним источником
    """

    brand: ChoiceFieldSchema = Field(description='Бренд')
    model: ChoiceFieldSchema = Field(description='Модель')
    generation: list[ChoiceFieldSchema] = Field(description='Поколение')
    configuration: list[ChoiceFieldWithParentSchema] = Field(description='Комплектация')

#==================================================

# Модель: FrozenModelType (из models.py)
class FrozenModelType(BaseModel):
    """
    Модель данных, в которой запрещено изменять поля
    """

    __abstract__ = True

    model_config = {"frozen": True}

#==================================================

# Модель: RegistrationDataForm (из mutators.py)
class RegistrationDataForm(FrozenModelType):
    login: str = Field(..., min_length=1, max_length=50)
    email: str  # TODO: email validation
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self) -> "RegistrationDataForm":
        if self.password != self.confirm_password:
            raise ValidationError("Passwords do not match")
        return self

#==================================================

# Модель: CurrentUser (из models.py)
class CurrentUser(APIModel):
    """
    Модель текущего пользователя, доступная в API-запросах
    """

    id: UUID
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None

#==================================================

# Модель: Token (из token.py)
class Token(BaseModel):
    access_token: str
    token_type: str

#==================================================

# Модель: TokenData (из token.py)
class TokenData(BaseModel):
    user_id: str | None

#==================================================

