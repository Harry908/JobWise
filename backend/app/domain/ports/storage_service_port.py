"""Universal storage service port - abstract interface for file storage."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from dataclasses import dataclass


@dataclass
class StorageUploadRequest:
    """Request model for file upload operations."""
    file: BinaryIO
    filename: str
    content_type: Optional[str] = None
    folder: str = "documents"


@dataclass
class StorageUploadResponse:
    """Response model for file upload operations."""
    file_path: str
    file_url: str
    file_size: int


class StorageServicePort(ABC):
    """Abstract interface for storage services."""

    @abstractmethod
    async def upload_file(self, request: StorageUploadRequest) -> StorageUploadResponse:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> Optional[BinaryIO]:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for file access."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the storage service is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass