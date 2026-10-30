from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_dto import Pagination
from src.core.database import get_session


async def _get_db() -> AsyncGenerator[AsyncSession]:
    """Get database session"""
    async with get_session() as session:
        yield session


# Инъекция базы данных
SessionDep = Annotated[AsyncSession, Depends(_get_db)]


async def _get_pagination(index: int = 0, count: int = 1000) -> Pagination:
    """Get pagination parameters

    Args:
        index (int, optional): offset. Defaults to 0.
        count (int, optional): limit. Defaults to 1000.
    """
    return Pagination(index=index, count=count)


# Инъекция параметров пагинации
PaginationDep = Annotated[Pagination, Depends(_get_pagination)]
