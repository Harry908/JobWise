"""
Remove deprecated database tables and associated code.

Based on Sprint 5 design document:
docs/sprint5/01-DATABASE-SCHEMA.md

Removes v2.0 tables that are no longer needed in V3 system.
"""

import asyncio
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tables to remove per Sprint 5 design
DEPRECATED_TABLES = [
    'writing_style_configs',
    'layout_configs', 
    'user_generation_profiles',
    'example_resumes',
    'consistency_scores',
    'job_type_overrides'
]

DB_PATH = Path(__file__).parent / "instance" / "jobwise.db"

def backup_database():
    """Create backup before dropping tables."""
    backup_path = DB_PATH.parent / f"jobwise_backup_{int(asyncio.get_event_loop().time())}.db"
    
    if not DB_PATH.exists():
        logger.warning(f"Database not found: {DB_PATH}")
        return None
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"✅ Database backed up to: {backup_path}")
    return backup_path

def check_table_exists(cursor, table_name):
    """Check if table exists in database."""
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone()[0] > 0

def get_table_row_count(cursor, table_name):
    """Get number of rows in table."""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except Exception:
        return 0

def drop_deprecated_tables():
    """Drop deprecated database tables."""
    logger.info("🗑️  Starting database schema cleanup...")
    
    # Backup first
    backup_path = backup_database()
    if not backup_path and DB_PATH.exists():
        logger.error("Failed to backup database. Aborting.")
        return False
    
    if not DB_PATH.exists():
        logger.warning("Database doesn't exist. Nothing to clean up.")
        return True
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check which tables exist and their sizes
        logger.info("\n📊 Current table status:")
        existing_tables = []
        for table in DEPRECATED_TABLES:
            if check_table_exists(cursor, table):
                row_count = get_table_row_count(cursor, table)
                logger.info(f"  • {table}: {row_count} rows")
                existing_tables.append((table, row_count))
            else:
                logger.info(f"  • {table}: NOT FOUND")
        
        if not existing_tables:
            logger.info("✅ No deprecated tables found. Database is already clean.")
            conn.close()
            return True
        
        # Drop tables in reverse dependency order to avoid FK constraint issues
        drop_order = [
            'user_generation_profiles',  # References writing_style_configs, layout_configs
            'example_resumes',           # References layout_configs
            'consistency_scores',        # Independent
            'job_type_overrides',        # Independent
            'writing_style_configs',     # Referenced by others
            'layout_configs'             # Referenced by others
        ]
        
        logger.info(f"\n🗑️  Dropping {len(existing_tables)} deprecated tables...")
        
        for table in drop_order:
            if any(t[0] == table for t in existing_tables):
                logger.info(f"  Dropping table: {table}")
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        # Commit changes
        conn.commit()
        
        # Verify tables are gone
        logger.info("\n✅ Verification - Checking remaining tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        remaining_tables = [row[0] for row in cursor.fetchall()]
        
        # Check if any deprecated tables remain
        remaining_deprecated = [t for t in DEPRECATED_TABLES if t in remaining_tables]
        if remaining_deprecated:
            logger.error(f"❌ Some tables still exist: {remaining_deprecated}")
            conn.close()
            return False
        
        logger.info(f"✅ All deprecated tables removed successfully!")
        logger.info(f"✅ Current tables ({len(remaining_tables)}): {', '.join(remaining_tables)}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        if backup_path:
            logger.info(f"Database backup available at: {backup_path}")
        return False

def main():
    """Main cleanup function."""
    logger.info("=" * 60)
    logger.info("JobWise Database Schema Cleanup - Sprint 5")
    logger.info("Removing deprecated v2.0 tables per design document")
    logger.info("=" * 60)
    
    success = drop_deprecated_tables()
    
    if success:
        logger.info("\n🎉 Database cleanup completed successfully!")
        logger.info("The following deprecated tables have been removed:")
        for table in DEPRECATED_TABLES:
            logger.info(f"  ❌ {table}")
        logger.info("\nV3 system tables remain intact:")
        logger.info("  ✅ sample_documents")
        logger.info("  ✅ job_content_rankings") 
        logger.info("  ✅ prompt_templates")
        logger.info("  ✅ users, master_profiles, experiences, projects, generations, etc.")
    else:
        logger.error("\n❌ Database cleanup failed!")
        logger.error("Check logs above for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())