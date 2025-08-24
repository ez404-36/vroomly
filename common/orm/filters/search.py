from typing import Any, TypeVar, Iterable

from sqlalchemy import Select, or_

T = TypeVar('T', bound=Select[Any])

def apply_search(query: T, search: str | None, search_fields: Iterable[str]) -> T:
    if not search:
        return query

    return query.filter(
        or_(
            *[
                getattr(query.froms[0].c, field).ilike(f'%{search}%') for field in search_fields
            ]
        )
    )
