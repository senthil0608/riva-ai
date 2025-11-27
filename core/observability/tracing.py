"""
OpenTelemetry tracing for Riva AI agents.
Aligned with Google Cloud Trace and Google ADK best practices.
"""
import os
import time
from typing import Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    
    # Try to import Google Cloud Trace exporter
    try:
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        CLOUD_TRACE_AVAILABLE = True
    except ImportError:
        CLOUD_TRACE_AVAILABLE = False
    
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    CLOUD_TRACE_AVAILABLE = False


class ADKTracer:
    """
    OpenTelemetry tracer for Riva AI agents.
    Supports both local console export and Google Cloud Trace.
    """
    
    def __init__(
        self,
        service_name: str = "riva-ai",
        enable_cloud_trace: bool = False,
        project_id: Optional[str] = None
    ):
        self.service_name = service_name
        self.enabled = OTEL_AVAILABLE
        
        if not self.enabled:
            print("Warning: OpenTelemetry not available. Tracing disabled.")
            return
        
        # Create resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0"
        })
        
        # Create tracer provider
        provider = TracerProvider(resource=resource)
        
        # Add console exporter for local development
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        # Add Cloud Trace exporter if enabled
        if enable_cloud_trace and CLOUD_TRACE_AVAILABLE and project_id:
            try:
                cloud_exporter = CloudTraceSpanExporter(project_id=project_id)
                provider.add_span_processor(BatchSpanProcessor(cloud_exporter))
                print(f"✓ Cloud Trace enabled for project: {project_id}")
            except Exception as e:
                print(f"Warning: Could not enable Cloud Trace: {e}")
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)
    
    @contextmanager
    def trace_span(self, name: str, attributes: Optional[dict] = None):
        """Create a trace span context manager."""
        if not self.enabled:
            yield None
            return
        
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            yield span
    
    def trace_agent(self, agent_name: str):
        """Decorator to trace agent execution."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                with self.trace_span(
                    f"agent.{agent_name}",
                    attributes={
                        "agent.name": agent_name,
                        "agent.type": "adk_agent"
                    }
                ) as span:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        if span:
                            span.set_attribute("agent.status", "success")
                        return result
                    except Exception as e:
                        if span:
                            span.set_attribute("agent.status", "error")
                            span.set_attribute("error.type", type(e).__name__)
                            span.set_attribute("error.message", str(e))
                        raise
                    finally:
                        duration = (time.time() - start_time) * 1000
                        if span:
                            span.set_attribute("agent.duration_ms", duration)
            
            return wrapper
        return decorator
    
    def trace_tool(self, tool_name: str):
        """Decorator to trace tool execution."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                with self.trace_span(
                    f"tool.{tool_name}",
                    attributes={
                        "tool.name": tool_name,
                        "tool.type": "function"
                    }
                ) as span:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        if span:
                            span.set_attribute("tool.status", "success")
                        return result
                    except Exception as e:
                        if span:
                            span.set_attribute("tool.status", "error")
                            span.set_attribute("error.type", type(e).__name__)
                            span.set_attribute("error.message", str(e))
                        raise
                    finally:
                        duration = (time.time() - start_time) * 1000
                        if span:
                            span.set_attribute("tool.duration_ms", duration)
            
            return wrapper
        return decorator
    
    @contextmanager
    def trace_api_call(self, endpoint: str, method: str = "POST"):
        """Trace an API call."""
        if not self.enabled:
            yield None
            return
        
        with self.trace_span(
            f"api.{method}.{endpoint}",
            attributes={
                "http.method": method,
                "http.route": endpoint,
                "http.type": "api_call"
            }
        ) as span:
            yield span


# Global tracer instance
_tracer: Optional[ADKTracer] = None


def get_tracer(
    service_name: str = "riva-ai",
    enable_cloud_trace: bool = False,
    project_id: Optional[str] = None
) -> ADKTracer:
    """Get or create global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = ADKTracer(service_name, enable_cloud_trace, project_id)
    return _tracer


# Convenience instance
tracer = get_tracer(
    enable_cloud_trace=os.getenv("ENABLE_CLOUD_TRACE", "false").lower() == "true",
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
)
