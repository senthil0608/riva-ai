"""
Prometheus metrics for Riva AI agents.
Aligned with Google Cloud Monitoring and Google ADK best practices.
"""
import time
from typing import Optional
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class ADKMetrics:
    """
    Prometheus metrics collector for Riva AI agents.
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        
        if not self.enabled:
            if not PROMETHEUS_AVAILABLE:
                print("Warning: Prometheus client not available. Metrics disabled.")
            return
        
        # Agent metrics
        self.agent_executions = Counter(
            'riva_agent_executions_total',
            'Total number of agent executions',
            ['agent_name', 'status']
        )
        
        self.agent_duration = Histogram(
            'riva_agent_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_name'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )
        
        # Tool metrics
        self.tool_calls = Counter(
            'riva_tool_calls_total',
            'Total number of tool calls',
            ['tool_name', 'status']
        )
        
        self.tool_duration = Histogram(
            'riva_tool_duration_seconds',
            'Tool execution duration in seconds',
            ['tool_name'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
        )
        
        # API metrics
        self.api_requests = Counter(
            'riva_api_requests_total',
            'Total number of API requests',
            ['endpoint', 'method', 'status_code']
        )
        
        self.api_duration = Histogram(
            'riva_api_duration_seconds',
            'API request duration in seconds',
            ['endpoint', 'method'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
        )
        
        # Error metrics
        self.errors = Counter(
            'riva_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        # System metrics
        self.active_requests = Gauge(
            'riva_active_requests',
            'Number of active requests',
            ['type']
        )
        
        # Info metric
        self.info = Info(
            'riva_build',
            'Build information'
        )
        self.info.info({
            'version': '1.0.0',
            'service': 'riva-ai'
        })
    
    def record_agent_execution(
        self,
        agent_name: str,
        duration_seconds: float,
        status: str = "success"
    ):
        """Record agent execution metrics."""
        if not self.enabled:
            return
        
        self.agent_executions.labels(
            agent_name=agent_name,
            status=status
        ).inc()
        
        self.agent_duration.labels(
            agent_name=agent_name
        ).observe(duration_seconds)
    
    def record_tool_call(
        self,
        tool_name: str,
        duration_seconds: float,
        status: str = "success"
    ):
        """Record tool call metrics."""
        if not self.enabled:
            return
        
        self.tool_calls.labels(
            tool_name=tool_name,
            status=status
        ).inc()
        
        self.tool_duration.labels(
            tool_name=tool_name
        ).observe(duration_seconds)
    
    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_seconds: float
    ):
        """Record API request metrics."""
        if not self.enabled:
            return
        
        self.api_requests.labels(
            endpoint=endpoint,
            method=method,
            status_code=status_code
        ).inc()
        
        self.api_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration_seconds)
    
    def record_error(
        self,
        error_type: str,
        component: str
    ):
        """Record error metrics."""
        if not self.enabled:
            return
        
        self.errors.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    @contextmanager
    def track_agent(self, agent_name: str):
        """Context manager to track agent execution."""
        start_time = time.time()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "error"
            self.record_error(type(e).__name__, f"agent.{agent_name}")
            raise
        finally:
            duration = time.time() - start_time
            self.record_agent_execution(agent_name, duration, status)
    
    @contextmanager
    def track_tool(self, tool_name: str):
        """Context manager to track tool execution."""
        start_time = time.time()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "error"
            self.record_error(type(e).__name__, f"tool.{tool_name}")
            raise
        finally:
            duration = time.time() - start_time
            self.record_tool_call(tool_name, duration, status)
    
    @contextmanager
    def track_api(self, endpoint: str, method: str = "POST"):
        """Context manager to track API request."""
        start_time = time.time()
        status_code = 200
        
        self.active_requests.labels(type="api").inc()
        
        try:
            yield lambda code: setattr(self, '_status_code', code)
        except Exception as e:
            status_code = 500
            self.record_error(type(e).__name__, "api")
            raise
        finally:
            duration = time.time() - start_time
            final_status = getattr(self, '_status_code', status_code)
            self.record_api_request(endpoint, method, final_status, duration)
            self.active_requests.labels(type="api").dec()
    
    def get_metrics(self) -> bytes:
        """Get current metrics in Prometheus format."""
        if not self.enabled:
            return b""
        
        return generate_latest(REGISTRY)


# Global metrics instance
_metrics: Optional[ADKMetrics] = None


def get_metrics(enabled: bool = True) -> ADKMetrics:
    """Get or create global metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = ADKMetrics(enabled)
    return _metrics


# Convenience instance
metrics = get_metrics()
