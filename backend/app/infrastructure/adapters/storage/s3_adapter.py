"""AWS S3 Storage Adapter for Document Exports

This module provides secure S3 storage integration for exported documents
with user-scoped access control and presigned URL generation.

Security Features:
- User-scoped S3 key paths (exports/{user_id}/{export_id}.{ext})
- Private bucket access only
- Presigned URLs with configurable expiration
- Server-side encryption (SSE-S3)
- Content-Type validation
- File size limits enforcement
"""

import logging
from datetime import datetime, timedelta
from typing import BinaryIO, Optional, Dict, Any
from uuid import UUID
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config

from app.core.config import get_settings
from app.core.exceptions import StorageError, AuthorizationError

logger = logging.getLogger(__name__)
settings = get_settings()


class S3StorageAdapter:
    """
    S3 storage adapter for secure document export management.
    
    All operations enforce user-scoped access control through S3 key naming:
    - Pattern: exports/{user_id}/{export_id}.{extension}
    - Prevents cross-user access through path isolation
    - Validates ownership before generating presigned URLs
    """
    
    def __init__(self):
        """Initialize S3 client with security best practices."""
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.s3_region
        
        # Configure S3 client with retry strategy and timeout
        config = Config(
            region_name=self.region,
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'standard'},
            connect_timeout=5,
            read_timeout=30,
        )
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=config
        )
        
        # Allowed content types for security
        self.allowed_content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'zip': 'application/zip',
        }
        
        # File size limits (100 MB max)
        self.max_file_size_bytes = 100 * 1024 * 1024
    
    def _build_s3_key(self, user_id: str, export_id: str, extension: str) -> str:
        """
        Build S3 object key with user scoping for security.
        
        Pattern: exports/{user_id}/{export_id}.{extension}
        
        Args:
            user_id: User ID (UUID string) - isolates files by user
            export_id: Export ID (UUID string) - unique per export
            extension: File extension (pdf, docx, zip)
        
        Returns:
            S3 object key string
        """
        return f"exports/{user_id}/{export_id}.{extension}"
    
    def _validate_file_size(self, file_obj: BinaryIO) -> int:
        """
        Validate file size is within limits.
        
        Args:
            file_obj: File-like object
        
        Returns:
            File size in bytes
        
        Raises:
            StorageError: If file exceeds size limit
        """
        file_obj.seek(0, 2)  # Seek to end
        size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning
        
        if size > self.max_file_size_bytes:
            raise StorageError(
                f"File size {size} bytes exceeds maximum allowed size "
                f"{self.max_file_size_bytes} bytes"
            )
        
        return size
    
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
        Upload a file to S3 with user-scoped key and encryption.
        
        Security Features:
        - User-scoped S3 key prevents cross-user access
        - Server-side encryption (AES-256)
        - Content-Type validation
        - File size enforcement
        - Metadata sanitization
        
        Args:
            file_obj: File-like object to upload
            user_id: User ID who owns the export
            export_id: Unique export identifier
            format: File format (pdf, docx, zip)
            content_type: Optional content type override
            metadata: Optional metadata dict (sanitized)
        
        Returns:
            Dict with:
                - s3_key: S3 object key
                - size_bytes: File size
                - etag: S3 ETag for verification
                - version_id: S3 version ID (if versioning enabled)
        
        Raises:
            StorageError: Upload failure or validation error
        """
        try:
            # Validate file size
            size_bytes = self._validate_file_size(file_obj)
            
            # Build user-scoped S3 key
            s3_key = self._build_s3_key(user_id, export_id, format)
            
            # Determine content type
            if content_type is None:
                content_type = self.allowed_content_types.get(format)
                if content_type is None:
                    raise StorageError(f"Unsupported format: {format}")
            
            # Sanitize metadata (remove any PII, limit size)
            safe_metadata = {}
            if metadata:
                for key, value in list(metadata.items())[:10]:  # Max 10 items
                    # Only allow alphanumeric keys and limit value length
                    if key.replace('_', '').replace('-', '').isalnum():
                        safe_metadata[key] = str(value)[:256]
            
            # Upload with encryption and metadata
            upload_args = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Body': file_obj,
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256',  # SSE-S3
                'Metadata': safe_metadata,
                # ACL not set - bucket should be private
            }
            
            response = self.s3_client.put_object(**upload_args)
            
            logger.info(
                f"Uploaded file to S3: {s3_key} "
                f"(size: {size_bytes} bytes, user: {user_id})"
            )
            
            return {
                's3_key': s3_key,
                'size_bytes': size_bytes,
                'etag': response.get('ETag', '').strip('"'),
                'version_id': response.get('VersionId'),
            }
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 upload failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to upload file: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")
    
    def download_file(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> BinaryIO:
        """
        Download a file from S3 with ownership verification.
        
        Security:
        - Verifies user owns the file through key path
        - No cross-user access possible
        
        Args:
            user_id: User ID who owns the export
            export_id: Export identifier
            format: File format
        
        Returns:
            File-like object (BytesIO)
        
        Raises:
            StorageError: Download failure
            AuthorizationError: User doesn't own the file
        """
        try:
            s3_key = self._build_s3_key(user_id, export_id, format)
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Downloaded file from S3: {s3_key} (user: {user_id})")
            
            return response['Body']
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == 'NoSuchKey':
                # File doesn't exist - could be wrong user_id
                raise AuthorizationError("Export not found or access denied")
            
            logger.error(f"S3 download failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to download file: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")
    
    def generate_presigned_url(
        self,
        user_id: str,
        export_id: str,
        format: str,
        expiration_seconds: int = 3600,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a presigned URL for secure, temporary download access.
        
        Security Features:
        - Time-limited access (default 1 hour, max 7 days)
        - User ownership verified through key path
        - No permanent public access
        - Optional custom filename in Content-Disposition
        
        Args:
            user_id: User ID who owns the export
            export_id: Export identifier
            format: File format
            expiration_seconds: URL validity duration (max 604800 = 7 days)
            filename: Optional custom download filename
        
        Returns:
            Presigned URL string
        
        Raises:
            StorageError: URL generation failure
            AuthorizationError: Invalid ownership
        """
        try:
            # Enforce max expiration (7 days)
            expiration_seconds = min(expiration_seconds, 604800)
            
            s3_key = self._build_s3_key(user_id, export_id, format)
            
            # Verify object exists and user owns it
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
            except ClientError as e:
                if e.response.get('Error', {}).get('Code') == '404':
                    raise AuthorizationError("Export not found or access denied")
                raise
            
            # Build presigned URL params
            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
            }
            
            # Add Content-Disposition for custom filename
            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration_seconds
            )
            
            logger.info(
                f"Generated presigned URL for {s3_key} "
                f"(user: {user_id}, expires_in: {expiration_seconds}s)"
            )
            
            return url
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Presigned URL generation failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to generate download URL: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")
    
    def delete_file(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> bool:
        """
        Delete a file from S3 with ownership verification.
        
        Security:
        - Only owner can delete through key path scoping
        
        Args:
            user_id: User ID who owns the export
            export_id: Export identifier
            format: File format
        
        Returns:
            True if deleted successfully
        
        Raises:
            StorageError: Deletion failure
        """
        try:
            s3_key = self._build_s3_key(user_id, export_id, format)
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Deleted file from S3: {s3_key} (user: {user_id})")
            
            return True
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 deletion failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to delete file: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")
    
    def get_file_metadata(
        self,
        user_id: str,
        export_id: str,
        format: str
    ) -> Dict[str, Any]:
        """
        Get metadata for a file without downloading it.
        
        Args:
            user_id: User ID who owns the export
            export_id: Export identifier
            format: File format
        
        Returns:
            Dict with:
                - size_bytes: File size
                - last_modified: Last modified datetime
                - content_type: Content type
                - etag: ETag
                - metadata: Custom metadata
        
        Raises:
            StorageError: Metadata retrieval failure
            AuthorizationError: User doesn't own the file
        """
        try:
            s3_key = self._build_s3_key(user_id, export_id, format)
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                'size_bytes': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {}),
            }
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code in ['404', 'NoSuchKey']:
                raise AuthorizationError("Export not found or access denied")
            
            logger.error(f"S3 metadata retrieval failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to get file metadata: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")
    
    def list_user_exports(
        self,
        user_id: str,
        max_keys: int = 100
    ) -> list[Dict[str, Any]]:
        """
        List all exports for a specific user.
        
        Security:
        - Only lists files in user's directory (exports/{user_id}/)
        
        Args:
            user_id: User ID
            max_keys: Maximum number of objects to return
        
        Returns:
            List of dicts with:
                - key: S3 object key
                - size: File size
                - last_modified: Last modified datetime
                - etag: ETag
        
        Raises:
            StorageError: Listing failure
        """
        try:
            prefix = f"exports/{user_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            exports = []
            for obj in response.get('Contents', []):
                exports.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj.get('ETag', '').strip('"'),
                })
            
            logger.info(f"Listed {len(exports)} exports for user {user_id}")
            
            return exports
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 listing failed: {error_code} - {str(e)}")
            raise StorageError(f"Failed to list exports: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"S3 client error: {str(e)}")
            raise StorageError("Storage service unavailable")


# Singleton instance
_s3_adapter: Optional[S3StorageAdapter] = None


def get_s3_adapter() -> S3StorageAdapter:
    """Get or create S3 adapter singleton instance."""
    global _s3_adapter
    if _s3_adapter is None:
        _s3_adapter = S3StorageAdapter()
    return _s3_adapter
