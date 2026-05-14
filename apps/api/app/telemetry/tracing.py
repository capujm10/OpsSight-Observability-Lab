from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config.settings import Settings


def configure_tracing(app, settings: Settings) -> None:
    if not settings.otel_enabled:
        return

    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "service.version": settings.service_version,
            "deployment.environment": settings.environment,
        }
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    HTTPXClientInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=False)


def current_trace_id() -> str:
    span = trace.get_current_span()
    context = span.get_span_context()
    if not context.is_valid:
        return "-"
    return f"{context.trace_id:032x}"
