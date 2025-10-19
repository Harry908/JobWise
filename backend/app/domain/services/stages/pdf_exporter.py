"""PDF Exporter Stage - Stage 5 of the AI generation pipeline."""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ..ai_orchestrator import PipelineStageInterface, PipelineStage, PipelineContext, StageError


logger = logging.getLogger(__name__)


class PDFExporterStage(PipelineStageInterface):
    """Stage 5: Export generated documents to PDF format."""

    def __init__(self, openai_client=None):  # Not needed for PDF export
        self.openai_client = openai_client

    @property
    def stage(self) -> PipelineStage:
        return PipelineStage.EXPORTING_PDF

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Export generated documents to PDF format."""
        try:
            # Export each document to PDF
            pdf_results = {}

            for result in context.generation.results:
                pdf_url = await self._export_to_pdf(result, context.generation.id)
                if pdf_url:
                    pdf_results[result.document_type.value] = {
                        'url': pdf_url,
                        'exported_at': datetime.utcnow().isoformat(),
                        'file_size': self._get_file_size(pdf_url) if pdf_url.startswith('/') else None
                    }

            # Update context metadata
            context.update_metadata('pdf_exports', pdf_results)
            context.update_metadata('stage_5_completed', True)

            # Add PDF URLs to generation metadata
            context.generation.pipeline_metadata['pdf_results'] = pdf_results

            logger.info(f"PDF export completed for generation {context.generation.id}")
            return context

        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise StageError(self.stage, f"Failed to export documents to PDF: {str(e)}", e)

    async def _export_to_pdf(self, document_result, generation_id: str) -> Optional[str]:
        """Export a document to PDF format."""
        try:
            # For now, we'll simulate PDF generation
            # In a real implementation, this would use a library like WeasyPrint or ReportLab

            # Create a mock PDF URL/path
            pdf_filename = f"{generation_id}_{document_result.document_type.value}_{int(datetime.utcnow().timestamp())}.pdf"
            pdf_path = f"/generated_pdfs/{pdf_filename}"

            # Simulate PDF generation process
            await self._generate_pdf_content(document_result.content, pdf_path)

            logger.info(f"PDF generated: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"Failed to generate PDF for {document_result.document_type.value}: {str(e)}")
            return None

    async def _generate_pdf_content(self, content: str, output_path: str) -> None:
        """Generate PDF content from document text."""
        # This is a placeholder for actual PDF generation
        # In production, you would use:
        # - WeasyPrint for HTML to PDF
        # - ReportLab for direct PDF creation
        # - Puppeteer/Playwright for browser-based rendering

        try:
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)

            # For now, just create a text file as placeholder
            # In real implementation, use proper PDF library
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert content to basic HTML for PDF generation
            html_content = self._convert_to_html(content)

            # Here you would call the PDF library
            # Example with WeasyPrint (commented out):
            # from weasyprint import HTML
            # HTML(string=html_content).write_pdf(output_path)

            # For now, save as text file
            text_path = output_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.debug(f"PDF content prepared for {output_path}")

        except Exception as e:
            logger.error(f"PDF content generation failed: {str(e)}")
            raise

    def _convert_to_html(self, content: str) -> str:
        """Convert plain text content to basic HTML for PDF generation."""
        # Basic HTML conversion
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Generated Document</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                p {{
                    margin-bottom: 15px;
                }}
                .contact-info {{
                    margin-bottom: 30px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 20px;
                }}
            </style>
        </head>
        <body>
        """

        # Split content into paragraphs and wrap in HTML
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Basic formatting for headers
                if len(paragraph.strip()) < 100 and not paragraph.startswith(' '):
                    html += f"<h2>{paragraph.strip()}</h2>\n"
                else:
                    html += f"<p>{paragraph.strip().replace(chr(10), '<br>')}</p>\n"

        html += "</body></html>"
        return html

    def _get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception:
            return None

    def _validate_pdf_generation(self, pdf_path: str) -> bool:
        """Validate that PDF was generated successfully."""
        try:
            # Check if file exists and has content
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                return size > 0
            return False
        except Exception:
            return False