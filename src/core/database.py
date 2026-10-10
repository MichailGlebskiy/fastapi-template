from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.settings import settings

_engine = create_async_engine(settings.app.database_url, echo=settings.logging.show_sql)

SQLAlchemyInstrumentor().instrument(engine=_engine.sync_engine)

_async_session_maker = async_sessionmaker(_engine, expire_on_commit=False, autoflush=False, autocommit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    """Transactional context"""
    async with _async_session_maker() as session, session.begin():
        yield session
