import logging
import os
from uuid import uuid4
from opentelemetry.trace import set_tracer_provider
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import ConsoleLogExporter, BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.sdk._logs.export import LogExporter


resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "iot-recognition-service",
    ResourceAttributes.SERVICE_VERSION: "v0",
    ResourceAttributes.SERVICE_INSTANCE_ID: uuid4().hex,
}, schema_url=ResourceAttributes.SCHEMA_URL)


def setup_telemetry() -> None:
    """Setup the OpenTelemetry SDK for Baselime, and instrument the gRPC client."""

    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(create_trace_exporter())
    )
    set_tracer_provider(trace_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
       BatchLogRecordProcessor(create_log_exporter())
    )
    set_logger_provider(logger_provider)

    GrpcInstrumentorClient().instrument()


def create_trace_exporter() -> SpanExporter:
    """Setup the OpenTelemetry OTLP Span Exporter for Baselime."""

    baselime_api_key = os.getenv("BASELIME_API_KEY")
    if not baselime_api_key:
        logging.warn("BASELIME_API_KEY is not set. Using the stdout OTLP exporter.")
        return ConsoleSpanExporter()

    baselime_dataset = os.getenv("BASELIME_DATASET", "otel")

    return OTLPSpanExporter(endpoint="otel.baselime.io/v1/traces", headers={
        "x-api-key": baselime_api_key,
        "x-baselime-dataset": baselime_dataset,
    })


def create_log_exporter() -> LogExporter:
    """Setup the OpenTelemetry OTLP Log Exporter for Baselime."""

    baselime_api_key = os.getenv("BASELIME_API_KEY")
    if not baselime_api_key:
        logging.warn("BASELIME_API_KEY is not set. Using the stdout OTLP exporter.")
        return ConsoleLogExporter()

    baselime_dataset = os.getenv("BASELIME_DATASET", "otel")

    return OTLPLogExporter(endpoint="otel.baselime.io/v1/logs", headers={
        "x-api-key": baselime_api_key,
        "x-baselime-dataset": baselime_dataset,
    })

