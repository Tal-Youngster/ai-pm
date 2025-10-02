"""OpenTelemetry integration helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanProcessor,
)

if TYPE_CHECKING:
    from app.config import Settings

_OTEL_CONFIGURED_ATTR = "_otel_configured"


def _should_use_console(settings: "Settings") -> bool:
    """Return True when the console exporter should be enabled."""

    return settings.environment.lower() == "development"


def configure_telemetry(app: FastAPI, settings: "Settings") -> None:
    """Configure OpenTelemetry exporters and instrumentation."""

    if getattr(app.state, _OTEL_CONFIGURED_ATTR, False):
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
        return

    resource = Resource.create({"service.name": "ai-pm-api"})
    provider = TracerProvider(resource=resource)

    for processor in span_processors:
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument_app(app)
    setattr(app.state, _OTEL_CONFIGURED_ATTR, True)

