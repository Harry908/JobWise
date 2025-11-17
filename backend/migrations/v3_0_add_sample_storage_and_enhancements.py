"""
Migration: V3.0 - Add text-only sample storage and profile enhancements

This migration implements the v3.0 system redesign:
1. Creates 3 new tables: sample_documents, job_content_rankings, prompt_templates
2. Adds enhanced columns to existing tables: master_profiles, experiences, projects, generations
3. Creates necessary indices for performance

DOES NOT remove old v2.0 tables to maintain backward compatibility.

Run this migration with:
    python migrations/v3_0_add_sample_storage_and_enhancements.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_sample_documents_table(cursor):
    """Create sample_documents table for text-only storage."""
    print("Creating sample_documents table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sample_documents (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            document_type TEXT NOT NULL CHECK(document_type IN ('resume', 'cover_letter')),
            original_filename TEXT,
            upload_timestamp TEXT NOT NULL,
            original_text TEXT NOT NULL,
            word_count INTEGER,
            character_count INTEGER,
            line_count INTEGER,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            archived_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sample_documents_user_id ON sample_documents(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sample_documents_document_type ON sample_documents(document_type)")
    
    print("✅ Created sample_documents table with 2 indices")


def create_job_content_rankings_table(cursor):
    """Create job_content_rankings table for job-specific ranking."""
    print("Creating job_content_rankings table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_content_rankings (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            job_id TEXT NOT NULL,
            ranked_experience_ids TEXT NOT NULL,
            ranked_project_ids TEXT NOT NULL,
            ranked_skill_ids TEXT NOT NULL,
            ranking_model_used TEXT,
            ranking_timestamp TEXT NOT NULL,
            ranking_confidence_score REAL,
            ranking_explanations TEXT,
            times_used_in_generation INTEGER DEFAULT 0,
            last_used_at TEXT,
            user_modified BOOLEAN DEFAULT 0,
            user_override_timestamp TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)
    
    # Create indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_content_rankings_user_id ON job_content_rankings(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_content_rankings_job_id ON job_content_rankings(job_id)")
    
    print("✅ Created job_content_rankings table with 2 indices")


def create_prompt_templates_table(cursor):
    """Create prompt_templates table for database-stored Jinja2 templates."""
    print("Creating prompt_templates table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL DEFAULT '1.0.0',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            template_content TEXT NOT NULL,
            required_variables TEXT NOT NULL,
            optional_variables TEXT,
            description TEXT,
            expected_output_format TEXT,
            estimated_tokens INTEGER,
            ab_test_group TEXT,
            performance_metrics TEXT,
            deprecated_at TEXT,
            superseded_by_template_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT
        )
    """)
    
    # Create indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_templates_template_name ON prompt_templates(template_name)")
    
    print("✅ Created prompt_templates table with 1 index")


