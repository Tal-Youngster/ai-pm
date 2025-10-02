"""OpenTelemetry configuration for the Temporal worker."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanProcessor,
)

if TYPE_CHECKING:
    from worker.settings import Settings

_CONFIGURED = False


def _should_use_console(settings: "Settings") -> bool:
    """Return True when the console exporter should be enabled."""

    return settings.environment.lower() == "development"


def configure_telemetry(settings: "Settings") -> None:
    """Initialise OpenTelemetry exporters for the worker process."""

    global _CONFIGURED

    if _CONFIGURED:
        return

    span_processors: list[SpanProcessor] = []

    if settings.otel_exporter_otlp_endpoint:
        span_processors.append(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
            )
        )

    if _should_use_console(settings):
        span_processors.append(SimpleSpanProcessor(ConsoleSpanExporter()))

    if not span_processors:
        _CONFIGURED = True
        return

    provider = TracerProvider(
        resource=Resource.create({"service.name": "ai-pm-worker"})
    )

    for processor in span_processors:
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    _CONFIGURED = True

