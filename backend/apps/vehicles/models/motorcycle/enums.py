from enum import Enum


class MotorcycleCoolingType(Enum):
    """Тип охлаждения"""
    AIR = 1
    LIQUID = 2


class MotorcycleShiftType(Enum):
    """Тип переключения передач мотоцикла"""
    FOOT = 1
    HAND = 2
    SEMI_AUTO = 3


class MotorcycleBodyType(Enum):
    """Тип кузова мотоцикла"""
