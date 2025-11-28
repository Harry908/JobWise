"""Add employment_type field to jobs table

This migration adds the employment_type column to the jobs table
to support tracking the type of employment (full_time, part_time, contract, etc.)

Run this migration after V3.0 updates.
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def add_employment_type_to_jobs(db_path: str = "jobwise.db"):
    """Add employment_type column to jobs table"""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'employment_type' in columns:
            logger.info("employment_type column already exists in jobs table")
            return True
            
        # Add the column with default value
        cursor.execute("""
            ALTER TABLE jobs 
            ADD COLUMN employment_type TEXT DEFAULT 'full_time'
        """)
        
        # Update existing rows to have the default value
        cursor.execute("""
            UPDATE jobs 
            SET employment_type = 'full_time' 
            WHERE employment_type IS NULL
        """)
        
        conn.commit()
        logger.info("Successfully added employment_type column to jobs table")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add employment_type column: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Run the migration"""
    logger.info("Starting employment_type migration...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run migration
    success = add_employment_type_to_jobs()
    
    if success:
        logger.info("Employment type migration completed successfully")
    else:
        logger.error("Employment type migration failed")
        exit(1)

if __name__ == "__main__":
    main()