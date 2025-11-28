"""
Add writing style storage fields to sample_documents table.

Migration for database schema update to support writing style caching.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "jobwise.db"

def add_writing_style_fields():
    """Add writing style fields to sample_documents table."""
    logger.info("🔄 Adding writing style fields to sample_documents table...")
    
    if not DB_PATH.exists():
        logger.warning("Database doesn't exist. Fields will be added when tables are created.")
        return True
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='sample_documents'
        """)
        
        if cursor.fetchone()[0] == 0:
            logger.info("sample_documents table doesn't exist yet. Fields will be added when created.")
            conn.close()
            return True
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(sample_documents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_fields = [
            "extracted_writing_style",
            "style_extraction_status", 
            "style_extraction_model",
            "style_extraction_timestamp",
            "style_extraction_confidence"
        ]
        
        existing_fields = [field for field in new_fields if field in columns]
        if existing_fields:
            logger.info(f"✅ Writing style fields already exist: {existing_fields}")
            conn.close()
            return True
        
        logger.info("Adding new writing style fields...")
        
        # Add new fields
        cursor.execute("ALTER TABLE sample_documents ADD COLUMN extracted_writing_style TEXT")
        cursor.execute("ALTER TABLE sample_documents ADD COLUMN style_extraction_status TEXT DEFAULT 'pending'")
        cursor.execute("ALTER TABLE sample_documents ADD COLUMN style_extraction_model TEXT")
        cursor.execute("ALTER TABLE sample_documents ADD COLUMN style_extraction_timestamp DATETIME")
        cursor.execute("ALTER TABLE sample_documents ADD COLUMN style_extraction_confidence REAL")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        logger.info("✅ Successfully added writing style fields to sample_documents table")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding writing style fields: {e}")
        return False

def main():
    """Main migration function."""
    logger.info("=" * 60)
    logger.info("JobWise Database Migration - Add Writing Style Fields")
    logger.info("Adding caching support for extracted writing styles")
    logger.info("=" * 60)
    
    success = add_writing_style_fields()
    
    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("Writing style extraction will now be cached in database")
        logger.info("Benefits:")
        logger.info("  ✅ Faster profile enhancement (cached styles)")
        logger.info("  ✅ Consistent style analysis across sessions") 
        logger.info("  ✅ Ability to re-extract styles when needed")
    else:
        logger.error("\n❌ Migration failed!")
        logger.error("Check logs above for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())