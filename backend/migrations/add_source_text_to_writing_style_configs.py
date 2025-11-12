"""
Migration: Add source_text column to writing_style_configs table

This migration adds a new TEXT column to store the full verbatim text
of the uploaded cover letter for future reference and re-analysis.

Run this migration with:
    python migrations/add_source_text_to_writing_style_configs.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_migration(db_path: str = "jobwise.db"):
    """Add source_text column to writing_style_configs table."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(writing_style_configs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'source_text' in columns:
            print("✅ Column 'source_text' already exists in writing_style_configs table")
            return
        
        # Add the column
        print("Adding 'source_text' column to writing_style_configs table...")
        cursor.execute("""
            ALTER TABLE writing_style_configs 
            ADD COLUMN source_text TEXT
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   Added column: source_text (TEXT)")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


def verify_migration(db_path: str = "jobwise.db"):
    """Verify the migration was successful."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(writing_style_configs)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print("\n📋 Current writing_style_configs schema:")
        for col_name, col_type in columns.items():
            marker = "✨ NEW" if col_name == "source_text" else "  "
            print(f"  {marker} {col_name} ({col_type})")
        
        if 'source_text' in columns and columns['source_text'] == 'TEXT':
            print("\n✅ Verification passed: source_text column exists with correct type")
            return True
        else:
            print("\n❌ Verification failed: source_text column missing or wrong type")
            return False
            
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add source_text column to writing_style_configs")
    parser.add_argument(
        "--db", 
        default="jobwise.db", 
        help="Path to database file (default: jobwise.db)"
    )
    parser.add_argument(
        "--verify-only", 
        action="store_true", 
        help="Only verify migration, don't run it"
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration(args.db)
    else:
        run_migration(args.db)
        verify_migration(args.db)
