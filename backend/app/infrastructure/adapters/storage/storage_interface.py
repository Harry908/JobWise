"""Storage adapter interface for document exports."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any


class StorageInterface(ABC):
    """
    Abstract interface for storage backends.
    
    Implementations must enforce user-scoped access control
    and secure file handling.
    """
    
    @abstractmethod
    def upload_file(
        self,
        file_obj: BinaryIO,
        user_id: str,
        export_id: str,
        format: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file with user-scoped access control.
        
        Returns:
            Dict with storage metadata (key, size, etag, etc.)
        """
        pass
    
    @abstractmethod
    def download_file(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> BinaryIO:
        """
        Download a file with ownership verification.
        
        Returns:
            File-like object
        """
        pass
    
    @abstractmethod
    def generate_presigned_url(
        self,
        user_id: str,
        export_id: str,
        format: str,
        expiration_seconds: int = 3600,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate time-limited presigned URL for downloads.
        
        Returns:
            Presigned URL string
        """
        pass
    
    @abstractmethod
    def delete_file(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> bool:
        """
        Delete a file with ownership verification.
        
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    def get_file_metadata(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> Dict[str, Any]:
        """
        Get file metadata without downloading.
        
        Returns:
            Dict with size, last_modified, content_type, etc.
        """
        pass
    
    @abstractmethod
    def list_user_exports(
        self,
        user_id: str,
        max_keys: int = 100
    ) -> list[Dict[str, Any]]:
        """
        List all exports for a user.
        
        Returns:
            List of file metadata dicts
        """
        pass
