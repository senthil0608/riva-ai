"""
Structured logging for Riva AI agents.
Aligned with Google Cloud Logging format and Google ADK best practices.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(str, Enum):
    """Log severity levels aligned with Google Cloud Logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs.
    Compatible with Google Cloud Logging and local development.
    """
    
    def __init__(self, name: str = "riva_ai", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Configure handler
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._get_formatter())
            self.logger.addHandler(handler)
    
    def _get_formatter(self):
        """Get JSON formatter for structured logging."""
        return JsonFormatter()
    
    def _log(
        self,
        severity: str,
        message: str,
        **kwargs
    ):
        """Internal log method with structured fields."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity,
            "message": message,
            "logger": self.name,
            **kwargs
        }
        
        # Log as JSON string
        self.logger.log(
            getattr(logging, severity),
            json.dumps(log_entry)
        )
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    # Agent-specific logging methods
    
    def log_agent_start(
        self,
        agent_name: str,
        student_id: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log agent execution start."""
        self.info(
            f"Agent {agent_name} started",
            agent_name=agent_name,
            student_id=student_id,
            event_type="agent_start",
            context=context or {}
        )
    
    def log_agent_complete(
        self,
        agent_name: str,
        duration_ms: float,
        result: Optional[Dict[str, Any]] = None
    ):
        """Log agent execution completion."""
        self.info(
            f"Agent {agent_name} completed",
            agent_name=agent_name,
            duration_ms=duration_ms,
            event_type="agent_complete",
            result_summary=self._summarize_result(result)
        )
    
    def log_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        agent_name: Optional[str] = None
    ):
        """Log tool invocation."""
        self.debug(
            f"Tool {tool_name} called",
            tool_name=tool_name,
            agent_name=agent_name,
            params=params,
            event_type="tool_call"
        )
    
    def log_tool_result(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Log tool execution result."""
        level = "info" if success else "error"
        getattr(self, level)(
            f"Tool {tool_name} {'succeeded' if success else 'failed'}",
            tool_name=tool_name,
            duration_ms=duration_ms,
            success=success,
            error=error,
            event_type="tool_result"
        )
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        student_id: Optional[str] = None
    ):
        """Log API request."""
        self.info(
            f"API request: {method} {endpoint}",
            endpoint=endpoint,
            method=method,
            student_id=student_id,
            event_type="api_request"
        )
    
    def log_api_response(
        self,
        endpoint: str,
        status_code: int,
        duration_ms: float
    ):
        """Log API response."""
        level = "info" if status_code < 400 else "error"
        getattr(self, level)(
            f"API response: {endpoint} - {status_code}",
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            event_type="api_response"
        )
    
    def log_error_with_context(
        self,
        error: Exception,
        context: Dict[str, Any]
    ):
        """Log error with full context."""
        self.error(
            f"Error: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            event_type="error",
            **context
        )
    
    def _summarize_result(self, result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize result for logging (avoid logging large payloads)."""
        if not result:
            return {}
        
        summary = {}
        for key, value in result.items():
            if isinstance(value, list):
                summary[key] = f"<list of {len(value)} items>"
            elif isinstance(value, dict):
                summary[key] = f"<dict with {len(value)} keys>"
            else:
                summary[key] = value
        
        return summary


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        # If message is already JSON, return as-is
        if record.msg.startswith('{'):
            return record.msg
        
        # Otherwise, create JSON structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        
        return json.dumps(log_entry)


# Global logger instance
_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "riva_ai", log_level: str = "INFO") -> StructuredLogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name, log_level)
    return _logger


# Convenience instance
logger = get_logger()
