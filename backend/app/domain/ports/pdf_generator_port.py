"""Universal PDF generator service port - abstract interface for PDF generation."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PDFRequest:
    """Request model for PDF generation operations."""
    content: str
    template: str = "modern"
    title: Optional[str] = None
    author: Optional[str] = None


@dataclass
class PDFResponse:
    """Response model for PDF generation operations."""
    file_path: str
    file_size: int
    download_url: str


class PDFGeneratorPort(ABC):
    """Abstract interface for PDF generation services."""

    @abstractmethod
    async def generate_pdf(self, request: PDFRequest) -> PDFResponse:
        """Generate PDF from content."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the PDF generator service is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass