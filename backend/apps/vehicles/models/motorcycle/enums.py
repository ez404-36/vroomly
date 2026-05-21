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
    CRUISER = 1
    SPORTBIKE = 2
    TOURIST = 3
    DUAL_SPORT = 4
    NAKED = 5
    CAFE_RACER = 6
    BOBBER = 7
    CHOPPER = 8