def add_enhanced_columns_to_master_profiles(cursor):
    """Add AI enhancement columns to master_profiles table."""
    print("Adding enhanced columns to master_profiles...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(master_profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    
    added = []
    
    if 'enhanced_professional_summary' not in columns:
        cursor.execute("ALTER TABLE master_profiles ADD COLUMN enhanced_professional_summary TEXT")
        added.append("enhanced_professional_summary")
    
    if 'enhancement_metadata' not in columns:
        cursor.execute("ALTER TABLE master_profiles ADD COLUMN enhancement_metadata TEXT")
        added.append("enhancement_metadata")
    
    if added:
        print(f"✅ Added columns to master_profiles: {', '.join(added)}")
    else:
        print("✅ master_profiles already has enhanced columns")


def add_enhanced_columns_to_experiences(cursor):
    """Add AI enhancement columns to experiences table."""
    print("Adding enhanced columns to experiences...")
    
    cursor.execute("PRAGMA table_info(experiences)")
    columns = [row[1] for row in cursor.fetchall()]
    
    added = []
    
    if 'enhanced_description' not in columns:
        cursor.execute("ALTER TABLE experiences ADD COLUMN enhanced_description TEXT")
        added.append("enhanced_description")
    
    if 'enhancement_metadata' not in columns:
        cursor.execute("ALTER TABLE experiences ADD COLUMN enhancement_metadata TEXT")
        added.append("enhancement_metadata")
    
    if added:
        print(f"✅ Added columns to experiences: {', '.join(added)}")
    else:
        print("✅ experiences already has enhanced columns")


def add_enhanced_columns_to_projects(cursor):
    """Add AI enhancement columns to projects table."""
    print("Adding enhanced columns to projects...")
    
    cursor.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    
    added = []
    
    if 'enhanced_description' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN enhanced_description TEXT")
        added.append("enhanced_description")
    
    if 'enhancement_metadata' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN enhancement_metadata TEXT")
        added.append("enhancement_metadata")
    
    if added:
        print(f"✅ Added columns to projects: {', '.join(added)}")
    else:
        print("✅ projects already has enhanced columns")


def add_user_custom_prompt_to_generations(cursor):
    """Add user_custom_prompt column to generations table."""
    print("Adding user_custom_prompt to generations...")
    
    cursor.execute("PRAGMA table_info(generations)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'user_custom_prompt' not in columns:
        cursor.execute("ALTER TABLE generations ADD COLUMN user_custom_prompt TEXT")
        print("✅ Added user_custom_prompt column to generations")
    else:
        print("✅ generations already has user_custom_prompt column")


def run_migration(db_path: str = "jobwise.db"):
    """Run the complete v3.0 migration."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Starting V3.0 Migration")
        print("=" * 60)
        print()
        
        # Create new tables
        create_sample_documents_table(cursor)
        create_job_content_rankings_table(cursor)
        create_prompt_templates_table(cursor)
        
        print()
        
        # Add enhanced columns to existing tables
        add_enhanced_columns_to_master_profiles(cursor)
        add_enhanced_columns_to_experiences(cursor)
        add_enhanced_columns_to_projects(cursor)
        add_user_custom_prompt_to_generations(cursor)
        
        conn.commit()
        
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


def verify_migration(db_path: str = "jobwise.db"):
    """Verify the migration was successful."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("Verifying Migration")
        print("=" * 60)
        
        # Check for new tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['sample_documents', 'job_content_rankings', 'prompt_templates']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print(f"\n✅ All 3 new tables created: {', '.join(required_tables)}")
        
        # Check enhanced columns in master_profiles
        cursor.execute("PRAGMA table_info(master_profiles)")
        mp_columns = [row[1] for row in cursor.fetchall()]
        
        required_mp_cols = ['enhanced_professional_summary', 'enhancement_metadata']
        missing_mp_cols = [c for c in required_mp_cols if c not in mp_columns]
        
        if missing_mp_cols:
            print(f"❌ master_profiles missing columns: {', '.join(missing_mp_cols)}")
            return False
        else:
            print(f"✅ master_profiles has enhanced columns")
        
        # Check enhanced columns in experiences
        cursor.execute("PRAGMA table_info(experiences)")
        exp_columns = [row[1] for row in cursor.fetchall()]
        
        required_exp_cols = ['enhanced_description', 'enhancement_metadata']
        missing_exp_cols = [c for c in required_exp_cols if c not in exp_columns]
        
        if missing_exp_cols:
            print(f"❌ experiences missing columns: {', '.join(missing_exp_cols)}")
            return False
        else:
            print(f"✅ experiences has enhanced columns")
        
        # Check enhanced columns in projects
        cursor.execute("PRAGMA table_info(projects)")
        proj_columns = [row[1] for row in cursor.fetchall()]
        
        required_proj_cols = ['enhanced_description', 'enhancement_metadata']
        missing_proj_cols = [c for c in required_proj_cols if c not in proj_columns]
        
        if missing_proj_cols:
            print(f"❌ projects missing columns: {', '.join(missing_proj_cols)}")
            return False
        else:
            print(f"✅ projects has enhanced columns")
        
        # Check user_custom_prompt in generations
        cursor.execute("PRAGMA table_info(generations)")
        gen_columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_custom_prompt' not in gen_columns:
            print("❌ generations missing user_custom_prompt column")
            return False
        else:
            print("✅ generations has user_custom_prompt column")
        
        print("\n" + "=" * 60)
        print("✅ All verification checks passed!")
        print("=" * 60)
        return True
            
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="V3.0 Migration: Add sample storage and enhancements")
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
