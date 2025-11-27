"""
Observability configuration for Riva AI.
"""
import os
from typing import Optional
from pydantic import BaseModel


class ObservabilityConfig(BaseModel):
    """Configuration for observability features."""
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    # Tracing
    enable_tracing: bool = True
    enable_cloud_trace: bool = False
    trace_sample_rate: float = 1.0
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Google Cloud
    google_cloud_project: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "ObservabilityConfig":
        """Create config from environment variables."""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            enable_tracing=os.getenv("ENABLE_TRACING", "true").lower() == "true",
            enable_cloud_trace=os.getenv("ENABLE_CLOUD_TRACE", "false").lower() == "true",
            trace_sample_rate=float(os.getenv("TRACE_SAMPLE_RATE", "1.0")),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        )


# Global config instance
_config: Optional[ObservabilityConfig] = None


def get_observability_config() -> ObservabilityConfig:
    """Get or create global observability config."""
    global _config
    if _config is None:
        _config = ObservabilityConfig.from_env()
    return _config
