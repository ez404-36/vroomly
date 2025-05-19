__all__ = (
    'get_current_workspaces',
)

from core.safety.token import TOKEN
from .routers import router


@router.get('/')
async def get_current_workspaces(token: TOKEN):
    return {'token': token}
