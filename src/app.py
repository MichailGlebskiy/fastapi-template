from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logging import setup_logging
from src.core.otel import setup_otel_providers
from src.core.settings import settings
from src.middleware.logging import logging_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger = setup_logging()
    setup_otel_providers(logger)
    yield


logger = setup_logging()
tracer_provider, logger_provider = setup_otel_providers(logger)
app = FastAPI(
    **settings.app_config,
    lifespan=lifespan,
    telemetry={
        'tracer_provider': tracer_provider,
        'logger_provider': logger_provider,
        'operation_spans': True,
    },
)


# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.middleware('http')(logging_middleware)


@app.get('/')
def read_root() -> str:
    return 'Hello'
