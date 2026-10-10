from logging import Logger

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.settings import settings


def setup_otel_providers(logger: Logger, log_level: str = 'INFO', service_name: str = 'gcc') -> LoggerProvider | None:
    """Otel exporter setup"""

    if not settings.logging.otel_url:
        return None

    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: settings.version,
            'deployment.environment': 'production',
        }
    )

    # 1. Tracing (Tempo)
    tracer_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=settings.logging.otel_url, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # 2. Logging (OTel Collector)
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    log_exporter = OTLPLogExporter(endpoint=settings.logging.otel_url, insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    otel_handler = LoggingHandler(logger_provider=logger_provider)
    otel_handler.setLevel(log_level)
    logger.addHandler(otel_handler)
    return logger_provider


def setup_instrumentation(app: FastAPI) -> None:
    FastAPIInstrumentor.instrument_app(app)
    # other instrumentation
    # HTTPXClientInstrumentor().instrument()
