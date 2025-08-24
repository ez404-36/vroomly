from apps.accounts.service import service_name
from core.micro_services.routers import get_default_router

router = get_default_router(service_name)

list_routers = [
    router,
]
