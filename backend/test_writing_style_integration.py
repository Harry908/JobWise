"""
Integration test to verify writing style separate table storage implementation.
Tests that writing style extraction is stored in dedicated writing_styles table.
"""

import pytest
import json
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.database.models import SampleDocumentModel, WritingStyleModel
from app.application.services.writing_style_service import WritingStyleService
from sqlalchemy.ext.asyncio import AsyncSession

# Sample cover letter text for testing
SAMPLE_COVER_LETTER = """
Dear Hiring Manager,

I am excited to apply for the Software Engineer position at your innovative company. With my strong background in Python development and passion for creating efficient solutions, I believe I would be a valuable addition to your team.

In my previous role, I developed robust API systems that handled thousands of requests daily. I'm particularly proud of implementing a caching system that reduced response times by 40%. My experience with FastAPI, SQLAlchemy, and cloud platforms makes me well-suited for your technical requirements.

I am eager to bring my collaborative spirit and problem-solving skills to your organization. Thank you for considering my application.

Best regards,
Test User
"""

@pytest.fixture
async def db_session():
    """Create async database session for testing."""
    engine = create_engine()
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        yield session
    await engine.dispose()

@pytest.fixture
async def writing_style_service(db_session):
    """Create writing style service instance."""
    return WritingStyleService(db_session)

@pytest.mark.asyncio
async def test_writing_style_database_storage(db_session, writing_style_service):
    """Test that writing style is extracted and stored in separate writing_styles table."""
    print("\\n🧪 Testing writing style separate table storage...")
    
    # Test user ID
    test_user_id = 999
    
    # Create a sample document first
    sample_doc = SampleDocumentModel(
        id="test-sample-uuid-123",
        user_id=test_user_id,
        document_type="cover_letter",
        original_text=SAMPLE_COVER_LETTER,
        original_filename="test_cover_letter.txt",
        word_count=len(SAMPLE_COVER_LETTER.split()),
        character_count=len(SAMPLE_COVER_LETTER),
        line_count=SAMPLE_COVER_LETTER.count('\\n') + 1,
        upload_timestamp=datetime.utcnow(),
        is_active=True
    )
    
    db_session.add(sample_doc)
    await db_session.commit()
    await db_session.refresh(sample_doc)
    
    print(f"✅ Created sample document: {sample_doc.id}")
    
    # Test writing style extraction and storage
    try:
        writing_style = await writing_style_service.get_or_extract_style(test_user_id)
        print(f"✅ Extracted writing style: {json.dumps(writing_style, indent=2)}")
        
        # Verify style was stored in separate writing_styles table
        result = await db_session.execute(
            select(WritingStyleModel).where(WritingStyleModel.user_id == test_user_id)
        )
        stored_style = result.scalar_one()
        
        assert stored_style.extracted_style is not None
        assert stored_style.extraction_status == "completed"
        assert stored_style.extraction_model == "regex_analysis"
        assert stored_style.source_sample_id == sample_doc.id
        
        print(f"✅ Writing style stored in separate table:")
        print(f"   ID: {stored_style.id}")
        print(f"   User ID: {stored_style.user_id}")
        print(f"   Status: {stored_style.extraction_status}")
        print(f"   Model: {stored_style.extraction_model}")
        print(f"   Confidence: {stored_style.extraction_confidence}")
        print(f"   Source Sample: {stored_style.source_sample_id}")
        
        # Test cached retrieval (should not re-extract)
        cached_style = await writing_style_service.get_or_extract_style(test_user_id)
        assert cached_style == writing_style
        print("✅ Cached retrieval working correctly")
        
        # Verify style structure
        assert "writing_style" in writing_style
        assert "language_patterns" in writing_style
        assert "content_approach" in writing_style
        
        # Check nested structure
        assert "tone" in writing_style["writing_style"]
        assert "formality_level" in writing_style["writing_style"]
        
        print("✅ Writing style has expected structure")
        
    finally:
        # Cleanup - Delete writing style first (foreign key constraint)
        result = await db_session.execute(
            select(WritingStyleModel).where(WritingStyleModel.user_id == test_user_id)
        )
        style_record = result.scalar_one_or_none()
        if style_record:
            await db_session.delete(style_record)
        
        await db_session.delete(sample_doc)
        await db_session.commit()
        print("✅ Test cleanup completed")
    """Test that writing style is extracted and stored in database."""
    print("\n🧪 Testing writing style database storage...")
    
    # Test user ID
    test_user_id = 999
    
    # Create a sample document first
    sample_doc = SampleDocumentModel(
        id="test-sample-uuid-123",
        user_id=test_user_id,
        document_type="cover_letter",
        original_text=SAMPLE_COVER_LETTER,
        original_filename="test_cover_letter.txt",
        word_count=len(SAMPLE_COVER_LETTER.split()),
        character_count=len(SAMPLE_COVER_LETTER),
        line_count=SAMPLE_COVER_LETTER.count('\n') + 1,
        upload_timestamp=datetime.utcnow(),
        is_active=True
    )
    
    db_session.add(sample_doc)
    await db_session.commit()
    await db_session.refresh(sample_doc)
    
    print(f"✅ Created sample document: {sample_doc.id}")
    
    # Test writing style extraction and storage
    try:
        writing_style = await writing_style_service.get_or_extract_style(test_user_id)
        print(f"✅ Extracted writing style: {json.dumps(writing_style, indent=2)}")
        
        # Verify style was stored in database
        result = await db_session.execute(
            select(SampleDocumentModel).where(
                SampleDocumentModel.user_id == test_user_id,
                SampleDocumentModel.document_type == "cover_letter",
                SampleDocumentModel.is_active == True
            )
        )
        stored_sample = result.scalar_one()
        
        assert stored_sample.extracted_writing_style is not None
        assert stored_sample.style_extraction_status == "completed"
        assert stored_sample.style_extraction_model is not None
        
        print(f"✅ Writing style stored in database:")
        print(f"   Status: {stored_sample.style_extraction_status}")
        print(f"   Model: {stored_sample.style_extraction_model}")
        print(f"   Confidence: {stored_sample.style_extraction_confidence}")
        
        # Test cached retrieval (should not re-extract)
        cached_style = await writing_style_service.get_or_extract_style(test_user_id)
        assert cached_style == writing_style
        print("✅ Cached retrieval working correctly")
        
        # Verify style structure - check the actual returned structure
        assert "writing_style" in writing_style
        assert "language_patterns" in writing_style
        assert "content_approach" in writing_style
        
        # Check nested structure
        assert "tone" in writing_style["writing_style"]
        assert "formality_level" in writing_style["writing_style"]
        
        print("✅ Writing style has expected structure")
        
    finally:
        # Cleanup
        await db_session.delete(sample_doc)
        await db_session.commit()
        print("✅ Test cleanup completed")

if __name__ == "__main__":
    """Run test directly for quick verification."""
    from datetime import datetime
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        print("=" * 80)
        print("JobWise Writing Style Database Integration Test")
        print("=" * 80)
        
        from app.infrastructure.database.connection import get_db_session
        
        async for session in get_db_session():
            service = WritingStyleService(session)
            await test_writing_style_database_storage(session, service)
            break
    
    asyncio.run(main())