import os
from uuid import uuid4
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.sdk._logs.export import LogExporter
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricExporter, ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer


resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "recognition-service",
    ResourceAttributes.SERVICE_NAMESPACE: "iot-monitor",
    ResourceAttributes.SERVICE_VERSION: "v0",
    ResourceAttributes.SERVICE_INSTANCE_ID: uuid4().hex,
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "development", # fixme: switch to production after online
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

    reader = PeriodicExportingMetricReader(create_meter_exporter())
    meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
    set_meter_provider(meterProvider)

    GrpcInstrumentorServer().instrument()



def create_trace_exporter() -> SpanExporter:
    """Setup the OpenTelemetry OTLP Span Exporter."""

    if os.getenv("IOT_RECOGNITION_EXPORTER_CONSOLE") == "true":
        return ConsoleSpanExporter()

    return OTLPSpanExporter()


def create_log_exporter() -> LogExporter:
    """Setup the OpenTelemetry OTLP Log Exporter."""

    if os.getenv("IOT_RECOGNITION_EXPORTER_CONSOLE") == "true":
        return ConsoleLogExporter()

    return OTLPLogExporter()


def create_meter_exporter() -> MetricExporter:
    """Setup the OpenTelemetry OTLP Metric Exporter."""

    if os.getenv("IOT_RECOGNITION_EXPORTER_CONSOLE") == "true":
        return ConsoleMetricExporter()

    return OTLPMetricExporter()
