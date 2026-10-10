import logging
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request
from fastapi.responses import Response

logger = structlog.get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Add log context"""

    import time
    import uuid

    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    start_time = time.perf_counter()

    # Bind context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        if response.status_code >= 500:
            level = logging.ERROR
            event = 'request_failed'
        elif response.status_code >= 400:
            level = logging.WARNING
            event = 'request_client_error'
        else:
            level = logging.INFO
            event = 'request_completed'

        await logger.alog(level, event, status_code=response.status_code, duration_ms=round(duration_ms, 2))

        response.headers['X-Request-ID'] = request_id
        return response

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        await logger.aerror(
            'request_failed',
            error=str(exc),
            error_type=type(exc).__name__,
            duration_ms=round(duration_ms, 2),
        )
        raise
