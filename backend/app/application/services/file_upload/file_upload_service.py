"""File upload service for handling cover letters and example resumes."""

import os
import uuid
import hashlib
from typing import Optional, Dict, Any, BinaryIO, Union
from pathlib import Path
import logging

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.preferences.example_resume import ExampleResume, FileMetadata
from app.infrastructure.repositories.example_resume_repository import ExampleResumeRepository
from app.core.exceptions import ValidationException, StorageException
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FileUploadService:
    """Service for secure file upload and storage management."""
    
    # Allowed file types and extensions
    ALLOWED_MIME_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
        "application/msword": "doc"
    }
    
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "doc"}
    
    # File size limits (in bytes) - now from settings
    MAX_FILE_SIZE = settings.upload_max_file_size  
    MIN_FILE_SIZE = 100  # 100 bytes minimum
    
    def __init__(self, db: AsyncSession, upload_directory: Optional[str] = None):
        """
        Initialize file upload service.
        
        Args:
            db: Database session
            upload_directory: Directory for storing uploaded files
        """
        self.db = db
        self.repository = ExampleResumeRepository(db)
        
        # Set upload directory
        self.upload_directory = Path(upload_directory or settings.upload_storage_path or "./uploads")
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.cover_letters_dir = self.upload_directory / "cover_letters"
        self.example_resumes_dir = self.upload_directory / "example_resumes" 
        self.temp_dir = self.upload_directory / "temp"
        
        for directory in [self.cover_letters_dir, self.example_resumes_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def upload_cover_letter(
        self,
        user_id: int,
        file: UploadFile,
        source: str = "web"
    ) -> Dict[str, Any]:
        """
        Upload and store a cover letter for writing style extraction.
        
        Args:
            user_id: User ID
            file: Uploaded file
            source: Upload source (web, mobile, api)
            
        Returns:
            Dict with file metadata and storage information
            
        Raises:
            ValidationException: Invalid file
            StorageException: Storage error
        """
        # Validate file
        await self._validate_file(file)
        
        # Read file content
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Generate unique filename and storage path
        file_id = str(uuid.uuid4())
        file_extension = self._get_file_extension(file.filename, file.content_type)
        storage_filename = f"{user_id}_{file_id}.{file_extension}"
        storage_path = self.cover_letters_dir / storage_filename
        
        try:
            # Save file to disk
            with open(storage_path, "wb") as f:
                f.write(file_content)
            
            # Create file metadata
            content_hash = hashlib.sha256(file_content).hexdigest()
            file_metadata = {
                "file_id": file_id,
                "original_filename": file.filename,
                "storage_filename": storage_filename,
                "storage_path": str(storage_path),
                "file_size": len(file_content),
                "content_type": file.content_type,
                "content_hash": content_hash,
                "upload_source": source
            }
            
            logger.info(f"Cover letter uploaded: user_id={user_id}, file_id={file_id}, size={len(file_content)}")
            return file_metadata
            
        except Exception as e:
            # Clean up file if it was created
            if storage_path.exists():
                storage_path.unlink()
            
            logger.error(f"Failed to upload cover letter: user_id={user_id}, error={e}")
            raise StorageException(f"Failed to save file: {str(e)}")

    async def upload_example_resume(
        self,
        user_id: int,
        file: UploadFile,
        source: str = "web",
        is_primary: bool = False
    ) -> ExampleResume:
        """
        Upload and store an example resume for structural analysis.
        
        Args:
            user_id: User ID
            file: Uploaded file
            source: Upload source (web, mobile, api)
            is_primary: Whether this is the user's primary example
            
        Returns:
            ExampleResume entity
            
        Raises:
            ValidationException: Invalid file
            StorageException: Storage error
        """
        # Validate file
        await self._validate_file(file)
        
        # Read file content
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Generate unique filename and storage path
        file_id = str(uuid.uuid4())
        file_extension = self._get_file_extension(file.filename, file.content_type)
        storage_filename = f"{user_id}_{file_id}.{file_extension}"
        storage_path = self.example_resumes_dir / storage_filename
        
        try:
            # Save file to disk
            with open(storage_path, "wb") as f:
                f.write(file_content)
            
            # Create ExampleResume entity
            example_resume = ExampleResume.create_from_upload(
                user_id=user_id,
                file_name=file.filename,
                file_content=file_content,
                file_type=file.content_type,
                storage_path=str(storage_path),
                upload_source=source
            )
            
            if is_primary:
                example_resume.mark_as_primary()
            
            # Save to database
            created_resume = await self.repository.create(example_resume)
            
            logger.info(f"Example resume uploaded: user_id={user_id}, resume_id={created_resume.id}, size={len(file_content)}")
            return created_resume
            
        except Exception as e:
            # Clean up file if it was created
            if storage_path.exists():
                storage_path.unlink()
            
            logger.error(f"Failed to upload example resume: user_id={user_id}, error={e}")
            raise StorageException(f"Failed to save file: {str(e)}")

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted, False if file didn't exist
        """
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_path_obj.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: path={file_path}, error={e}")
            raise StorageException(f"Failed to delete file: {str(e)}")

    async def get_file_content(self, file_path: str) -> bytes:
        """
        Read file content from storage.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as bytes
            
        Raises:
            StorageException: File not found or read error
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise StorageException(f"File not found: {file_path}")
            
            with open(file_path_obj, "rb") as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to read file: path={file_path}, error={e}")
            raise StorageException(f"Failed to read file: {str(e)}")

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            stats = {
                "cover_letters": self._get_directory_stats(self.cover_letters_dir),
                "example_resumes": self._get_directory_stats(self.example_resumes_dir),
                "temp": self._get_directory_stats(self.temp_dir),
            }
            
            stats["total_files"] = sum(s["file_count"] for s in stats.values())
            stats["total_size"] = sum(s["total_size"] for s in stats.values())
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}

    async def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: FastAPI UploadFile
            
        Raises:
            ValidationException: Invalid file
        """
        # Check file size
        file_size = 0
        temp_content = await file.read()
        file_size = len(temp_content)
        await file.seek(0)  # Reset file pointer
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValidationException(
                error_code="file_too_large",
                message=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / 1024 / 1024:.1f}MB",
                details={
                    "file_size": file_size,
                    "max_size": self.MAX_FILE_SIZE,
                    "filename": file.filename
                }
            )
        
        if file_size < self.MIN_FILE_SIZE:
            raise ValidationException(
                error_code="file_too_small", 
                message=f"File size is below minimum required size of {self.MIN_FILE_SIZE} bytes",
                details={
                    "file_size": file_size,
                    "min_size": self.MIN_FILE_SIZE,
                    "filename": file.filename
                }
            )
        
        # Check file type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationException(
                error_code="invalid_file_type",
                message=f"File type {file.content_type} is not supported",
                details={
                    "content_type": file.content_type,
                    "allowed_types": list(self.ALLOWED_MIME_TYPES.keys()),
                    "filename": file.filename
                }
            )
        
        # Check file extension
        if file.filename:
            extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if extension not in self.ALLOWED_EXTENSIONS:
                raise ValidationException(
                    error_code="invalid_file_extension",
                    message=f"File extension .{extension} is not supported",
                    details={
                        "extension": extension,
                        "allowed_extensions": list(self.ALLOWED_EXTENSIONS),
                        "filename": file.filename
                    }
                )

    def _get_file_extension(self, filename: Optional[str], content_type: str) -> str:
        """Get file extension from filename or content type."""
        if filename and '.' in filename:
            return filename.split('.')[-1].lower()
        return self.ALLOWED_MIME_TYPES.get(content_type, "bin")

    def _get_directory_stats(self, directory: Path) -> Dict[str, Any]:
        """Get statistics for a directory."""
        if not directory.exists():
            return {"file_count": 0, "total_size": 0}
        
        files = list(directory.glob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "file_count": len([f for f in files if f.is_file()]),
            "total_size": total_size,
            "directory": str(directory)
        }