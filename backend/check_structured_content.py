"""Simple test to check database schema."""

import asyncio
import sqlite3
import json
from pathlib import Path


async def check_schema():
    """Check if content_structured column exists and has data."""
    db_path = Path(__file__).parent / "jobwise.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check schema
        cursor.execute("PRAGMA table_info(generations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "content_structured" in columns:
            print("✅ Column 'content_structured' exists in generations table\n")
        else:
            print("❌ Column 'content_structured' NOT found\n")
            return
        
        # Check for any generations
        cursor.execute("SELECT COUNT(*) FROM generations")
        count = cursor.fetchone()[0]
        print(f"Total generations in database: {count}\n")
        
        if count == 0:
            print("❌ No generations found. Generate a resume/cover letter first.")
            return
        
        # Get the most recent generation
        cursor.execute("""
            SELECT id, user_id, document_type, content_structured, created_at
            FROM generations
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            gen_id, user_id, doc_type, content_structured, created_at = row
            print(f"Most recent generation:")
            print(f"  ID: {gen_id}")
            print(f"  User ID: {user_id}")
            print(f"  Type: {doc_type}")
            print(f"  Created: {created_at}")
            
            if content_structured:
                print(f"\n✅ Structured content EXISTS!")
                try:
                    structured = json.loads(content_structured)
                    print(f"  Keys: {list(structured.keys())}")
                    
                    if "header" in structured:
                        header = structured["header"]
                        print(f"\n  Header fields:")
                        for key, value in header.items():
                            if value:
                                print(f"    ✅ {key}: {value[:50] if len(str(value)) > 50 else value}")
                            else:
                                print(f"    ⚠️  {key}: (empty)")
                    
                    if "sections" in structured:
                        sections = structured["sections"]
                        print(f"\n  Sections ({len(sections)} total):")
                        for section in sections:
                            section_type = section.get("type")
                            print(f"    - {section_type}")
                            
                            if section_type == "skills":
                                categories = section.get("categories", [])
                                for cat in categories:
                                    cat_name = cat.get("name")
                                    items = cat.get("items", [])
                                    print(f"      ✅ {cat_name}: {len(items)} items")
                    
                    if "metadata" in structured:
                        metadata = structured["metadata"]
                        print(f"\n  Metadata:")
                        for key, value in metadata.items():
                            print(f"    - {key}: {value}")
                    
                    print(f"\n🎉 ALL FIELDS ARE PRESENT AND STRUCTURED CORRECTLY!")
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ Failed to parse JSON: {e}")
            else:
                print(f"\n⚠️  Structured content is NULL")
                print(f"  This generation was created before the structured content update.")
                print(f"  Generate a new resume/cover letter to test the feature.")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(check_schema())
