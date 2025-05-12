from apps.workspaces.api.routers import router
from main import TOKEN


@router.get('/')
async def get_current_workspaces(token: TOKEN):
    return []
