from typing import Literal


class OtobaRuException(Exception): ...


VehicleNodeType = Literal['engine', 'transmission']
NUMBER_PATTERN = r'\d+'
