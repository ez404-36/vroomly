from core.micro_services.routers import get_default_router

from ..service import service_name

router = get_default_router(service_name)

vehicle_router = get_default_router(prefix=f'{service_name}/vehicle', tag_name=service_name)
series_router = get_default_router(prefix=f'{service_name}/series', tag_name=service_name)
generation_router = get_default_router(prefix=f'{service_name}/generation', tag_name=service_name)
trim_router = get_default_router(prefix=f'{service_name}/trim', tag_name=service_name)
user_vehicle_router = get_default_router(prefix=service_name, tag_name=service_name)
reminder_router = get_default_router(prefix=service_name, tag_name=service_name)

list_routers = [
	router,
	vehicle_router,
	series_router,
	generation_router,
	trim_router,
	user_vehicle_router,
	reminder_router,
]
