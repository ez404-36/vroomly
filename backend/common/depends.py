from fastapi import Depends

from common.auth.decode_token import get_current_user
from common.schemas.models import CurrentUser

request_user: CurrentUser = Depends(get_current_user)
