__all__ = (
    'get_default_router',
    'register_all_service_routers',
)

import logging

from fastapi import APIRouter, FastAPI

from core.constants import APPS_DIR

logger = logging.getLogger(__name__)


def get_default_router(service_name: str, tag_name: str=None) -> APIRouter:
    tag_name = tag_name or service_name
    router = APIRouter(prefix=f"/{service_name}", tags=[tag_name])
    return router


def register_all_service_routers(_root_router: APIRouter | FastAPI) -> None:
    for service_dir in APPS_DIR.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = service_dir.name
        if service_name.startswith('__'):
            continue

        api_dir = service_dir / 'api'
        if not api_dir.exists():
            continue

        routers_file_path = api_dir / 'routers.py'
        if not routers_file_path.exists():
            logger.error(f"Routers file {routers_file_path} does not exist")

        try:
            router_file_module = __import__(f"apps.{service_name}.api.routers", fromlist=["*"])
            for router in getattr(router_file_module, 'list_routers', []):
                _root_router.include_router(router)
        except ImportError as e:
            logger.error(f"Не удалось импортировать роутеры для сервиса {service_name}: {e}")
            continue
        except Exception as e:
            logger.error(e)
            continue
