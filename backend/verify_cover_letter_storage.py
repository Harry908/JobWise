"""
Verification script for cover letter text storage implementation.

This script verifies that:
1. The source_text column exists in writing_style_configs table
2. The WritingStyleConfig entity has the source_text field
3. The database model has the source_text column
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from app.domain.entities.preferences.writing_style_config import WritingStyleConfig
from app.infrastructure.database.models import WritingStyleConfigModel

def verify_database_schema():
    """Verify database has source_text column."""
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 60)
    
    conn = sqlite3.connect('jobwise.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(writing_style_configs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    if 'source_text' in columns:
        print("✅ Column 'source_text' exists in writing_style_configs table")
        print(f"   Type: {columns['source_text']}")
    else:
        print("❌ Column 'source_text' NOT FOUND in writing_style_configs table")
        return False
    
    conn.close()
    return True


def verify_domain_entity():
    """Verify domain entity has source_text field."""
    print("\n" + "=" * 60)
    print("DOMAIN ENTITY VERIFICATION")
    print("=" * 60)
    
    # Create a test instance
    config = WritingStyleConfig(
        user_id=1,
        source_text="This is a test cover letter text"
    )
    
    if hasattr(config, 'source_text'):
        print("✅ WritingStyleConfig entity has 'source_text' field")
        print(f"   Value: {config.source_text[:50]}...")
    else:
        print("❌ WritingStyleConfig entity missing 'source_text' field")
        return False
    
    return True


def verify_database_model():
    """Verify database model has source_text column."""
    print("\n" + "=" * 60)
    print("DATABASE MODEL VERIFICATION")
    print("=" * 60)
    
    if hasattr(WritingStyleConfigModel, 'source_text'):
        print("✅ WritingStyleConfigModel has 'source_text' column")
        print(f"   Type: {WritingStyleConfigModel.source_text.type}")
    else:
        print("❌ WritingStyleConfigModel missing 'source_text' column")
        return False
    
    return True


def print_summary():
    """Print implementation summary."""
    print("\n" + "=" * 60)
    print("IMPLEMENTATION SUMMARY")
    print("=" * 60)
    
    print("""
Cover Letter Text Storage:
├── Database Table: writing_style_configs
│   └── Column: source_text (TEXT)
│
├── Domain Entity: WritingStyleConfig
│   └── Field: source_text (Optional[str])
│
├── Database Model: WritingStyleConfigModel
│   └── Column: source_text (Text)
│
└── Service Layer: PreferenceExtractionService
    └── Method: extract_writing_style_from_cover_letter()
        └── Saves: style_config.source_text = text_content

Benefits:
✓ Full text persistence in database
✓ No need to re-read files for text content
✓ Enables future re-analysis without file access
✓ Supports user review of uploaded text
✓ Improves data integrity and audit trail
    """)


if __name__ == "__main__":
    print("\n🔍 VERIFYING COVER LETTER TEXT STORAGE IMPLEMENTATION\n")
    
    results = []
    
    # Run all verifications
    results.append(("Database Schema", verify_database_schema()))
    results.append(("Domain Entity", verify_domain_entity()))
    results.append(("Database Model", verify_database_model()))
    
    # Print summary
    print_summary()
    
    # Final result
    print("=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED - Implementation complete!")
    else:
        print("❌ SOME VERIFICATIONS FAILED - Review implementation")
    print("=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)
