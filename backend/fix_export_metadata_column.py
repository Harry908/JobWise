"""
Migration script: Fix export_metadata column name mismatch.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

import sqlite3


def fix_export_metadata_column():
    """Rename metadata column to export_metadata in exports table."""
    
    # Connect to database
    db_path = Path(__file__).parent / "jobwise.db"
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if exports table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='exports'
        """)
        
        if not cursor.fetchone():
            print("⚠️ Table 'exports' doesn't exist!")
            return
        
        # Check current column names
        cursor.execute("PRAGMA table_info(exports)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("Current columns:", column_names)
        
        if 'export_metadata' in column_names:
            print("✓ Column 'export_metadata' already exists!")
            return
        
        if 'metadata' not in column_names:
            print("⚠️ Column 'metadata' not found, adding 'export_metadata' column")
            cursor.execute("ALTER TABLE exports ADD COLUMN export_metadata TEXT")
            conn.commit()
            print("✓ Added 'export_metadata' column")
            return
        
        print("Renaming 'metadata' to 'export_metadata'...")
        
        # SQLite doesn't support RENAME COLUMN directly in older versions
        # We need to recreate the table
        
        # Get all data from current table
        cursor.execute("SELECT * FROM exports")
        rows = cursor.fetchall()
        
        # Drop and recreate with correct column name
        cursor.execute("DROP TABLE IF EXISTS exports_backup")
        
        # Drop existing indexes
        cursor.execute("DROP INDEX IF EXISTS idx_exports_user_id")
        cursor.execute("DROP INDEX IF EXISTS idx_exports_generation_id")
        cursor.execute("DROP INDEX IF EXISTS idx_exports_format")
        cursor.execute("DROP INDEX IF EXISTS idx_exports_created_at")
        
        cursor.execute("ALTER TABLE exports RENAME TO exports_backup")
        
        # Create new table with correct column name
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
                export_metadata TEXT,
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
        
        # Copy data from backup
        if rows:
            cursor.executemany("""
                INSERT INTO exports 
                (id, user_id, generation_id, format, template, filename, file_path, 
                 file_size_bytes, page_count, options, export_metadata, download_url, 
                 expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            print(f"✓ Migrated {len(rows)} rows")
        
        # Drop backup table
        cursor.execute("DROP TABLE exports_backup")
        
        conn.commit()
        print("✓ Successfully renamed 'metadata' to 'export_metadata'")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(exports)")
        columns = cursor.fetchall()
        
        print("\nUpdated table structure:")
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
    print("Migration: Fix export_metadata column name")
    print("=" * 60)
    fix_export_metadata_column()
    print("\nMigration complete!")
