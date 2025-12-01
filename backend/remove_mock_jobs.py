"""Remove all mock jobs from the database.

Mock jobs should NOT be stored in the database.
They should only exist in mock_jobs.json for the browse feature.
"""
import asyncio
from sqlalchemy import text
from app.infrastructure.database.connection import create_engine
from app.infrastructure.database.models import Base
from sqlalchemy.ext.asyncio import AsyncSession


async def remove_mock_jobs():
    """Remove all jobs with source='mock' from database."""
    engine = create_engine()
    
    async with AsyncSession(engine) as session:
        # Count mock jobs before deletion
        result = await session.execute(
            text("SELECT COUNT(*) FROM jobs WHERE source = 'mock'")
        )
        count_before = result.scalar()
        
        print(f"\nFound {count_before} mock jobs in database")
        
        if count_before == 0:
            print("✓ No mock jobs to remove")
            return
        
        # Confirm deletion
        print("\nMock jobs should NOT be in the database.")
        print("They should only exist in mock_jobs.json for browsing.")
        confirm = input("\nDelete all mock jobs from database? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
        
        # Delete mock jobs
        await session.execute(
            text("DELETE FROM jobs WHERE source = 'mock'")
        )
        await session.commit()
        
        # Verify deletion
        result = await session.execute(
            text("SELECT COUNT(*) FROM jobs WHERE source = 'mock'")
        )
        count_after = result.scalar() or 0
        
        deleted = (count_before or 0) - count_after
        print(f"\n✓ Deleted {deleted} mock jobs from database")
        print("✓ Database now contains only user-saved jobs")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(remove_mock_jobs())
