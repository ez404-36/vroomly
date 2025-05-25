__all__ = (
    'api_create_workspace',
)

from apps.users.api.utils import request_user
from apps.workspaces.api.routers import router
from apps.workspaces.api.schemas.mutators import WorkspaceCreate
from apps.workspaces.models.workspace import WorkspaceModel
from config.database import get_async_session


@router.post('/')
async def api_create_workspace(data: WorkspaceCreate, user = request_user) -> None:
    workspace = WorkspaceModel(
        name=data.name,
        user_id=user.id,
    )

    async with get_async_session() as session:
        session.add(workspace)
        await session.commit()