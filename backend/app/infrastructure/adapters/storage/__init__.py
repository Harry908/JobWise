"""Storage adapters package."""

from .storage_interface import StorageInterface
from .s3_adapter import S3StorageAdapter, get_s3_adapter

__all__ = [
    'StorageInterface',
    'S3StorageAdapter',
    'get_s3_adapter',
]
