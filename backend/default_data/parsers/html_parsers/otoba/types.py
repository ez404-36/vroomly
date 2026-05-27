from typing import Literal


class OtobaRuException(Exception): ...


VehicleNodeType = Literal['engine', 'transmission', 'vehicle', 'china_vehicle']
NUMBER_PATTERN = r'\d+'
