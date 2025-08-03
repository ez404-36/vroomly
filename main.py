import logging

import uvicorn
from fastapi import FastAPI, APIRouter

from core.micro_services.routers.utils import register_all_service_routers

app = FastAPI()

logger = logging.getLogger(__name__)

root_router = APIRouter(prefix="/api")
register_all_service_routers(root_router)
app.include_router(root_router)


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8077, reload=True)
