"""Manual test script to upload real sample documents."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.models import SampleDocumentModel
from sqlalchemy import select, update
import uuid


async def test_upload_real_samples():
    """Upload Huy Ky's resume and cover letter samples."""
    
    # File paths
    resume_path = Path(__file__).parent.parent / "docs" / "sample artifacts" / "Huy_Ky_Enhanced_Resume.txt"
    cover_letter_path = Path(__file__).parent.parent / "docs" / "sample artifacts" / "Huy_Ky_General_Cover_Letter.txt"
    
    # Read files
    print("📄 Reading sample files...")
    resume_text = resume_path.read_text(encoding='utf-8')
    cover_letter_text = cover_letter_path.read_text(encoding='utf-8')
    
    print(f"✅ Resume: {len(resume_text)} characters, {len(resume_text.split())} words")
    print(f"✅ Cover Letter: {len(cover_letter_text)} characters, {len(cover_letter_text.split())} words")
    
    # Get database session
    async for db in get_db_session():
        try:
            user_id = 1  # Test user
            
            # Deactivate previous resume samples
            print("\n🔄 Deactivating previous resume samples...")
            stmt = (
                update(SampleDocumentModel)
                .where(
                    SampleDocumentModel.user_id == user_id,
                    SampleDocumentModel.document_type == "resume"
                )
                .values(is_active=False)
            )
            await db.execute(stmt)
            
            # Upload resume
            print("📤 Uploading resume sample...")
            resume_sample = SampleDocumentModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                document_type="resume",
                original_filename="Huy_Ky_Enhanced_Resume.txt",
                original_text=resume_text,
                word_count=len(resume_text.split()),
                character_count=len(resume_text),
                is_active=True
            )
            db.add(resume_sample)
            
            # Deactivate previous cover letter samples
            print("🔄 Deactivating previous cover letter samples...")
            stmt = (
                update(SampleDocumentModel)
                .where(
                    SampleDocumentModel.user_id == user_id,
                    SampleDocumentModel.document_type == "cover_letter"
                )
                .values(is_active=False)
            )
            await db.execute(stmt)
            
            # Upload cover letter
            print("📤 Uploading cover letter sample...")
            cover_letter_sample = SampleDocumentModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                document_type="cover_letter",
                original_filename="Huy_Ky_General_Cover_Letter.txt",
                original_text=cover_letter_text,
                word_count=len(cover_letter_text.split()),
                character_count=len(cover_letter_text),
                is_active=True
            )
            db.add(cover_letter_sample)
            
            await db.commit()
            await db.refresh(resume_sample)
            await db.refresh(cover_letter_sample)
            
            print("\n✅ Successfully uploaded both samples!")
            print(f"\nResume Sample:")
            print(f"  ID: {resume_sample.id}")
            print(f"  Words: {resume_sample.word_count}")
            print(f"  Characters: {resume_sample.character_count}")
            print(f"  Active: {resume_sample.is_active}")
            
            print(f"\nCover Letter Sample:")
            print(f"  ID: {cover_letter_sample.id}")
            print(f"  Words: {cover_letter_sample.word_count}")
            print(f"  Characters: {cover_letter_sample.character_count}")
            print(f"  Active: {cover_letter_sample.is_active}")
            
            # Verify samples in database
            print("\n🔍 Verifying samples in database...")
            stmt = select(SampleDocumentModel).where(
                SampleDocumentModel.user_id == user_id,
                SampleDocumentModel.is_active == True
            )
            result = await db.execute(stmt)
            active_samples = result.scalars().all()
            
            print(f"\n✅ Found {len(active_samples)} active samples for user {user_id}:")
            for sample in active_samples:
                print(f"  - {sample.document_type}: {sample.original_filename} ({sample.word_count} words)")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        break


if __name__ == "__main__":
    print("=" * 60)
    print("Sample Document Upload Test")
    print("=" * 60)
    asyncio.run(test_upload_real_samples())
    print("\n" + "=" * 60)
