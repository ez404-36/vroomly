from typing import Literal


class OtobaRuException(Exception): ...


VehicleNodeType = Literal['engine', 'transmission', 'vehicle']
NUMBER_PATTERN = r'\d+'
