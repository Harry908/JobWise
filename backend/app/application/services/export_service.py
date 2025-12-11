"""
Export Service
Orchestrates document export process: rendering + S3 upload + presigned URLs.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import uuid

from app.domain.entities.export import Export
from app.domain.entities.generation import Generation
from app.domain.enums.export_format import ExportFormat
from app.domain.enums.template_type import TemplateType
from app.application.services.export_renderer import ExportRenderer
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.export_repository import ExportRepository


class ExportService:
    """Service for handling document exports."""
    
    def __init__(
        self,
        export_renderer: ExportRenderer,
        s3_adapter: S3StorageAdapter,
        generation_repository: GenerationRepository,
        export_repository: ExportRepository
    ):
        """Initialize export service with dependencies."""
        self.renderer = export_renderer
        self.s3_adapter = s3_adapter
        self.generation_repo = generation_repository
        self.export_repo = export_repository
    
    async def export_to_pdf(
        self,
        user_id: str,
        generation_id: str,
        template: TemplateType,
        options: Optional[Dict[str, Any]] = None
    ) -> Export:
        """
        Export a generation to PDF.
        
        Args:
            user_id: User ID (for authorization)
            generation_id: Generation ID to export
            template: Template type to use
            options: Template customization options
        
        Returns:
            Export entity with download URL
        
        Raises:
            ValueError: If generation not found or has no structured content
        """
        # Fetch generation
        generation = await self.generation_repo.get_by_id(generation_id, user_id)
        if not generation:
            raise ValueError(f"Generation {generation_id} not found")
        
        if not generation.content_structured:
            raise ValueError(f"Generation {generation_id} has no structured content")
        
        # Render PDF
        pdf_bytes = self.renderer.render_pdf(
            structured_content=generation.content_structured,
            template=template,
            options=options
        )
        
        # Create export entity
        export_id = str(uuid.uuid4())
        filename = self._generate_filename(generation, ExportFormat.PDF)
        s3_key = Export.generate_s3_key(user_id, export_id, ExportFormat.PDF)
        
        # Upload to S3
        self.s3_adapter.upload_file(
            file_content=pdf_bytes,
            key=s3_key,
            content_type='application/pdf'
        )
        
        # Get file size and estimate page count
        file_size = len(pdf_bytes)
        page_count = self._estimate_page_count(pdf_bytes, ExportFormat.PDF)
        
        # Generate presigned URL (1 hour expiry)
        download_url = self.s3_adapter.generate_presigned_url(
            key=s3_key,
            expiration=3600  # 1 hour
        )
        
        # Create export record
        export = Export(
            id=export_id,
            user_id=user_id,
            generation_id=generation_id,
            format=ExportFormat.PDF,
            template=template,
            filename=filename,
            file_path=s3_key,
            file_size_bytes=file_size,
            page_count=page_count,
            options=options or {},
            metadata={
                'generation_type': generation.generation_type.value,
                'created_from': generation.id
            },
            download_url=download_url,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        # Save to database
        await self.export_repo.create(export)
        
        return export
    
    async def export_to_docx(
        self,
        user_id: str,
        generation_id: str,
        template: TemplateType,
        options: Optional[Dict[str, Any]] = None
    ) -> Export:
        """
        Export a generation to DOCX.
        
        Args:
            user_id: User ID (for authorization)
            generation_id: Generation ID to export
            template: Template type to use
            options: Template customization options
        
        Returns:
            Export entity with download URL
        """
        # Fetch generation
        generation = await self.generation_repo.get_by_id(generation_id, user_id)
        if not generation:
            raise ValueError(f"Generation {generation_id} not found")
        
        if not generation.content_structured:
            raise ValueError(f"Generation {generation_id} has no structured content")
        
        # Render DOCX
        docx_bytes = self.renderer.render_docx(
            structured_content=generation.content_structured,
            template=template,
            options=options
        )
        
        # Create export entity
        export_id = str(uuid.uuid4())
        filename = self._generate_filename(generation, ExportFormat.DOCX)
        s3_key = Export.generate_s3_key(user_id, export_id, ExportFormat.DOCX)
        
        # Upload to S3
        self.s3_adapter.upload_file(
            file_content=docx_bytes,
            key=s3_key,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Get file size
        file_size = len(docx_bytes)
        
        # Generate presigned URL (1 hour expiry)
        download_url = self.s3_adapter.generate_presigned_url(
            key=s3_key,
            expiration=3600
        )
        
        # Create export record
        export = Export(
            id=export_id,
            user_id=user_id,
            generation_id=generation_id,
            format=ExportFormat.DOCX,
            template=template,
            filename=filename,
            file_path=s3_key,
            file_size_bytes=file_size,
            page_count=None,  # DOCX doesn't have fixed pages
            options=options or {},
            metadata={
                'generation_type': generation.generation_type.value,
                'created_from': generation.id
            },
            download_url=download_url,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        # Save to database
        await self.export_repo.create(export)
        
        return export
    
    async def batch_export(
        self,
        user_id: str,
        generation_ids: List[str],
        format: ExportFormat,
        template: TemplateType,
        options: Optional[Dict[str, Any]] = None
    ) -> Export:
        """
        Create a batch export (ZIP) of multiple generations.
        
        Args:
            user_id: User ID
            generation_ids: List of generation IDs to export
            format: Format for individual files (PDF or DOCX)
            template: Template type to use
            options: Template customization options
        
        Returns:
            Export entity with ZIP file and download URL
        """
        if format not in [ExportFormat.PDF, ExportFormat.DOCX]:
            raise ValueError("Batch export only supports PDF and DOCX formats")
        
        # Render all generations
        exports = []
        for gen_id in generation_ids:
            generation = await self.generation_repo.get_by_id(gen_id, user_id)
            if not generation or not generation.content_structured:
                continue
            
            # Render based on format
            if format == ExportFormat.PDF:
                content = self.renderer.render_pdf(
                    structured_content=generation.content_structured,
                    template=template,
                    options=options
                )
            else:  # DOCX
                content = self.renderer.render_docx(
                    structured_content=generation.content_structured,
                    template=template,
                    options=options
                )
            
            filename = self._generate_filename(generation, format)
            exports.append({
                'filename': filename,
                'content': content
            })
        
        if not exports:
            raise ValueError("No valid generations found for export")
        
        # Create ZIP file
        zip_bytes = self.renderer.create_batch_export(exports)
        
        # Create export entity
        export_id = str(uuid.uuid4())
        filename = f"batch_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
        s3_key = Export.generate_s3_key(user_id, export_id, ExportFormat.ZIP)
        
        # Upload to S3
        self.s3_adapter.upload_file(
            file_content=zip_bytes,
            key=s3_key,
            content_type='application/zip'
        )
        
        # Generate presigned URL
        download_url = self.s3_adapter.generate_presigned_url(
            key=s3_key,
            expiration=3600
        )
        
        # Create export record
        export = Export(
            id=export_id,
            user_id=user_id,
            generation_id=None,  # Batch export
            format=ExportFormat.ZIP,
            template=template,
            filename=filename,
            file_path=s3_key,
            file_size_bytes=len(zip_bytes),
            page_count=None,
            options=options or {},
            metadata={
                'generation_ids': generation_ids,
                'file_count': len(exports),
                'individual_format': format.value
            },
            download_url=download_url,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        # Save to database
        await self.export_repo.create(export)
        
        return export
    
    async def get_export(self, export_id: str, user_id: str) -> Optional[Export]:
        """Get export by ID with fresh download URL."""
        export = await self.export_repo.get_by_id(export_id, user_id)
        
        if not export:
            return None
        
        # Check if expired
        if export.is_expired():
            return None
        
        # Regenerate presigned URL (fresh 1-hour expiry)
        export.download_url = self.s3_adapter.generate_presigned_url(
            key=export.file_path,
            expiration=3600
        )
        
        return export
    
    async def list_exports(
        self,
        user_id: str,
        format: Optional[ExportFormat] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Export]:
        """List user's exports with pagination."""
        exports = await self.export_repo.list_by_user(
            user_id=user_id,
            format=format,
            limit=limit,
            offset=offset
        )
        
        # Regenerate download URLs for non-expired exports
        valid_exports = []
        for export in exports:
            if not export.is_expired():
                export.download_url = self.s3_adapter.generate_presigned_url(
                    key=export.file_path,
                    expiration=3600
                )
                valid_exports.append(export)
        
        return valid_exports
    
    async def delete_export(self, export_id: str, user_id: str) -> bool:
        """Delete an export (removes from S3 and database)."""
        export = await self.export_repo.get_by_id(export_id, user_id)
        
        if not export:
            return False
        
        # Delete from S3
        self.s3_adapter.delete_file(export.file_path)
        
        # Delete from database
        await self.export_repo.delete(export_id, user_id)
        
        return True
    
    async def cleanup_expired_exports(self) -> int:
        """Clean up expired exports (background job)."""
        return await self.export_repo.cleanup_expired()
    
    def _generate_filename(self, generation: Generation, format: ExportFormat) -> str:
        """Generate filename for export."""
        # Extract name from generation (if available in metadata)
        name = "document"
        
        # Use generation type
        gen_type = generation.generation_type.value
        
        # Format: {type}_{timestamp}.{ext}
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        extension = format.value
        
        return f"{gen_type}_{timestamp}.{extension}"
    
    def _estimate_page_count(self, pdf_bytes: bytes, format: ExportFormat) -> Optional[int]:
        """Estimate page count for PDF files."""
        if format != ExportFormat.PDF:
            return None
        
        # Simple estimation: count "/Type /Page" occurrences
        try:
            count = pdf_bytes.count(b'/Type /Page')
            return count if count > 0 else 1
        except:
            return None
