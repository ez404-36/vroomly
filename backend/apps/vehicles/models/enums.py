from enum import IntEnum, IntFlag


class EngineType(IntFlag):
    PETROL = 0
    DIESEL = 1
    ELECTRO = 2
    GAS = 4
    ATMOSPHERIC = 8
    TURBO = 16


class VehicleType(IntEnum):
    """Тип ТС"""

    CAR = 0
    MOTORCYCLE = 1
