"""
Migration script: Add job_id and local caching fields to exports table.
Date: December 12, 2025
Purpose: Support job-specific filtering and mobile local caching
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

import sqlite3
from datetime import datetime


def migrate_exports_table():
    """Add job_id, local_cache_path, and cache_expires_at columns to exports table."""
    
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
            print("❌ Error: Table 'exports' does not exist!")
            print("Please run add_exports_table.py first")
            return
        
        # Check current columns
        cursor.execute("PRAGMA table_info(exports)")
        columns = {col[1] for col in cursor.fetchall()}
        
        print("\n📋 Current columns:")
        for col in columns:
            print(f"  - {col}")
        
        # Add job_id column if it doesn't exist
        if 'job_id' not in columns:
            print("\n➕ Adding job_id column...")
            cursor.execute("""
                ALTER TABLE exports
                ADD COLUMN job_id TEXT
            """)
            print("✓ Added job_id column")
            
            # Populate job_id from generations table
            print("📝 Populating job_id from generations...")
            cursor.execute("""
                UPDATE exports
                SET job_id = (
                    SELECT job_id FROM generations
                    WHERE generations.id = exports.generation_id
                )
                WHERE generation_id IS NOT NULL
            """)
            affected = cursor.rowcount
            print(f"✓ Updated {affected} rows with job_id")
            
            # Add foreign key constraint (SQLite doesn't support ALTER TABLE ADD CONSTRAINT)
            # Note: This is noted for documentation; SQLite requires table recreation for FK constraints
            print("⚠️ Note: Foreign key constraint for job_id should be added via table recreation if needed")
        else:
            print("✓ job_id column already exists")
        
        # Add local_cache_path column if it doesn't exist
        if 'local_cache_path' not in columns:
            print("\n➕ Adding local_cache_path column...")
            cursor.execute("""
                ALTER TABLE exports
                ADD COLUMN local_cache_path TEXT
            """)
            print("✓ Added local_cache_path column")
        else:
            print("✓ local_cache_path column already exists")
        
        # Add cache_expires_at column if it doesn't exist
        if 'cache_expires_at' not in columns:
            print("\n➕ Adding cache_expires_at column...")
            cursor.execute("""
                ALTER TABLE exports
                ADD COLUMN cache_expires_at TIMESTAMP
            """)
            print("✓ Added cache_expires_at column")
        else:
            print("✓ cache_expires_at column already exists")
        
        # Create composite index for job-specific queries
        print("\n📑 Creating composite index...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exports_user_job_created
                ON exports(user_id, job_id, created_at)
            """)
            print("✓ Created composite index idx_exports_user_job_created")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
        
        # Create job_id index
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exports_job_id
                ON exports(job_id)
            """)
            print("✓ Created index idx_exports_job_id")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify final table structure
        cursor.execute("PRAGMA table_info(exports)")
        columns = cursor.fetchall()
        
        print("\n📋 Final table structure:")
        for col in columns:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            default = f" DEFAULT {col[4]}" if col[4] else ""
            print(f"  - {col[1]:<25} {col[2]:<15} {nullable}{default}")
        
        # Show indexes
        cursor.execute("PRAGMA index_list(exports)")
        indexes = cursor.fetchall()
        
        print("\n📑 Indexes:")
        for idx in indexes:
            print(f"  - {idx[1]}")
        
        # Show row count
        cursor.execute("SELECT COUNT(*) FROM exports")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total exports: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("Migration: Add job_id and local caching fields to exports table")
    print("=" * 80)
    migrate_exports_table()
    print("\n🎉 Migration script completed!")
