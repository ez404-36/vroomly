__all__ = (
    "get_default_router",
    "register_all_service_routers",
)

import importlib
import logging

from common.utils.file_inspectors import get_all_python_files, path_to_module_name
from core.constants import APPS_DIR
from fastapi import APIRouter, FastAPI

logger = logging.getLogger(__name__)


def get_default_router(prefix: str, tag_name: str = None) -> APIRouter:
    tag_name = tag_name or prefix
    router = APIRouter(prefix=f"/{prefix}", tags=[tag_name])
    return router


def register_all_service_routers(_root_router: APIRouter | FastAPI) -> None:
    all_router_files = get_all_python_files(APPS_DIR, "routers")
    for router_file in all_router_files:
        router_module_name = path_to_module_name(router_file)
        all_endpoints_files = get_all_python_files(router_file.parent, "endpoints")

        try:
            for endpoint_file in all_endpoints_files:
                if endpoint_file.exists():
                    importlib.import_module(path_to_module_name(endpoint_file))
        except Exception as e:
            logger.error(f"Не удалось импортировать эндпоинты: {e}")

        try:
            router_file_module = importlib.import_module(router_module_name)
            for router in getattr(router_file_module, "list_routers", []):
                _root_router.include_router(router)
        except ImportError as e:
            logger.error(
                f"Не удалось импортировать роутеры из файла {router_file} по причине: {e}"
            )
            continue
        except Exception as e:
            logger.error(e)
            continue
