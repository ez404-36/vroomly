__all__ = (
    "UserAPI",
)

from fastapi_utils.cbv import cbv

from common.orm.views.mixins import BaseAPI
from common.schemas.models import CurrentUser

from ..routers import router


@cbv(router)
class UserAPI(
    BaseAPI,
):
    @router.get("/me")
    async def api_get_current_user(self) -> CurrentUser:
        return self.user
