"""Fix invalid job sources in the database."""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.infrastructure.database.connection import create_engine
from sqlalchemy import text


async def fix_invalid_sources():
    """Fix invalid job source values in the database."""
    engine = create_engine()
    
    valid_sources = [
        'user_created',
        'indeed',
        'linkedin',
        'glassdoor',
        'mock',
        'imported',
        'url_import'
    ]
    
    try:
        async with engine.begin() as conn:
            # Find all invalid sources
            placeholders = ', '.join([f"'{s}'" for s in valid_sources])
            query = f"SELECT DISTINCT source FROM jobs WHERE source NOT IN ({placeholders})"
            result = await conn.execute(text(query))
            invalid_sources = [row[0] for row in result.fetchall()]
            
            if not invalid_sources:
                print("✓ No invalid job sources found!")
                return
            
            print(f"Found invalid sources: {invalid_sources}")
            print(f"\nWill convert them to 'user_created'")
            
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("Cancelled.")
                return
            
            # Update invalid sources to 'user_created'
            for invalid_source in invalid_sources:
                result = await conn.execute(
                    text("UPDATE jobs SET source = 'user_created' WHERE source = :invalid_source"),
                    {"invalid_source": invalid_source}
                )
                count = result.rowcount
                print(f"✓ Updated {count} jobs from '{invalid_source}' to 'user_created'")
            
            print("\n✓ All invalid sources have been fixed!")
            
    except Exception as e:
        print(f"❌ Error fixing sources: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    print("="*80)
    print("FIX INVALID JOB SOURCES")
    print("="*80)
    print("\nThis will update jobs with invalid source values to 'user_created'")
    print(f"Valid sources: user_created, indeed, linkedin, glassdoor, mock, imported, url_import")
    print()
    
    await fix_invalid_sources()
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
