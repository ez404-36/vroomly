from sqlalchemy import Boolean
from sqlalchemy.orm import mapped_column, Mapped


class DeletedModelMixin:
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    def delete(self):
        self.deleted = True

    def restore(self):
        self.deleted = False
