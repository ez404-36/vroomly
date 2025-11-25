from enum import Enum, IntEnum, IntFlag

from common.schemas.choices_mixin import ChoicesMixin


class VehicleType(ChoicesMixin, IntEnum):
    """Тип ТС"""

    CAR = 1
    MOTORCYCLE = 2

    __labels__ = {
        CAR: "Автомобиль",
        MOTORCYCLE: "Мотоцикл",
    }


class VehicleEngineType(IntFlag):
    """
    Тип двигателя ТС.
    Комбинируемые значения через ИЛИ (|).

    Например, бензиновый атмосферный двигатель записывается так:
    PETROL ATMOSPHERIC == 1 | 16 == 17
    """
    PETROL = 1
    DIESEL = 2
    ELECTRO = 4
    GAS = 8
    ATMOSPHERIC = 16
    TURBO = 32


class VehicleEngineGRMType(IntFlag):
    """Тип привода ГРМ"""
    BELT = 1    # Ремень
    CHAIN = 2   # Цепь
    GEARS = 4   # Шестерни
    TWO_CHAINS = 8  # 2 Цепи
    THREE_CHAINS = 16   # 3 цепи
    FOUR_CHAINS = 32    # 4 Цепи
    WET_BELT = 64   # "Мокрый" ремень (ремень ГРМ погружен в моторное масло)
    TWO_BELTS = 128 # 2 ремня


class VehicleEnginePhaseRegulatorType(IntEnum):
    """Тип привода ГРМ"""
    INPUT = 1   # На впускном распределительном валу
    OUTPUT = 2   # На выпускном распределительном валу
    DUAL = 3    # На обоих валах
    """
    Сложные системы, управляющие в 1 очередь впускными клапанами, но имеющими доп. механизмы на выпуске.
    Системы изменения высоты подъема клапанов.
    """
    COMPLEX = 4


class VehicleTransmissionType(Enum):
    """Тип коробки передач"""

    MANUAL = 1
    AUTO = 2
    ROBOT = 3
    VARIATOR = 4


class VehicleBodyType(IntFlag):
    """Тип кузова ТС (комбинируемые значения)"""
    STEEL = 1   # Сталь
    ALUMINUM = 2   # Алюминий
    MAGNESIUM_ALLOYS = 4    # Магниевые сплавы
    FIBERGLASS = 8 # Стеклопластик
    CARBON = 16  # Углепластик (карбон)
    ABS = 32 # Полипропилен, ABS и другие пластики
    TITAN = 64   # Титан
    TREE = 128    # Дерево
