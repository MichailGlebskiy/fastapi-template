import logging
import sys

import structlog

from src.core.settings import settings


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Настройка structlog для production и development."""

    # Общие процессоры для всех режимов
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,  # Контекст из contextvars
        structlog.stdlib.add_logger_name,  # Имя логгера
        structlog.stdlib.add_log_level,  # Уровень лога
        structlog.processors.TimeStamper(fmt='iso'),  # ISO timestamp
        structlog.processors.StackInfoRenderer(),  # Stack trace
    ]

    renderer = structlog.dev.ConsoleRenderer(colors=settings.app.dev_mode)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors, processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer]
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    return root_logger
