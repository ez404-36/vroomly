from fastapi import APIRouter

from apps.users.service import service_name

router = APIRouter(prefix=f"/{service_name}", tags=[service_name])
