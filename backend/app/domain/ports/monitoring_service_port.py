"""Universal monitoring service port - abstract interface for monitoring."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MetricData:
    """Metric data model."""
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: Optional[float] = None


@dataclass
class HealthStatus:
    """Health status model."""
    service: str
    status: str  # "healthy", "unhealthy", "degraded"
    response_time: Optional[float] = None
    error_message: Optional[str] = None


class MonitoringServicePort(ABC):
    """Abstract interface for monitoring services."""

    @abstractmethod
    async def record_metric(self, metric: MetricData) -> None:
        """Record a metric."""
        pass

    @abstractmethod
    async def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        pass

    @abstractmethod
    async def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        pass

    @abstractmethod
    async def check_health(self, service_name: str) -> HealthStatus:
        """Check health of a service."""
        pass

    @abstractmethod
    async def log_event(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an event."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the monitoring service itself is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass