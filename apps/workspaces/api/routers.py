from fastapi import APIRouter
from ..service import service_name

router = APIRouter(prefix=f"/{service_name}", tags=[service_name])
