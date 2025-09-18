from pydantic import BaseModel


class CarInfoByVinData(BaseModel):
    model: str  # по-русски
    year: int
    frame: str | None  # хз что это
    vin: str
    carplate: str  # хз что это
    color: str
    type: str
    volume: int
    power: int
    frame_id: int  # хз что это
    vehicle_type: str


class CarInfoByVIN(BaseModel):
    success: bool
    status: int
    data: CarInfoByVinData
