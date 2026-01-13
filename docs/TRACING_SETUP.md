# OpenTelemetry Tracing Setup

This document describes the distributed tracing setup for the JobWise backend using OpenTelemetry and AI Toolkit.

## Overview

The JobWise backend uses **OpenTelemetry** for distributed tracing to provide observability into:
- API request flows
- Database operations
- LLM interactions with Groq
- External HTTP calls
- Performance metrics

Traces are exported to the **AI Toolkit Trace Viewer** for visualization and analysis.

## Architecture

```
┌─────────────────┐
│  FastAPI App    │
│  (Auto-traced)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Tracing │
    │ Middleware│
    └────┬────┘
         │
    ┌────┴────────────────┐
    │  Instrumentation    │
    ├─────────────────────┤
    │ • FastAPI          │
    │ • HTTPx            │
    │ • SQLAlchemy       │
    │ • Custom (Groq)    │
    └────┬────────────────┘
         │
    ┌────┴────────────┐
    │ OTLP Exporter   │
    │ localhost:4318  │
    └────┬────────────┘
         │
    ┌────┴─────────────┐
    │ AI Toolkit       │
    │ Trace Viewer     │
    └──────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

The OpenTelemetry dependencies are already added to `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `opentelemetry-api` - Core tracing API
- `opentelemetry-sdk` - SDK implementation
- `opentelemetry-exporter-otlp` - OTLP exporter for AI Toolkit
- `opentelemetry-instrumentation-fastapi` - Auto-instrumentation for FastAPI
- `opentelemetry-instrumentation-httpx` - Auto-instrumentation for HTTP clients
- `opentelemetry-instrumentation-sqlalchemy` - Auto-instrumentation for database

### 2. Open AI Toolkit Trace Viewer

Before running the application, open the trace viewer:

**In VS Code:**
- Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
- Run: `AI Toolkit: Open Trace Viewer`

Or the trace viewer opens automatically when you install AI Toolkit.

### 3. Run the Application

Start the FastAPI server:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The tracing setup will initialize automatically on startup. You should see:

```
✅ OpenTelemetry tracing initialized for jobwise-backend
📊 Traces are being sent to http://localhost:4318
🔍 Open AI Toolkit Trace Viewer to see traces
```

## What Gets Traced Automatically

### FastAPI Endpoints
All HTTP requests are automatically traced with:
- HTTP method and path
- Status code
- Request/response duration
- Query parameters and headers

### Database Operations
All SQLAlchemy queries are traced with:
- Query text
- Execution time
- Connection pool metrics

### HTTP Client Calls
All outgoing HTTPx requests are traced with:
- Target URL
- Response time
- Status codes

## Custom Tracing for LLM Operations

The `GroqAdapter` includes custom tracing for LLM calls:

```python
with tracer.start_as_current_span("groq.generate_completion") as span:
    span.set_attribute("llm.model", model)
    span.set_attribute("llm.provider", "groq")
    span.set_attribute("llm.prompt_tokens", prompt_tokens)
    span.set_attribute("llm.completion_tokens", completion_tokens)
    span.set_attribute("llm.processing_time_ms", processing_time * 1000)
    # ... LLM call
```

This captures:
- Model name
- Token usage (prompt + completion)
- Processing time
- Error conditions

## Adding Custom Spans

### Method 1: Using the Tracer Directly

```python
from app.core.tracing import get_tracer

tracer = get_tracer(__name__)

async def my_operation(user_id: int):
    with tracer.start_as_current_span("my_operation") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("operation", "data_processing")
        
        # Your operation logic here
        result = await process_data(user_id)
        
        span.set_attribute("result_count", len(result))
        return result
```

### Method 2: Adding Attributes to Current Span

```python
from app.core.tracing import add_span_attributes

@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    # Add custom attributes to the auto-created FastAPI span
    add_span_attributes(
        job_id=job_id,
        operation="fetch_job",
        cache_hit=False
    )
    
    # Your endpoint logic
    job = await job_service.get_job(job_id)
    return job
```

## Viewing Traces

### In AI Toolkit Trace Viewer

1. Open the AI Toolkit panel in VS Code
2. Navigate to "Traces" section
3. View traces in real-time as requests come in

The trace viewer shows:
- **Timeline view**: Visual representation of span hierarchy
- **Span details**: Attributes, events, and timing
- **Performance metrics**: Duration, token usage, errors
- **Search and filter**: Find specific operations

### Trace Attributes

Each trace includes:
- `service.name`: "jobwise-backend"
- `service.version`: "1.0.0"
- `http.*`: HTTP-specific attributes
- `db.*`: Database operation attributes
- `llm.*`: LLM-specific attributes (custom)

## Performance Monitoring

### Key Metrics to Watch

1. **API Response Time**
   - Target: < 200ms for non-LLM endpoints
   - Target: < 3s for LLM-powered endpoints

2. **LLM Token Usage**
   - Monitor `llm.prompt_tokens` and `llm.completion_tokens`
   - Track costs per operation

3. **Database Query Performance**
   - Identify slow queries (> 100ms)
   - Watch for N+1 query patterns

4. **Error Rates**
   - Track spans with `error=true`
   - Monitor LLM API failures

## Troubleshooting

### Traces Not Appearing

1. **Check AI Toolkit is running:**
   ```powershell
   # Trace collector should be on port 4318
   netstat -an | Select-String "4318"
   ```

2. **Verify exporter configuration:**
   - Endpoint: `http://localhost:4318/v1/traces`
   - Protocol: HTTP (not gRPC)

3. **Check application logs:**
   ```
   ✅ OpenTelemetry tracing initialized
   ```

### High Latency

If traces show high latency:
1. Check `llm.processing_time_ms` for LLM bottlenecks
2. Look for slow database queries in `db.*` spans
3. Identify network delays in HTTP client spans

### Memory Issues

The batch span processor buffers traces before export:
- Default batch size: 512 spans
- Default timeout: 5 seconds
- Traces are dropped if exporter is unavailable

## Best Practices

1. **Attribute Naming**: Use semantic conventions
   - HTTP: `http.method`, `http.status_code`
   - Database: `db.system`, `db.statement`
   - Custom: Use namespaces like `llm.*`, `job.*`

2. **Span Granularity**: 
   - Don't create spans for trivial operations
   - Focus on business-critical operations
   - Keep span count per request reasonable (< 50)

3. **Sensitive Data**:
   - Don't log API keys or passwords
   - Sanitize PII from span attributes
   - Use `span.set_status()` for errors, not full error messages with sensitive data

4. **Performance**:
   - Tracing has minimal overhead (< 1ms per span)
   - Batch exporter prevents blocking
   - Disable tracing in production if needed by not calling `setup_tracing()`

## Configuration

Tracing can be configured via environment variables:

```bash
# Disable tracing
OTEL_SDK_DISABLED=true

# Change sampling rate (0.0 to 1.0)
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1  # Sample 10% of traces

# Change exporter endpoint
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## Integration with Other Services

### Future Enhancements

- **Mobile app tracing**: Add OpenTelemetry to Flutter app
- **Log correlation**: Link logs to traces via trace ID
- **Metrics**: Add Prometheus metrics alongside traces
- **Production exporter**: Send to cloud observability platform

## References

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [FastAPI Instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html)
- [AI Toolkit Documentation](https://aka.ms/ai-toolkit)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
