import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from core.db import database
from core.micro_services.routers.utils import register_all_service_routers
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI

logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if hasattr(database, "connect"):
        await database.connect()

    yield

    if hasattr(database, "disconnect"):
        await database.disconnect()


app = FastAPI(lifespan=lifespan)

_root_api_router = APIRouter(prefix="/api")
register_all_service_routers(_root_api_router)
app.include_router(_root_api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True,
    )
