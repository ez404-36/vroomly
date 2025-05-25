__all__ = (
    'api_get_current_workspaces',
)

from sqlalchemy import select, and_

from apps.users.api.utils import request_user
from apps.workspaces.api.routers import router
from apps.workspaces.api.schemas.readers import WorkspaceDetail
from apps.workspaces.models.workspace import WorkspaceModel
from config.database import get_async_session, fetch_all


@router.get('/')
async def api_get_current_workspaces(user = request_user):
    async with get_async_session() as session:
        query = (
            select(WorkspaceModel)
            .where(
                and_(
                    WorkspaceModel.user_id == user.id,
                    WorkspaceModel.deleted == False,
                )
            )
        )
        workspaces = await fetch_all(session, query)

    return [
        WorkspaceDetail.model_validate(workspace)
        for workspace in workspaces
    ]
