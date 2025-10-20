__all__ = ("render_item",)

from sqlalchemy import TypeDecorator


def render_item(type_, obj, _autogen_context):
    """Применяет правильный рендер типа для кастомных полей"""

    if type_ == "type" and isinstance(obj, TypeDecorator):
        return f"sa.{obj.impl!r}"

    return False
