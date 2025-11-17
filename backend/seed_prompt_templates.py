"""
Seed prompt templates into database.

Run this script to populate the prompt_templates table with initial Jinja2 templates.

Usage:
    python backend/seed_prompt_templates.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.application.services.prompt_service import PromptService

if __name__ == "__main__":
    print("=" * 60)
    print("Seeding Prompt Templates")
    print("=" * 60)
    print()
    
    db_path = "jobwise.db"
    
    try:
        count = PromptService.seed_templates(db_path=db_path)
        
        print()
        print("=" * 60)
        print(f"✅ Successfully seeded {count} prompt templates")
        print("=" * 60)
        print()
        print("Templates available:")
        print("  1. writing_style_extraction v1.0.0")
        print("  2. profile_enhancement v1.0.0")
        print("  3. content_ranking v1.0.0")
        print("  4. cover_letter_generation v1.0.0")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Failed to seed templates: {e}")
        print("=" * 60)
        sys.exit(1)
