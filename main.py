import logging

import uvicorn
from fastapi import FastAPI

from core.micro_services.routers.utils import register_all_service_routers

app = FastAPI()

logger = logging.getLogger(__name__)

# TODO: с root_router не работают роуты
# root_router = APIRouter(prefix="/api")
# app.include_router(root_router)
# register_all_service_routers(root_router)
register_all_service_routers(app)


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
