from enum import Enum


class CarDriveType(Enum):
    """Тип привода"""

    FRONT = 0
    BACK = 1
    FULL = 2


class CarBodyType(Enum):
    """Тип кузова"""

    SEDAN = 0
    HATCHBACK = 1
    SW = 2
    COUPE = 3
    CUV = 4
    SUV = 5
    LIFTBACK = 6
    ROADSTER = 7
    VAN = 8
    MINIVAN = 9
    PICKUP_TRUCK = 10
    MINIBUS = 11
    TARGA = 12
    FASTBACK = 13
    LANDAU = 14
    CUV_COUPE = 15
    SHOOTING_BRAKE = 16
