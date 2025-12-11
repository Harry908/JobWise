"""Test structured content generation."""

import asyncio
import json
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository


async def test_structured_content():
    """Test that structured content is being generated."""
    engine = create_engine()
    session_factory = create_session_factory(engine)
    
    async with session_factory() as session:
        try:
            gen_repo = GenerationRepository(session)
            profile_repo = ProfileRepository(session)
            
            # Get the most recent generation
            generations = await gen_repo.list_by_user(user_id=1, limit=1)
            
            if not generations:
                print("❌ No generations found for user 1")
                await engine.dispose()
                return
            
            generation = generations[0]
            
            print(f"\n{'='*80}")
            print(f"Generation ID: {generation.id}")
            print(f"Document Type: {generation.document_type.value}")
            print(f"Created At: {generation.created_at}")
            print(f"{'='*80}\n")
            
            # Check plain text
            print("📄 PLAIN TEXT (content_text):")
            print(f"Length: {len(generation.content_text)} characters")
            print(f"Preview: {generation.content_text[:200]}...\n")
            
            # Check structured content
            if generation.content_structured:
                print("✅ STRUCTURED CONTENT (content_structured) EXISTS!")
                try:
                    structured = json.loads(generation.content_structured)
                    print(f"\nStructured JSON keys: {list(structured.keys())}")
                    
                    # Check header
                    if "header" in structured:
                        print(f"\n📋 Header fields: {list(structured['header'].keys())}")
                        print(f"   - Name: {structured['header'].get('name')}")
                        print(f"   - Email: {structured['header'].get('email')}")
                        print(f"   - LinkedIn: {structured['header'].get('linkedin', 'N/A')}")
                        print(f"   - GitHub: {structured['header'].get('github', 'N/A')}")
                        print(f"   - Website: {structured['header'].get('website', 'N/A')}")
                    
                    # Check sections
                    if "sections" in structured:
                        print(f"\n📚 Sections ({len(structured['sections'])} total):")
                        for section in structured['sections']:
                            section_type = section.get('type')
                            print(f"   - {section_type}")
                            
                            if section_type == "skills":
                                categories = section.get('categories', [])
                                print(f"     Categories: {[c['name'] for c in categories]}")
                                for cat in categories:
                                    if cat['name'] == 'Languages':
                                        print(f"       ✅ Languages found: {cat.get('items', [])}")
                                    elif cat['name'] == 'Certifications':
                                        print(f"       ✅ Certifications found: {len(cat.get('items', []))} items")
                                    elif cat['name'] == 'Soft Skills':
                                        print(f"       ✅ Soft Skills found: {cat.get('items', [])}")
                            
                            elif section_type == "experience":
                                entries = section.get('entries', [])
                                print(f"     Entries: {len(entries)}")
                                if entries:
                                    first_exp = entries[0]
                                    print(f"       First experience has 'is_current': {first_exp.get('is_current')}")
                            
                            elif section_type == "projects":
                                entries = section.get('entries', [])
                                print(f"     Entries: {len(entries)}")
                                if entries:
                                    first_proj = entries[0]
                                    print(f"       First project has dates: start={first_proj.get('start_date')}, end={first_proj.get('end_date')}")
                            
                            elif section_type == "education":
                                entries = section.get('entries', [])
                                print(f"     Entries: {len(entries)}")
                                if entries:
                                    first_edu = entries[0]
                                    print(f"       First education has honors: {first_edu.get('honors', [])}")
                    
                    # Check metadata
                    if "metadata" in structured:
                        print(f"\n📊 Metadata:")
                        for key, value in structured['metadata'].items():
                            print(f"   - {key}: {value}")
                    
                    print(f"\n✅ ALL CHECKS PASSED - Structured content is complete!")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse structured content: {e}")
            else:
                print("❌ STRUCTURED CONTENT MISSING!")
                print("This generation was created before the update.")
                print("Generate a new resume/cover letter to test structured content.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_structured_content())
