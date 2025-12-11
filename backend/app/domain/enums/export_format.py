"""Export format enum."""

from enum import Enum


class ExportFormat(Enum):
    """Export file formats."""
    
    PDF = "pdf"
    DOCX = "docx"
    ZIP = "zip"
