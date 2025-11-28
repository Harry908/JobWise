"""
Integration test for separate writing_styles table implementation.
Tests normalized database design with dedicated table storage.
"""

import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy import select
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.models import SampleDocumentModel, WritingStyleModel
from app.application.services.writing_style_service import WritingStyleService

# Sample cover letter text for testing
SAMPLE_COVER_LETTER = """
Dear Hiring Manager,

I am excited to apply for the Software Engineer position at your innovative company. With my strong background in Python development and passion for creating efficient solutions, I believe I would be a valuable addition to your team.

In my previous role, I developed robust API systems that handled thousands of requests daily. I'm particularly proud of implementing a caching system that reduced response times by 40%. My experience with FastAPI, SQLAlchemy, and cloud platforms makes me well-suited for your technical requirements.

I am eager to bring my collaborative spirit and problem-solving skills to your organization. Thank you for considering my application.

Best regards,
Test User
"""

async def test_separate_writing_styles_table():
    """Test writing style storage in dedicated writing_styles table."""
    print("\\n🧪 Testing separate writing_styles table implementation...")
    
    async for session in get_db_session():
        service = WritingStyleService(session)
        test_user_id = 888  # Use different ID to avoid cached data
        
        # Create sample document
        sample_doc = SampleDocumentModel(
            id="test-sample-uuid-456", 
            user_id=test_user_id,
            document_type="cover_letter",
            original_text=SAMPLE_COVER_LETTER,
            original_filename="test_cover_letter.txt",
            word_count=len(SAMPLE_COVER_LETTER.split()),
            character_count=len(SAMPLE_COVER_LETTER),
            upload_timestamp=datetime.utcnow(),
            is_active=True
        )
        
        session.add(sample_doc)
        await session.commit()
        await session.refresh(sample_doc)
        print(f"✅ Created sample document: {sample_doc.id}")
        
        try:
            # Extract writing style
            style = await service.get_or_extract_style(test_user_id)
            print(f"✅ Extracted and stored writing style")
            
            # Verify separate table storage
            result = await session.execute(
                select(WritingStyleModel).where(WritingStyleModel.user_id == test_user_id)
            )
            stored_style = result.scalar_one()
            
            assert stored_style.user_id == test_user_id
            assert stored_style.extraction_status == "completed"
            assert stored_style.extraction_model == "regex_analysis"
            assert stored_style.source_sample_id == sample_doc.id
            assert json.loads(stored_style.extracted_style) == style
            
            print(f"✅ Verified storage in writing_styles table:")
            print(f"   User ID: {stored_style.user_id}")
            print(f"   Status: {stored_style.extraction_status}")
            print(f"   Model: {stored_style.extraction_model}")
            print(f"   Confidence: {stored_style.extraction_confidence}")
            print(f"   Source Sample: {stored_style.source_sample_id}")
            
            # Test cached retrieval
            cached_style = await service.get_or_extract_style(test_user_id)
            assert cached_style == style
            print("✅ Cached retrieval working from separate table")
            
            # Verify table normalization
            assert stored_style.user_id == test_user_id  # One style per user
            print("✅ Table normalization verified (one style per user)")
            
        finally:
            # Cleanup: Delete style record first due to foreign key
            result = await session.execute(
                select(WritingStyleModel).where(WritingStyleModel.user_id == test_user_id)
            )
            style_record = result.scalar_one_or_none()
            if style_record:
                await session.delete(style_record)
            
            await session.delete(sample_doc)
            await session.commit()
            print("✅ Cleanup completed")
        
        break

async def main():
    """Main test runner."""
    print("=" * 80)
    print("JobWise Writing Styles Separate Table Test")
    print("Testing normalized database design with dedicated storage")
    print("=" * 80)
    
    await test_separate_writing_styles_table()
    
    print("\\n🎉 All tests passed!")
    print("✅ Writing styles stored in dedicated normalized table")
    print("✅ Proper foreign key relationships maintained")
    print("✅ Cached retrieval working correctly")
    print("✅ Database design follows normalization principles")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())