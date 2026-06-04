import os
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

OTEL_COLLECTOR_URL = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")

_METER_PROVIDER = None
_TRACER_PROVIDER = None

def setup_otel(service_name):
    global _METER_PROVIDER, _TRACER_PROVIDER
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    # Metrics Setup
    metric_exporter = OTLPMetricExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
    reader = PeriodicExportingMetricReader(metric_exporter)
    _METER_PROVIDER = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(_METER_PROVIDER)

    # Tracing Setup
    _TRACER_PROVIDER = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
    span_processor = BatchSpanProcessor(trace_exporter)
    _TRACER_PROVIDER.add_span_processor(span_processor)
    trace.set_tracer_provider(_TRACER_PROVIDER)

    return metrics.get_meter(service_name), trace.get_tracer(service_name)

def flush_otel():
    if _METER_PROVIDER:
        _METER_PROVIDER.force_flush()
    if _TRACER_PROVIDER:
        _TRACER_PROVIDER.force_flush()
