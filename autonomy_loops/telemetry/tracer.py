"""OpenTelemetry tracing for AutonomyLoops.

Provides distributed tracing across agent loops, tool calls,
and LLM provider requests for performance analysis and debugging.
"""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_initialized = False


def init_tracing(
    service_name: str = "autonomy-loops",
    exporter: str = "console",
    endpoint: str = "http://localhost:4317",
) -> None:
    """Initialize OpenTelemetry tracing.

    Args:
        service_name: Service name for trace identification.
        exporter: Exporter type ("console", "otlp", "none").
        endpoint: OTLP collector endpoint.
    """
    global _initialized
    if _initialized:
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if exporter == "console":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    elif exporter == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except ImportError:
            # Fall back to console if OTLP exporter not installed
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _initialized = True


def get_tracer(name: str = "autonomy-loops") -> trace.Tracer:
    """Get a named tracer instance.

    Args:
        name: Tracer name (typically module or component name).

    Returns:
        OpenTelemetry Tracer instance.
    """
    return trace.get_tracer(name)
