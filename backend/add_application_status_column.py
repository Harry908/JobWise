"""
Migration script to add application_status column to jobs table.
Run this script to update existing database: python add_application_status_column.py
"""

import sqlite3
import os

def add_application_status_column():
    """Add application_status column to jobs table if it doesn't exist."""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), 'test.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📂 Connecting to database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'application_status' in columns:
            print("✅ Column 'application_status' already exists!")
            conn.close()
            return True
        
        print("🔧 Adding 'application_status' column to jobs table...")
        
        # Add the new column with default value
        cursor.execute("""
            ALTER TABLE jobs 
            ADD COLUMN application_status TEXT DEFAULT 'not_applied'
        """)
        
        # Update existing rows to have the default value
        cursor.execute("""
            UPDATE jobs 
            SET application_status = 'not_applied' 
            WHERE application_status IS NULL
        """)
        
        # Create index for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_application_status 
            ON jobs(application_status)
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify the change
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'application_status' in columns:
            print("✅ Successfully added 'application_status' column!")
            
            # Show updated schema
            print("\n📋 Updated jobs table schema:")
            cursor.execute("PRAGMA table_info(jobs)")
            for col in cursor.fetchall():
                col_id, name, col_type, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                default_str = f"DEFAULT {default}" if default else ""
                print(f"  - {name}: {col_type} {nullable} {default_str}")
            
            # Count existing jobs
            cursor.execute("SELECT COUNT(*) FROM jobs")
            count = cursor.fetchone()[0]
            print(f"\n✅ Updated {count} existing job(s) with default status 'not_applied'")
            
            conn.close()
            return True
        else:
            print("❌ Failed to add column!")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Database Migration: Add application_status Column")
    print("=" * 60)
    print()
    
    success = add_application_status_column()
    
    print()
    if success:
        print("✅ Migration completed successfully!")
        print("🚀 You can now restart your backend server.")
    else:
        print("❌ Migration failed. Please check the error messages above.")
    print()
