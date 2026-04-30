from enum import Enum


class CarDriveType(Enum):
    """Тип привода"""

    FRONT = 1
    BACK = 2
    FULL = 3


class CarBodyType(Enum):
    """Тип кузова"""

    SEDAN = 1
    HATCHBACK = 2
    SW = 3
    COUPE = 4
    CUV = 5
    SUV = 6
    LIFTBACK = 7
    ROADSTER = 8
    VAN = 9
    MINIVAN = 10
    PICKUP_TRUCK = 11
    MINIBUS = 12
    TARGA = 13
    FASTBACK = 14
    LANDAU = 15
    CUV_COUPE = 16
    SHOOTING_BRAKE = 17
