"""Universal cache service port - abstract interface for caching."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import timedelta


class CacheServicePort(ABC):
    """Abstract interface for cache services."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the cache service is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass