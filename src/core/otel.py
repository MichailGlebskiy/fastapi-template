from logging import Logger

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.structlog import StructlogInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.settings import settings


def setup_otel_providers(logger: Logger, service_name: str = 'template') -> tuple[TracerProvider, LoggerProvider] | tuple[None, None]:
    """Настройки для otel экспортера"""

    if not settings.logging.otel_url:
        logger.warning('otel exporter is not set!')
        return None, None

    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: settings.version,
            'deployment.environment': 'production',
        }
    )

    # 1. Tracing (Трейсы -> otel collector -> tempo | opensearch)
    tracer_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=settings.logging.otel_url, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # 2. Logging (Логи -> OTel Collector -> loki | opensearch)
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    log_exporter = OTLPLogExporter(endpoint=settings.logging.otel_url, insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    StructlogInstrumentor().instrument(logger_provider=logger_provider)
    # HTTPX2ClientInstrumentor().instrument()

    return tracer_provider, logger_provider

    # HTTPX2ClientInstrumentor().instrument()
