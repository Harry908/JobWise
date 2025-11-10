#!/usr/bin/env python3
"""
Test enhanced GroqAdapter with anti-hallucination features using master resume data.

This test validates:
1. Updated default model (llama-3.3-70b-versatile)
2. Enhanced resume generation with fact-checking
3. Anti-hallucination prompt engineering
4. Comprehensive test data usage
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
import sys
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from infrastructure.adapters.groq_adapter import GroqAdapter
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent / "app"))
    from infrastructure.adapters.groq_adapter import GroqAdapter


async def test_enhanced_groq_adapter():
    """Test the enhanced GroqAdapter with master resume data."""
    
    print("🔬 Testing Enhanced GroqAdapter with Anti-Hallucination Features")
    print("=" * 60)
    
    # Load test master resume data
    data_file = Path(__file__).parent / "data" / "test_master_resume.json"
    if not data_file.exists():
        print("❌ Test master resume data not found. Please ensure test_master_resume.json exists in backend/data/")
        return
        
    with open(data_file, 'r') as f:
        test_data = json.load(f)
    
    # Extract user data from nested structure
    user_data = {
        'full_name': test_data['personal_info']['full_name'],
        'email': test_data['personal_info']['email'],
        'phone': test_data['personal_info']['phone'],
        'location': test_data['personal_info']['location'],
        'skills': ([skill['name'] for skill in test_data['technical_skills']['programming_languages']] + 
                  [skill['name'] for skill in test_data['technical_skills']['frameworks_tools']] +
                  [skill['name'] for skill in test_data['technical_skills']['testing_frameworks']] +
                  test_data['technical_skills']['concepts']),
        'work_experience': test_data['professional_experience'],
        'education': test_data['education'],
        'projects': test_data['projects']
    }
    
    print(f"📄 Loaded test data for: {user_data['full_name']}")
    print(f"📧 Email: {user_data['email']}")
    print(f"🎓 Degree: {user_data['education'][0]['degree']} in {user_data['education'][0]['major']}")
    print(f"💼 Experience: {len(user_data['work_experience'])} positions")
    print(f"🛠️ Skills: {len(user_data['skills'])} technical skills")
    print(f"🚀 Projects: {len(user_data['projects'])} projects")
    print()
    
    # Initialize GroqAdapter (should now default to llama-3.3-70b-versatile)
    try:
        adapter = GroqAdapter()
        print(f"✅ GroqAdapter initialized with model: {adapter.model}")
        
        # Get model info
        model_info = adapter.get_model_info()
        print(f"📊 Model Info: {model_info}")
        print()
        
    except ValueError as e:
        print(f"❌ Failed to initialize GroqAdapter: {e}")
        print("💡 Please ensure GROQ_API_KEY environment variable is set")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return
    
    # Test job analysis scenario
    job_analysis = {
        "title": "Senior Software Engineer - AI/ML",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "React", "JavaScript", "Git"],
        "experience_level": "Senior",
        "company": "Tech Innovation Corp"
    }
    
    print("🎯 Testing Resume Generation with Anti-Hallucination")
    print(f"Target Position: {job_analysis['title']}")
    print(f"Required Skills: {', '.join(job_analysis['required_skills'])}")
    print()
    
    try:
        # Test enhanced resume generation
        print("⏳ Generating resume with fact-checking constraints...")
        resume_content = await adapter.generate_resume_content(
            user_data=user_data,
            job_analysis=job_analysis,
            content_type="resume"
        )
        
        print("✅ Resume Generation Completed")
        print("=" * 40)
        print(resume_content)
        print("=" * 40)
        print()
        
        # Test cover letter generation
        print("⏳ Generating cover letter with fact-checking constraints...")
        cover_letter_content = await adapter.generate_resume_content(
            user_data=user_data,
            job_analysis=job_analysis,
            content_type="cover_letter"
        )
        
        print("✅ Cover Letter Generation Completed")
        print("=" * 40)
        print(cover_letter_content)
        print("=" * 40)
        print()
        
        # Validate fact-checking (basic checks)
        print("🔍 Fact-Checking Validation")
        print("-" * 30)
        
        # Check for user's actual information
        checks = [
            (user_data['full_name'] in resume_content, f"Name '{user_data['full_name']}' present in resume"),
            (user_data['email'] in resume_content, f"Email '{user_data['email']}' present in resume"),
            (any(skill in resume_content for skill in user_data['skills']), "At least one actual skill mentioned"),
            (any(exp['company'] in resume_content for exp in user_data['work_experience']), "At least one actual company mentioned"),
        ]
        
        for passed, description in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {description}")
        
        print()
        print("📈 Usage Statistics")
        usage_stats = adapter.get_usage_stats()
        for key, value in usage_stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_model_comparison():
    """Test different models for comparison."""
    
    print("\n🔬 Model Comparison Test")
    print("=" * 40)
    
    # Test data snippet for quick comparison
    test_snippet = {
        "full_name": "Huy Ky",
        "skills": ["Python", "Machine Learning", "React"],
        "work_experience": [
            {
                "title": "Software Engineering Research Intern",
                "company": "Washington State University",
                "start_date": "2024-01",
                "end_date": "2024-12",
                "description": "AI and VR research"
            }
        ]
    }
    
    job_req = {
        "title": "Python Developer",
        "required_skills": ["Python", "Machine Learning"],
        "experience_level": "Entry"
    }
    
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-90b-text-preview"]
    
    for model in models:
        try:
            print(f"\n🤖 Testing {model}...")
            adapter = GroqAdapter(model=model)
            
            # Simple generation test
            prompt = """Generate a one-sentence professional summary for this person:
Name: Huy Ky
Skills: Python, Machine Learning, React
Experience: Software Engineering Research Intern at WSU (AI and VR research)

CONSTRAINT: Only use the information provided above."""
            
            response = await adapter.generate(prompt, temperature=0.1, max_tokens=100)
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"❌ Failed for {model}: {e}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_groq_adapter())
    asyncio.run(test_model_comparison())