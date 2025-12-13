"""S3 Storage Adapter - Full AWS S3 Implementation with local fallback."""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import logging

# Try to import boto3 for real S3
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("Warning: boto3 not installed. Install with: pip install boto3")


logger = logging.getLogger(__name__)


class S3StorageAdapter:
    """
    Storage adapter supporting both AWS S3 and local file fallback.
    Automatically uses S3 if AWS credentials are configured, otherwise falls back to local storage.
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """Initialize storage adapter.
        
        Args:
            bucket_name: S3 bucket name (defaults to env var S3_BUCKET_NAME)
            region: AWS region (defaults to env var S3_REGION)
            access_key: AWS access key (defaults to env var AWS_ACCESS_KEY_ID)
            secret_key: AWS secret key (defaults to env var AWS_SECRET_ACCESS_KEY)
        """
        # Load from environment if not provided
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME', 'jobwise-exports')
        self.region = region or os.getenv('S3_REGION', 'us-west-2')
        self.access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Determine if we can use S3
        self.use_s3 = False
        self.s3_client = None
        
        if BOTO3_AVAILABLE and self.access_key and self.secret_key:
            try:
                # Initialize S3 client with credentials
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                
                # Test connection by checking if bucket exists or create it
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket_name)
                    logger.info(f"✓ Connected to S3 bucket: {self.bucket_name}")
                    self.use_s3 = True
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == '404':
                        # Bucket doesn't exist, create it
                        logger.info(f"Creating S3 bucket: {self.bucket_name}")
                        if self.region == 'us-east-1':
                            self.s3_client.create_bucket(Bucket=self.bucket_name)
                        else:
                            self.s3_client.create_bucket(
                                Bucket=self.bucket_name,
                                CreateBucketConfiguration={'LocationConstraint': self.region}
                            )
                        logger.info(f"✓ S3 bucket created: {self.bucket_name}")
                        self.use_s3 = True
                    else:
                        logger.error(f"S3 bucket access error: {e}")
                        raise
                        
            except (ClientError, NoCredentialsError) as e:
                logger.warning(f"Failed to initialize S3: {e}")
                logger.warning("Falling back to local file storage")
                self.use_s3 = False
        else:
            if not BOTO3_AVAILABLE:
                logger.warning("boto3 not available. Using local file storage.")
            else:
                logger.warning("AWS credentials not configured. Using local file storage.")
        
        # Setup local storage if S3 not available
        if not self.use_s3:
            self.local_storage_path = Path(__file__).parent.parent.parent.parent / "storage" / "exports"
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local file storage at: {self.local_storage_path}")
    
    def upload_file(
        self,
        file_content: bytes,
        key: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload file to storage (S3 or local).
        
        Args:
            file_content: File content as bytes
            key: Storage key (path)
            content_type: MIME type
        
        Returns:
            Storage key
        """
        if self.use_s3:
            try:
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_content,
                    ContentType=content_type
                )
                logger.info(f"✓ Uploaded {len(file_content)} bytes to S3: s3://{self.bucket_name}/{key}")
                return key
            except ClientError as e:
                logger.error(f"S3 upload failed: {e}")
                raise RuntimeError(f"Failed to upload to S3: {e}")
        else:
            # Save to local filesystem
            file_path = self.local_storage_path / key.replace('/', '_')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"✓ Saved {len(file_content)} bytes to local: {file_path}")
            return key
    
    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate download URL for file.
        
        Args:
            key: Storage key
            expiration: URL validity duration in seconds
        
        Returns:
            Download URL (presigned for S3, local endpoint for local storage)
        """
        if self.use_s3:
            try:
                # Generate presigned URL for S3
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': key
                    },
                    ExpiresIn=expiration
                )
                logger.debug(f"Generated S3 presigned URL for {key} (expires in {expiration}s)")
                return url
            except ClientError as e:
                logger.error(f"Failed to generate presigned URL: {e}")
                raise RuntimeError(f"Failed to generate download URL: {e}")
        else:
            # Return local file path URL
            file_path = self.local_storage_path / key.replace('/', '_')
            
            # Generate a token for security (simple hash-based)
            expires_at = int((datetime.utcnow() + timedelta(seconds=expiration)).timestamp())
            token = hashlib.md5(f"{key}{expires_at}".encode()).hexdigest()[:16]
            
            return f"/api/v1/exports/download/{key.replace('/', '_')}?token={token}&expires={expires_at}"
    
    def delete_file(self, key: str) -> None:
        """
        Delete file from storage.
        
        Args:
            key: Storage key
        """
        if self.use_s3:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info(f"✓ Deleted from S3: s3://{self.bucket_name}/{key}")
            except ClientError as e:
                logger.error(f"S3 delete failed: {e}")
                # Don't raise - deletion is best-effort
        else:
            file_path = self.local_storage_path / key.replace('/', '_')
            if file_path.exists():
                file_path.unlink()
                logger.info(f"✓ Deleted local file: {file_path}")
    
    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            key: Storage key
        
        Returns:
            True if file exists
        """
        if self.use_s3:
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                return True
            except ClientError:
                return False
        else:
            file_path = self.local_storage_path / key.replace('/', '_')
            return file_path.exists()
    
    def get_file_size(self, key: str) -> int:
        """
        Get file size from storage.
        
        Args:
            key: Storage key
        
        Returns:
            File size in bytes
        """
        if self.use_s3:
            try:
                response = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                return response['ContentLength']
            except ClientError:
                return 0
        else:
            file_path = self.local_storage_path / key.replace('/', '_')
            if file_path.exists():
                return file_path.stat().st_size
            return 0
    
    def get_file_content(self, key: str) -> Optional[bytes]:
        """
        Get file content from storage.
        
        Args:
            key: Storage key
        
        Returns:
            File content as bytes or None if not found
        """
        if self.use_s3:
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                return response['Body'].read()
            except ClientError as e:
                logger.error(f"Failed to get file from S3: {e}")
                return None
        else:
            file_path = self.local_storage_path / key.replace('/', '_')
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return f.read()
        return None
        # return response['ContentLength']
        return 0
