"""Clear all rankings from the database to test with fresh data."""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.infrastructure.database.connection import create_engine
from sqlalchemy import text


async def clear_rankings():
    """Clear all rankings and generations from database."""
    engine = create_engine()
    
    try:
        async with engine.begin() as conn:
            # First, delete all generations (they reference rankings)
            result = await conn.execute(text("DELETE FROM generations"))
            generations_deleted = result.rowcount
            
            # Then delete all rankings
            result = await conn.execute(text("DELETE FROM job_content_rankings"))
            rankings_deleted = result.rowcount
            
            print(f"✓ Cleared {generations_deleted} generations")
            print(f"✓ Cleared {rankings_deleted} rankings")
            print("\nAll rankings have been cleared!")
            print("You can now generate fresh rankings with the updated ranking system.")
            
    except Exception as e:
        print(f"❌ Error clearing rankings: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    print("="*80)
    print("CLEAR ALL RANKINGS")
    print("="*80)
    print("\nThis will delete:")
    print("  - All job content rankings")
    print("  - All generated resumes and cover letters")
    print("\nThis allows you to test with fresh rankings using the updated system.")
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\nClearing rankings...")
    await clear_rankings()
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
