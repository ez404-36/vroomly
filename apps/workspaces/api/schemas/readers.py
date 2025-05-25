from datetime import datetime

from pydantic import BaseModel, UUID4


class WorkspaceDetail(BaseModel):
    id: UUID4
    name: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
