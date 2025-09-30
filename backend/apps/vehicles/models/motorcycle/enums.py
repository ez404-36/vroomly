from enum import Enum


class MotorcycleCoolingType(Enum):
    """Тип охлаждения"""
    AIR = 0
    LIQUID = 1


class MotorcycleShiftType(Enum):
    """Тип переключения передач мотоцикла"""
    FOOT = 0
    HAND = 1
    SEMI_AUTO = 2


class MotorcycleBodyType(Enum):
    """Тип кузова мотоцикла"""
