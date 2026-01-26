import logging
import os
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import uvicorn
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from core.db import database
from core.micro_services.routers.utils import register_all_service_routers

logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Жизненный цикл приложения"""
    if connect := getattr(database, "connect", None):
        connect: Callable
        await connect()

    yield

    if disconnect := getattr(database, "disconnect", None):
        disconnect: Callable
        await disconnect()


app = FastAPI(lifespan=lifespan)

allowed_origins = [
    'http://localhost:8077',
    'http://localhost:5173',
]

@app.middleware("http")
async def strict_cors_blocker(request: Request, call_next):
    """
    Без этого слоя код эндпоинта будет выполнен, несмотря на ошибку CORS
    """
    if request.method == "OPTIONS":
        return await call_next(request)

    origin = request.headers.get("origin")

    if origin not in allowed_origins:
        return PlainTextResponse("CORS policy violation", status_code=200)

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
