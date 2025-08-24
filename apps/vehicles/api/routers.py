from core.micro_services.routers import get_default_router

from ..service import service_name

router = get_default_router(service_name)

list_routers = [
    router,
]
