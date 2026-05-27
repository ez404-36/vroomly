from pydantic import BaseModel


class CarInfoByVinDataSchema(BaseModel):
	model: str  # Бренд + Модель (на русском языке)
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


class CarInfoByVINSchema(BaseModel):
	success: bool
	status: int
	data: CarInfoByVinDataSchema
