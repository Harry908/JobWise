"""
Migration script: Add exports table to database.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

import sqlite3
from datetime import datetime


def add_exports_table():
    """Add exports table to database."""
    
    # Connect to database
    db_path = Path(__file__).parent / "jobwise.db"
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if exports table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='exports'
        """)
        
        if cursor.fetchone():
            print("⚠️ Table 'exports' already exists!")
            choice = input("Drop and recreate? (yes/no): ")
            if choice.lower() == 'yes':
                cursor.execute("DROP TABLE exports")
                print("✓ Dropped existing 'exports' table")
            else:
                print("Skipping table creation")
                return
        
        # Create exports table
        cursor.execute("""
            CREATE TABLE exports (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                generation_id TEXT,
                format TEXT NOT NULL,
                template TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                page_count INTEGER,
                options TEXT,
                metadata TEXT,
                download_url TEXT,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (generation_id) REFERENCES generations(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_exports_user_id ON exports(user_id)")
        cursor.execute("CREATE INDEX idx_exports_generation_id ON exports(generation_id)")
        cursor.execute("CREATE INDEX idx_exports_format ON exports(format)")
        cursor.execute("CREATE INDEX idx_exports_created_at ON exports(created_at)")
        
        conn.commit()
        print("✓ Created 'exports' table successfully")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(exports)")
        columns = cursor.fetchall()
        
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add exports table")
    print("=" * 60)
    add_exports_table()
    print("\nMigration complete!")
