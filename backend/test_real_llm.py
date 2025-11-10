#!/usr/bin/env python3
"""
Complete generation test - register user, create profile, test real LLM
"""

import asyncio
import httpx
import random

BASE_URL = "http://localhost:8000"

async def test_full_generation():
    async with httpx.AsyncClient() as client:
        print("🔍 Complete Real LLM Generation Test")
        print("=" * 60)
        
        # Register new user
        user_suffix = random.randint(100000, 999999)
        register_data = {
            "full_name": "John Doe",
            "email": f"test_llm_{user_suffix}@example.com",
            "password": "TestPass123"
        }
        
        print("👤 Registering new user...")
        register_response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        
        if register_response.status_code != 201:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return
        
        user_info = register_response.json()
        print(f"✅ User registered: ID {user_info['user']['id']}")
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        print("🔐 Logging in...")
        login_response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        login_result = login_response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Create profile
        print("📋 Creating profile...")
        profile_data = {
            "personal_info": {
                "full_name": "John Doe",
                "email": register_data["email"],
                "phone": "(555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "https://www.linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe"
            },
            "professional_summary": "Experienced software engineer with 5+ years in backend development, specializing in Python, FastAPI, and cloud technologies. Proven track record of building scalable APIs and integrating AI/ML services.",
            "skills": {
                "technical": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "AWS", "Docker", "Git", "REST APIs", "AI/ML Integration", "Microservices"],
                "soft": ["Team Leadership", "Problem Solving", "Communication", "Project Management"],
                "languages": [
                    {"name": "English", "proficiency": "native"},
                    {"name": "Spanish", "proficiency": "conversational"}
                ],
                "certifications": [
                    {"name": "AWS Solutions Architect", "issuer": "Amazon", "date_obtained": "2023-01-01"},
                    {"name": "Python Certification", "issuer": "Python Institute", "date_obtained": "2022-06-01"}
                ]
            },
            "experiences": [
                {
                    "id": "exp_1",
                    "title": "Senior Backend Engineer",
                    "company": "TechCorp Inc",
                    "location": "San Francisco, CA",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "is_current": True,
                    "description": "Lead backend development for scalable API platform serving 1M+ users.",
                    "achievements": [
                        "Built microservices architecture reducing response time by 40%",
                        "Integrated AI/ML models for intelligent document processing",
                        "Mentored team of 5 junior developers",
                        "Implemented comprehensive testing achieving 90% code coverage"
                    ]
                },
                {
                    "id": "exp_2",
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "location": "Remote",
                    "start_date": "2020-03-01",
                    "end_date": "2021-12-31",
                    "is_current": False,
                    "description": "Developed full-stack applications using Python and React.",
                    "achievements": [
                        "Built RESTful APIs serving 100K+ daily requests",
                        "Optimized database queries improving performance by 60%",
                        "Deployed applications on AWS with CI/CD pipeline"
                    ]
                }
            ],
            "education": [
                {
                    "id": "edu_1",
                    "institution": "University of California, Berkeley",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2016-09-01",
                    "end_date": "2020-05-01",
                    "gpa": 3.7,
                    "honors": ["Cum Laude", "Dean's List"]
                }
            ],
            "projects": [
                {
                    "id": "proj_1",
                    "name": "AI Resume Generator",
                    "description": "Built an AI-powered resume generation platform using FastAPI, SQLAlchemy, and OpenAI API. Features include real-time document processing and ATS optimization.",
                    "technologies": ["Python", "FastAPI", "OpenAI API", "SQLAlchemy", "React"],
                    "url": "https://github.com/johndoe/ai-resume-gen",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-01"
                }
            ]
        }
        
        profile_response = await client.post(f"{BASE_URL}/api/v1/profiles", json=profile_data, headers=headers)
        
        if profile_response.status_code != 201:
            print(f"❌ Profile creation failed: {profile_response.status_code}")
            print(f"Response: {profile_response.text}")
            return
        
        profile = profile_response.json()
        profile_id = profile["id"]
        print(f"✅ Profile created: {profile_id}")
        
        # Get a job to apply to
        print("💼 Getting job posting...")
        jobs_response = await client.get(f"{BASE_URL}/api/v1/jobs/browse?limit=1", headers=headers)
        
        if jobs_response.status_code != 200:
            print(f"❌ Failed to get jobs: {jobs_response.status_code}")
            return
        
        jobs = jobs_response.json()
        if not jobs["results"]:
            print("❌ No jobs available")
            return
        
        job = jobs["results"][0]
        job_id = job["id"]
        print(f"✅ Target job: {job['title']} at {job['company']}")
        print(f"   Job ID: {job_id}")
        
        # Start REAL LLM generation
        print("\n🚀 Starting REAL LLM resume generation...")
        print("   This will use Groq API with your .env GROQ_API_KEY")
        generation_data = {
            "profile_id": profile_id,
            "job_id": job_id,
            "document_type": "resume",
            "options": {
                "template": "modern",
                "length": "one_page",
                "custom_instructions": "Emphasize AI/ML experience, quantify achievements, and optimize for ATS scanning"
            }
        }
        
        generation_response = await client.post(
            f"{BASE_URL}/api/v1/generations/resume", 
            json=generation_data, 
            headers=headers
        )
        
        if generation_response.status_code != 201:
            print(f"❌ Failed to start generation: {generation_response.status_code}")
            print(f"Response: {generation_response.text}")
            return
        
        generation = generation_response.json()
        generation_id = generation["id"]
        print(f"✅ Generation started: {generation_id}")
        
        # Monitor real-time progress
        print("⏳ Real-time progress monitoring...")
        max_attempts = 60  # 60 seconds max for real LLM
        attempt = 0
        
        while attempt < max_attempts:
            await asyncio.sleep(2)  # Check every 2 seconds
            attempt += 1
            
            status_response = await client.get(
                f"{BASE_URL}/api/v1/generations/{generation_id}/status", 
                headers=headers
            )
            
            if status_response.status_code != 200:
                print(f"❌ Failed to get status: {status_response.status_code}")
                break
            
            status = status_response.json()
            progress = status["progress"]["percentage"]
            stage = status.get("stage_name", "Processing")
            stage_desc = status.get("stage_description", "")
            
            print(f"📊 {progress:3d}% - {stage}")
            if stage_desc:
                print(f"    └─ {stage_desc}")
            
            if status["status"] == "completed":
                print("\n🎉 REAL LLM GENERATION COMPLETED!")
                
                # Get the result with real content
                result_response = await client.get(
                    f"{BASE_URL}/api/v1/generations/{generation_id}/result", 
                    headers=headers
                )
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    resume_content = result["result"]["content"]["text"]
                    
                    print("\n" + "="*80)
                    print("📄 REAL LLM-GENERATED RESUME:")
                    print("="*80)
                    print(resume_content)
                    print("="*80)
                    
                    # Save to timestamped file
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"real_llm_resume_{timestamp}.txt"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(resume_content)
                    
                    print(f"\n💾 Resume saved to: {filename}")
                    
                    # Show AI generation metrics
                    result_data = result["result"]
                    print(f"\n📈 AI GENERATION METRICS:")
                    print(f"   ATS Score: {result_data['ats_score']:.1%}")
                    print(f"   Job Match: {result_data['match_percentage']}%")
                    print(f"   Keywords: {result_data['keywords_matched']}/{result_data['keywords_total']} matched")
                    
                    if result_data.get('recommendations'):
                        print(f"\n💡 AI RECOMMENDATIONS:")
                        for i, rec in enumerate(result_data['recommendations'], 1):
                            print(f"   {i}. {rec}")
                    
                    # Show generation stats
                    tokens_used = status.get('tokens_used', 0)
                    gen_time = status.get('generation_time', 0)
                    print(f"\n🔧 GENERATION STATS:")
                    print(f"   Tokens Used: {tokens_used:,}")
                    print(f"   Generation Time: {gen_time:.1f}s")
                    
                    print(f"\n✅ REAL LLM INTEGRATION SUCCESSFUL!")
                    print(f"   - Used Groq API for content generation")
                    print(f"   - Saved resume to {filename}")
                    print(f"   - Generated {len(resume_content):,} characters")
                
                break
                
            elif status["status"] == "failed":
                error_msg = status.get("error_message", "Unknown error")
                print(f"\n❌ Generation failed: {error_msg}")
                break
        
        if attempt >= max_attempts:
            print(f"\n⏰ Generation timeout after {max_attempts * 2} seconds")

if __name__ == "__main__":
    asyncio.run(test_full_generation())