from enum import IntEnum, IntFlag, Enum

from common.schemas.choices_mixin import ChoicesMixin


class VehicleType(ChoicesMixin, IntEnum):
    """Тип ТС"""

    CAR = 0
    MOTORCYCLE = 1

    __labels__ = {
        CAR: "Автомобиль",
        MOTORCYCLE: "Мотоцикл",
    }


class VehicleEngineType(IntFlag):
    """Тип двигателя ТС (комбинируемые значения)"""
    PETROL = 0
    DIESEL = 1
    ELECTRO = 2
    GAS = 4
    ATMOSPHERIC = 8
    TURBO = 16


class VehicleTransmissionType(Enum):
    """Тип коробки передач"""

    MANUAL = 0
    AUTO = 1
    ROBOT = 2
    VARIATOR = 3


class VehicleBodyType(IntFlag):
    """Тип кузова ТС (комбинируемые значения)"""
    STEEL = 0   # Сталь
    ALUMINUM = 1   # Алюминий
    MAGNESIUM_ALLOYS = 2    # Магниевые сплавы
    FIBERGLASS = 4 # Стеклопластик
    CARBON = 8  # Углепластик (карбон)
    ABS = 16 # Полипропилен, ABS и другие пластики
    TITAN = 32   # Титан
    TREE = 64    # Дерево


