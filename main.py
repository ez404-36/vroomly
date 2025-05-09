import logging

import uvicorn
from fastapi import FastAPI, APIRouter

from core.constants import APPS_DIR

app = FastAPI()

logger = logging.getLogger(__name__)


def register_routers(_app: FastAPI) -> None:
    for service_dir in APPS_DIR.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = service_dir.name
        if service_name.startswith('__'):
            continue

        api_dir = service_dir / 'api'
        if not api_dir.exists():
            continue

        service_module_path = api_dir / 'routers.py'

        if not service_module_path.exists():
            logger.error(f'{service_dir} doesnt have routers.py')
            continue

        try:
            router_file_module = __import__(f"apps.{service_name}.api.routers", fromlist=["*"])
            for file_name in dir(router_file_module):
                obj = getattr(router_file_module, file_name)
                if isinstance(obj, APIRouter):
                    app.include_router(obj)
        except ImportError as e:
            logger.error(f"Не удалось импортировать роутер для сервиса {service_name}: {e}")
            continue


register_routers(app)


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
