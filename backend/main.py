import logging
import os
from contextlib import asynccontextmanager
from typing import Callable

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

def _get_allowed_origins() -> list[str]:
    """Get allowed origins for development. Allows all localhost variants."""
    import socket

    def resolve_host_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host_ip = s.getsockname()[0]
            s.close()
            return host_ip
        except Exception:
            return "172.17.0.1"

    host_ip = resolve_host_ip()

    return [
        "http://localhost:8077",
        "http://127.0.0.1:8077",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        f"http://{host_ip}:8077",
        f"http://{host_ip}:5173",
        "http://host.docker.internal:8077",
        "http://host.docker.internal:5173",
    ]


allowed_origins: list[str] = _get_allowed_origins()

CORS_EXEMPT_PATHS = {"/docs", "/openapi.json", "/redoc", "/swagger"}


@app.middleware("http")
async def strict_cors_blocker(request: Request, call_next):
    """
    Без этого слоя код эндпоинта будет выполнен, несмотря на ошибку CORS
    """
    # Swagger/OpenAPI endpoints always allowed
    if request.url.path in CORS_EXEMPT_PATHS or request.url.path.startswith("/docs/"):
        return await call_next(request)

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
