"""
Migration: Create separate writing_styles table and migrate data from sample_documents.

This migration:
1. Creates the new writing_styles table
2. Migrates existing writing style data from sample_documents
3. Removes writing style columns from sample_documents
"""

import sqlite3
import logging
import json
import uuid
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "jobwise.db"

def create_writing_styles_table(cursor):
    """Create the new writing_styles table."""
    logger.info("🔄 Creating writing_styles table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS writing_styles (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            extracted_style TEXT NOT NULL,
            extraction_status TEXT DEFAULT 'pending' NOT NULL,
            extraction_model TEXT,
            extraction_timestamp DATETIME,
            extraction_confidence REAL,
            source_sample_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (source_sample_id) REFERENCES sample_documents(id) ON DELETE SET NULL
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_writing_styles_user_id ON writing_styles(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_writing_styles_status ON writing_styles(extraction_status)")
    
    logger.info("✅ Created writing_styles table with indexes")

def migrate_existing_data(cursor):
    """Migrate existing writing style data from sample_documents to writing_styles."""
    logger.info("🔄 Migrating existing writing style data...")
    
    # Find sample documents with writing style data
    cursor.execute("""
        SELECT id, user_id, extracted_writing_style, style_extraction_status, 
               style_extraction_model, style_extraction_timestamp, style_extraction_confidence
        FROM sample_documents 
        WHERE extracted_writing_style IS NOT NULL
        AND document_type = 'cover_letter'
    """)
    
    samples_with_styles = cursor.fetchall()
    migrated_count = 0
    
    for sample in samples_with_styles:
        sample_id, user_id, style_data, status, model, timestamp, confidence = sample
        
        # Check if user already has a writing style (avoid duplicates)
        cursor.execute("SELECT COUNT(*) FROM writing_styles WHERE user_id = ?", (user_id,))
        if cursor.fetchone()[0] > 0:
            logger.info(f"   User {user_id} already has writing style, skipping...")
            continue
        
        # Create new writing style record
        writing_style_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO writing_styles (
                id, user_id, extracted_style, extraction_status, extraction_model,
                extraction_timestamp, extraction_confidence, source_sample_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            writing_style_id, user_id, style_data, status or 'completed', model,
            timestamp, confidence, sample_id, now, now
        ))
        
        migrated_count += 1
        logger.info(f"   Migrated writing style for user {user_id} from sample {sample_id}")
    
    logger.info(f"✅ Migrated {migrated_count} writing style records")

def remove_writing_style_columns(cursor):
    """Remove writing style columns from sample_documents table."""
    logger.info("🔄 Removing writing style columns from sample_documents...")
    
    # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
    # First, get the current table structure (excluding writing style columns)
    cursor.execute("PRAGMA table_info(sample_documents)")
    columns = cursor.fetchall()
    
    # Define columns to keep (exclude writing style columns)
    keep_columns = []
    for col in columns:
        col_name = col[1]  # Column name is at index 1
        if col_name not in [
            'extracted_writing_style', 'style_extraction_status', 
            'style_extraction_model', 'style_extraction_timestamp', 
            'style_extraction_confidence'
        ]:
            keep_columns.append(col)
    
    # Create column definitions for new table
    column_defs = []
    column_names = []
    for col in keep_columns:
        col_name, col_type, not_null, default_value, pk = col[1], col[2], col[3], col[4], col[5]
        column_names.append(col_name)
        
        col_def = f"{col_name} {col_type}"
        if not_null:
            col_def += " NOT NULL"
        if default_value is not None:
            col_def += f" DEFAULT {default_value}"
        if pk:
            col_def += " PRIMARY KEY"
        column_defs.append(col_def)
    
    # Add foreign key constraint
    column_defs.append("FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
    
    # Create new table structure
    new_table_sql = f"""
        CREATE TABLE sample_documents_new (
            {', '.join(column_defs)}
        )
    """
    
    cursor.execute(new_table_sql)
    
    # Copy data to new table
    columns_str = ', '.join(column_names)
    cursor.execute(f"""
        INSERT INTO sample_documents_new ({columns_str})
        SELECT {columns_str} FROM sample_documents
    """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE sample_documents")
    cursor.execute("ALTER TABLE sample_documents_new RENAME TO sample_documents")
    
    # Recreate indexes
    cursor.execute("CREATE INDEX idx_sample_documents_user_id ON sample_documents(user_id)")
    cursor.execute("CREATE INDEX idx_sample_documents_user_type ON sample_documents(user_id, document_type)")
    cursor.execute("CREATE INDEX idx_sample_documents_active ON sample_documents(user_id, document_type, is_active)")
    
    logger.info("✅ Removed writing style columns and recreated table with indexes")

def main():
    """Main migration function."""
    logger.info("=" * 70)
    logger.info("JobWise Database Migration - Separate Writing Styles Table")
    logger.info("Creating normalized writing_styles table and migrating data")
    logger.info("=" * 70)
    
    if not DB_PATH.exists():
        logger.error("❌ Database doesn't exist! Please run init_database.py first.")
        return 1
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Step 1: Create writing_styles table
        create_writing_styles_table(cursor)
        
        # Step 2: Migrate existing data
        migrate_existing_data(cursor)
        
        # Step 3: Remove writing style columns from sample_documents
        remove_writing_style_columns(cursor)
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        logger.info("\\n🎉 Migration completed successfully!")
        logger.info("Database now has normalized writing styles storage:")
        logger.info("  ✅ writing_styles table created with proper relationships")
        logger.info("  ✅ Existing writing style data migrated")
        logger.info("  ✅ sample_documents table cleaned of writing style columns")
        logger.info("  ✅ All indexes recreated for optimal performance")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return 1

if __name__ == "__main__":
    exit(main())