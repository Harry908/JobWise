"""Storage service for managing file storage operations."""

import os
import shutil
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """Service for managing file storage and cleanup operations."""
    
    def __init__(self, base_directory: Optional[str] = None):
        """
        Initialize storage service.
        
        Args:
            base_directory: Base directory for file storage
        """
        self.base_directory = Path(base_directory or settings.upload_directory or "./uploads")
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Storage subdirectories
        self.cover_letters_dir = self.base_directory / "cover_letters"
        self.example_resumes_dir = self.base_directory / "example_resumes"
        self.temp_dir = self.base_directory / "temp"
        self.archives_dir = self.base_directory / "archives"
        
        # Ensure directories exist
        for directory in [self.cover_letters_dir, self.example_resumes_dir, self.temp_dir, self.archives_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def move_to_archive(self, file_path: str, reason: str = "archived") -> str:
        """
        Move a file to archive directory.
        
        Args:
            file_path: Path to file to archive
            reason: Reason for archiving
            
        Returns:
            New archived file path
            
        Raises:
            StorageException: Move operation failed
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise StorageException(f"File not found: {file_path}")
            
            # Create archive subdirectory by date
            archive_date = datetime.now().strftime("%Y-%m-%d")
            archive_subdir = self.archives_dir / archive_date
            archive_subdir.mkdir(exist_ok=True)
            
            # Generate archived filename
            timestamp = datetime.now().strftime("%H%M%S")
            archived_filename = f"{timestamp}_{source_path.name}"
            archive_path = archive_subdir / archived_filename
            
            # Move file
            shutil.move(str(source_path), str(archive_path))
            
            # Create metadata file
            metadata_file = archive_path.with_suffix(archive_path.suffix + ".meta")
            with open(metadata_file, "w") as f:
                f.write(f"original_path: {file_path}\n")
                f.write(f"archived_at: {datetime.now().isoformat()}\n")
                f.write(f"reason: {reason}\n")
            
            logger.info(f"File archived: {file_path} -> {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Failed to archive file: {file_path}, error={e}")
            raise StorageException(f"Archive operation failed: {str(e)}")

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for temp files
            
        Returns:
            Number of files cleaned up
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned temp file: {file_path}")
            
            logger.info(f"Cleaned {cleaned_count} temporary files older than {max_age_hours} hours")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
            return 0

    async def cleanup_orphaned_files(self, active_file_paths: List[str]) -> int:
        """
        Clean up files that are no longer referenced in the database.
        
        Args:
            active_file_paths: List of file paths that should be kept
            
        Returns:
            Number of orphaned files cleaned up
        """
        try:
            active_paths_set = set(Path(p).resolve() for p in active_file_paths)
            cleaned_count = 0
            
            # Check each storage directory
            for storage_dir in [self.cover_letters_dir, self.example_resumes_dir]:
                for file_path in storage_dir.glob("*"):
                    if file_path.is_file():
                        if file_path.resolve() not in active_paths_set:
                            # Move to archive instead of deleting
                            await self.move_to_archive(str(file_path), "orphaned")
                            cleaned_count += 1
                            logger.debug(f"Archived orphaned file: {file_path}")
            
            logger.info(f"Cleaned {cleaned_count} orphaned files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Orphaned file cleanup failed: {e}")
            return 0

    def get_storage_usage(self) -> Dict[str, Any]:
        """
        Get comprehensive storage usage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            stats = {}
            
            # Get stats for each directory
            directories = {
                "cover_letters": self.cover_letters_dir,
                "example_resumes": self.example_resumes_dir,
                "temp": self.temp_dir,
                "archives": self.archives_dir,
                "total": self.base_directory
            }
            
            for name, directory in directories.items():
                if directory.exists():
                    dir_stats = self._get_directory_stats(directory, recursive=(name == "total"))
                    stats[name] = dir_stats
                else:
                    stats[name] = {"file_count": 0, "total_size": 0, "directory": str(directory)}
            
            # Calculate usage percentages if max storage is defined
            if hasattr(settings, 'max_storage_bytes') and settings.max_storage_bytes:
                usage_percentage = (stats["total"]["total_size"] / settings.max_storage_bytes) * 100
                stats["usage_percentage"] = min(100, usage_percentage)
                stats["available_bytes"] = max(0, settings.max_storage_bytes - stats["total"]["total_size"])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage usage: {e}")
            return {"error": str(e)}

    def check_storage_health(self) -> Dict[str, Any]:
        """
        Check storage system health and identify potential issues.
        
        Returns:
            Health check results
        """
        try:
            health = {
                "status": "healthy",
                "issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check directory permissions
            for directory in [self.base_directory, self.cover_letters_dir, self.example_resumes_dir]:
                if not directory.exists():
                    health["issues"].append(f"Directory does not exist: {directory}")
                    health["status"] = "unhealthy"
                elif not os.access(directory, os.W_OK):
                    health["issues"].append(f"Directory not writable: {directory}")
                    health["status"] = "unhealthy"
            
            # Check available disk space
            try:
                disk_usage = shutil.disk_usage(self.base_directory)
                available_gb = disk_usage.free / (1024**3)
                
                if available_gb < 1:  # Less than 1GB available
                    health["issues"].append(f"Low disk space: {available_gb:.1f}GB available")
                    health["status"] = "unhealthy"
                elif available_gb < 5:  # Less than 5GB available
                    health["warnings"].append(f"Disk space getting low: {available_gb:.1f}GB available")
                    if health["status"] == "healthy":
                        health["status"] = "warning"
            except Exception:
                health["warnings"].append("Could not check disk space")
            
            # Check for excessive temp files
            temp_file_count = len(list(self.temp_dir.glob("*")))
            if temp_file_count > 100:
                health["warnings"].append(f"Many temp files: {temp_file_count}")
                health["recommendations"].append("Run temp file cleanup")
                if health["status"] == "healthy":
                    health["status"] = "warning"
            
            # Check storage usage
            usage_stats = self.get_storage_usage()
            if "usage_percentage" in usage_stats and usage_stats["usage_percentage"] > 90:
                health["issues"].append(f"Storage usage high: {usage_stats['usage_percentage']:.1f}%")
                health["status"] = "unhealthy"
            elif "usage_percentage" in usage_stats and usage_stats["usage_percentage"] > 75:
                health["warnings"].append(f"Storage usage: {usage_stats['usage_percentage']:.1f}%")
                health["recommendations"].append("Consider cleanup of old files")
                if health["status"] == "healthy":
                    health["status"] = "warning"
            
            return health
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "issues": ["Health check failed"],
                "warnings": [],
                "recommendations": ["Check storage service configuration"]
            }

    def _get_directory_stats(self, directory: Path, recursive: bool = False) -> Dict[str, Any]:
        """
        Get statistics for a directory.
        
        Args:
            directory: Directory to analyze
            recursive: Whether to include subdirectories
            
        Returns:
            Directory statistics
        """
        if not directory.exists():
            return {
                "file_count": 0,
                "total_size": 0,
                "directory": str(directory),
                "last_modified": None
            }
        
        try:
            total_size = 0
            file_count = 0
            last_modified = None
            
            pattern = "**/*" if recursive else "*"
            
            for item in directory.glob(pattern):
                if item.is_file():
                    file_count += 1
                    size = item.stat().st_size
                    total_size += size
                    
                    # Track most recent modification
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if last_modified is None or mtime > last_modified:
                        last_modified = mtime
            
            return {
                "file_count": file_count,
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "directory": str(directory),
                "last_modified": last_modified.isoformat() if last_modified else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for directory {directory}: {e}")
            return {
                "file_count": 0,
                "total_size": 0,
                "directory": str(directory),
                "error": str(e)
            }