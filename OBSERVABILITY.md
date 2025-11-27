# Observability Guide - Riva AI

Comprehensive logging, tracing, and metrics for Riva AI agents aligned with Google ADK best practices.

## Overview

Riva AI includes production-ready observability:
- **Structured Logging** - JSON logs compatible with Google Cloud Logging
- **OpenTelemetry Tracing** - Distributed tracing with Google Cloud Trace support
- **Prometheus Metrics** - Performance monitoring and alerting

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)

Edit `.env` file:
```bash
# Logging
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json         # json or text

# Tracing
ENABLE_TRACING=true
ENABLE_CLOUD_TRACE=false  # Set to true for Google Cloud Trace
TRACE_SAMPLE_RATE=1.0

# Metrics
ENABLE_METRICS=true
METRICS_PORT=9090

# Google Cloud (for Cloud Trace)
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Run with Observability

```bash
python3 server.py
```

Access:
- **API**: http://localhost:8000
- **Metrics**: http://localhost:8000/metrics
- **Docs**: http://localhost:8000/docs

## Features

### Structured Logging

**JSON Format:**
```json
{
  "timestamp": "2024-11-25T19:00:00Z",
  "severity": "INFO",
  "message": "Agent classroom_sync started",
  "agent_name": "classroom_sync",
  "student_id": "demo-student",
  "event_type": "agent_start"
}
```

**Usage in Code:**
```python
from core.observability import logger

# Simple logging
logger.info("Processing request", student_id="123")

# Agent logging
logger.log_agent_start("agent_name", "student_id")
logger.log_agent_complete("agent_name", duration_ms=150.5)

# Tool logging
logger.log_tool_call("tool_name", {"param": "value"})

# Error logging
logger.log_error_with_context(exception, {"context": "data"})
```

### OpenTelemetry Tracing

**Automatic Tracing:**
- All API requests traced
- Agent executions traced
- Tool calls traced

**Usage in Code:**
```python
from core.observability import tracer

# Decorator for agents
@tracer.trace_agent("agent_name")
def run_agent(student_id):
    # Agent logic
    pass

# Decorator for tools
@tracer.trace_tool("tool_name")
def tool_function(param):
    # Tool logic
    pass

# Manual tracing
with tracer.trace_span("custom_operation", {"key": "value"}):
    # Your code
    pass
```

**View Traces:**
- Local: Console output
- Cloud: Google Cloud Trace (if enabled)

### Prometheus Metrics

**Available Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `riva_agent_executions_total` | Counter | Agent execution count |
| `riva_agent_duration_seconds` | Histogram | Agent execution time |
| `riva_tool_calls_total` | Counter | Tool call count |
| `riva_tool_duration_seconds` | Histogram | Tool execution time |
| `riva_api_requests_total` | Counter | API request count |
| `riva_api_duration_seconds` | Histogram | API response time |
| `riva_errors_total` | Counter | Error count |
| `riva_active_requests` | Gauge | Active requests |

**Usage in Code:**
```python
from core.observability import metrics

# Track agent execution
with metrics.track_agent("agent_name"):
    # Agent logic
    pass

# Track tool call
with metrics.track_tool("tool_name"):
    # Tool logic
    pass

# Manual recording
metrics.record_agent_execution("agent_name", duration_seconds=0.5, status="success")
metrics.record_error("ValueError", "agent.classroom_sync")
```

**View Metrics:**
```bash
curl http://localhost:8000/metrics
```

**Example Output:**
```
# HELP riva_agent_executions_total Agent executions
# TYPE riva_agent_executions_total counter
riva_agent_executions_total{agent_name="classroom_sync",status="success"} 42.0

# HELP riva_agent_duration_seconds Agent execution duration
# TYPE riva_agent_duration_seconds histogram
riva_agent_duration_seconds_bucket{agent_name="classroom_sync",le="0.1"} 10.0
riva_agent_duration_seconds_bucket{agent_name="classroom_sync",le="0.5"} 35.0
riva_agent_duration_seconds_sum{agent_name="classroom_sync"} 12.5
riva_agent_duration_seconds_count{agent_name="classroom_sync"} 42.0
```

## Integration Examples

### Agent with Observability

```python
from core.observability import logger, tracer, metrics
import time

@tracer.trace_agent("my_agent")
def run_my_agent(student_id: str):
    logger.log_agent_start("my_agent", student_id)
    
    with metrics.track_agent("my_agent"):
        start_time = time.time()
        
        # Agent logic here
        result = {"data": "value"}
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_agent_complete("my_agent", duration_ms, result)
        
        return result
```

### API Endpoint with Observability

Observability is automatic via middleware! Just write your endpoint:

```python
@app.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # Automatically logged, traced, and metered
    result = run_my_agent(request.student_id)
    return result
```

## Google Cloud Integration

### Enable Cloud Trace

1. **Set up Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

2. **Configure environment:**
   ```bash
   ENABLE_CLOUD_TRACE=true
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

3. **Run server:**
   ```bash
   python3 server.py
   ```

4. **View traces:**
   - Go to: https://console.cloud.google.com/traces
   - Select your project
   - View distributed traces

### Enable Cloud Logging

1. **Install handler:**
   ```bash
   pip install google-cloud-logging
   ```

2. **Configure in code:**
   ```python
   from google.cloud import logging as cloud_logging
   
   client = cloud_logging.Client()
   client.setup_logging()
   ```

3. **View logs:**
   - Go to: https://console.cloud.google.com/logs
   - Filter by service: riva-ai

## Monitoring Dashboard

### Prometheus + Grafana

1. **Start Prometheus:**
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'riva-ai'
       static_configs:
         - targets: ['localhost:8000']
       metrics_path: '/metrics'
   ```

2. **Run Prometheus:**
   ```bash
   prometheus --config.file=prometheus.yml
   ```

3. **Add to Grafana:**
   - Add Prometheus data source
   - Import Riva AI dashboard
   - Monitor metrics in real-time

### Key Metrics to Monitor

- **Agent Performance**: `riva_agent_duration_seconds`
- **Error Rate**: `riva_errors_total`
- **API Latency**: `riva_api_duration_seconds`
- **Active Load**: `riva_active_requests`

## Troubleshooting

### No Logs Appearing

```bash
# Check log level
LOG_LEVEL=DEBUG python3 server.py

# Check logger
python3 -c "from core.observability import logger; logger.info('test')"
```

### Traces Not Showing

```bash
# Check tracing enabled
ENABLE_TRACING=true python3 server.py

# Check OpenTelemetry installed
pip install opentelemetry-api opentelemetry-sdk
```

### Metrics Not Available

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus client installed
pip install prometheus-client
```

## Best Practices

1. **Use Structured Logging** - Always use logger with context fields
2. **Trace Critical Paths** - Use @tracer decorators on important functions
3. **Monitor Error Rates** - Set up alerts on `riva_errors_total`
4. **Track Latency** - Monitor p95/p99 latencies
5. **Sample in Production** - Use `TRACE_SAMPLE_RATE=0.1` for high traffic

## Summary

✅ **Structured JSON logging** - Google Cloud Logging compatible
✅ **OpenTelemetry tracing** - Google Cloud Trace integration
✅ **Prometheus metrics** - Production monitoring
✅ **Automatic middleware** - No code changes needed
✅ **Google ADK aligned** - Best practices followed

**Built for production observability!** 📊
