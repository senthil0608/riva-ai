"""
Observability package for Riva AI.
Provides logging, tracing, and metrics aligned with Google ADK best practices.
"""

from .logging import logger, get_logger, StructuredLogger
from .tracing import tracer, get_tracer, ADKTracer
from .metrics import metrics, get_metrics, ADKMetrics
from .config import ObservabilityConfig, get_observability_config

__all__ = [
    # Logging
    'logger',
    'get_logger',
    'StructuredLogger',
    # Tracing
    'tracer',
    'get_tracer',
    'ADKTracer',
    # Metrics
    'metrics',
    'get_metrics',
    'ADKMetrics',
    # Config
    'ObservabilityConfig',
    'get_observability_config',
]
