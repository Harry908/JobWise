"""OpenTelemetry tracing configuration for JobWise backend."""

import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

logger = logging.getLogger(__name__)


def setup_tracing(app, service_name: str = "jobwise-backend", service_version: str = "1.0.0"):
    """
    Set up OpenTelemetry tracing for the FastAPI application.
    
    This configures:
    - OTLP exporter to AI Toolkit trace collector (http://localhost:4318)
    - Automatic instrumentation for FastAPI, HTTPx, and SQLAlchemy
    - Service resource attributes for trace identification
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for tracing
        service_version: Version of the service
    """
    try:
        # Create resource with service information
        resource = Resource(attributes={
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
        })
        
        # Create tracer provider with resource
        provider = TracerProvider(resource=resource)
        
        # Configure OTLP exporter to AI Toolkit (HTTP endpoint)
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://localhost:4318/v1/traces",
            timeout=5,
        )
        
        # Add batch span processor
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
        
        # Set the global tracer provider
        trace.set_tracer_provider(provider)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
        
        # Instrument HTTPx for outgoing HTTP requests
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPx instrumentation enabled")
        
        # Instrument SQLAlchemy (will auto-detect database connections)
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy instrumentation enabled")
        
        logger.info(f"✅ OpenTelemetry tracing initialized for {service_name}")
        logger.info("📊 Traces are being sent to http://localhost:4318")
        logger.info("🔍 Open AI Toolkit Trace Viewer to see traces")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize tracing: {e}")
        logger.warning("Application will continue without tracing")


def get_tracer(name: str = "jobwise-backend"):
    """
    Get a tracer instance for manual span creation.
    
    Use this for custom instrumentation when automatic instrumentation
    doesn't capture the operations you need to trace.
    
    Args:
        name: Name of the tracer
        
    Returns:
        Tracer instance
        
    Example:
        ```python
        from app.core.tracing import get_tracer
        
        tracer = get_tracer(__name__)
        
        with tracer.start_as_current_span("custom_operation") as span:
            span.set_attribute("user_id", user_id)
            # Your operation here
            result = do_something()
            span.set_attribute("result_count", len(result))
        ```
    """
    return trace.get_tracer(name)


def add_span_attributes(**attributes):
    """
    Add attributes to the current active span.
    
    This is useful for adding custom metadata to automatically created spans.
    
    Args:
        **attributes: Key-value pairs to add as span attributes
        
    Example:
        ```python
        from app.core.tracing import add_span_attributes
        
        @app.get("/jobs/{job_id}")
        async def get_job(job_id: int):
            add_span_attributes(job_id=job_id, operation="fetch_job")
            # Your endpoint logic
        ```
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        for key, value in attributes.items():
            current_span.set_attribute(str(key), str(value))
