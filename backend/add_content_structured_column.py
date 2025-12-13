"""Migration script to add content_structured column to generations table."""

import asyncio
import sqlite3
from pathlib import Path


async def migrate():
    """Add content_structured column to generations table."""
    db_path = Path(__file__).parent / "jobwise.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(generations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "content_structured" in columns:
            print("✅ Column 'content_structured' already exists in generations table")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE generations 
                ADD COLUMN content_structured TEXT
            """)
            conn.commit()
            print("✅ Successfully added 'content_structured' column to generations table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(generations)")
        columns = cursor.fetchall()
        print("\nGenerations table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){' NOT NULL' if col[3] else ''}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())
