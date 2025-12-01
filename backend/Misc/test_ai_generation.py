"""Test AI Generation API endpoints."""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# Load test credentials
with open("data/test_credentials.json") as f:
    creds = json.load(f)
    TOKEN = creds["access_token"]
    PROFILE_ID = creds["profile_id"]

headers = {"Authorization": f"Bearer {TOKEN}"}

print("="*70)
print("AI GENERATION API TEST")
print("="*70)

# Step 1: Create a test job
print("\n1. Creating test job...")
job_data = {
    "title": "Senior Python Developer",
    "company": "Tech Innovations Inc",
    "location": "Seattle, WA",
    "description": "We are seeking a Senior Python Developer with expertise in FastAPI, SQLAlchemy, and cloud technologies. The ideal candidate will have 5+ years of experience building scalable web applications, strong knowledge of async programming, and experience with Docker and Kubernetes.",
    "parsed_keywords": ["Python", "FastAPI", "SQLAlchemy", "AWS", "Docker", "Kubernetes", "async", "microservices"],
    "employment_type": "full_time",
    "remote": True
}

response = requests.post(f"{API_BASE}/jobs", headers=headers, json=job_data)
if response.status_code == 201:
    job = response.json()
    job_id = job["id"]
    print(f"✅ Created job: {job['title']} at {job['company']}")
    print(f"   Job ID: {job_id}")
else:
    print(f"❌ Failed to create job: {response.status_code}")
    print(response.text)
    exit(1)

# Step 2: Create content ranking
print("\n2. Creating content ranking...")
ranking_data = {"job_id": job_id}

response = requests.post(f"{API_BASE}/rankings/create", headers=headers, json=ranking_data)
if response.status_code == 200:
    ranking = response.json()
    print(f"✅ Created ranking!")
    print(f"   Ranked {len(ranking['ranked_experience_ids'])} experiences")
    print(f"   Ranked {len(ranking['ranked_project_ids'])} projects")
    print(f"   Rationale: {ranking['ranking_rationale'][:100]}...")
else:
    print(f"❌ Failed to create ranking: {response.status_code}")
    print(response.text)

# Step 3: Generate resume
print("\n3. Generating resume...")
resume_data = {
    "job_id": job_id,
    "max_experiences": 5,
    "max_projects": 3,
    "include_summary": True
}

response = requests.post(f"{API_BASE}/generations/resume", headers=headers, json=resume_data)
if response.status_code == 200:
    generation = response.json()
    print(f"✅ Generated resume!")
    print(f"   Generation ID: {generation['generation_id']}")
    print(f"   ATS Score: {generation['ats_score']}")
    print(f"   Status: {generation['status']}")
    print(f"\n   Resume Preview (first 500 chars):")
    print(f"   {generation['content_text'][:500]}...")
    
    # Save resume to file
    with open("data/test_resume.txt", "w") as f:
        f.write(generation['content_text'])
    print(f"\n   ✅ Full resume saved to data/test_resume.txt")
else:
    print(f"❌ Failed to generate resume: {response.status_code}")
    print(response.text)

# Step 4: Generate cover letter (with LLM)
print("\n4. Generating cover letter (using LLM)...")
cover_letter_data = {
    "job_id": job_id,
    "company_name": "Tech Innovations Inc",
    "hiring_manager_name": "Sarah Johnson",
    "max_paragraphs": 4
}

response = requests.post(f"{API_BASE}/generations/cover-letter", headers=headers, json=cover_letter_data)
if response.status_code == 200:
    generation = response.json()
    print(f"✅ Generated cover letter!")
    print(f"   Generation ID: {generation['generation_id']}")
    print(f"   ATS Score: {generation['ats_score']}")
    print(f"   Status: {generation['status']}")
    print(f"\n   Cover Letter Preview (first 500 chars):")
    print(f"   {generation['content_text'][:500]}...")
    
    # Save cover letter to file
    with open("data/test_cover_letter.txt", "w") as f:
        f.write(generation['content_text'])
    print(f"\n   ✅ Full cover letter saved to data/test_cover_letter.txt")
else:
    print(f"❌ Failed to generate cover letter: {response.status_code}")
    print(response.text)

# Step 5: Get generation history
print("\n5. Getting generation history...")
response = requests.get(f"{API_BASE}/generations/history?limit=10", headers=headers)
if response.status_code == 200:
    history = response.json()
    print(f"✅ Retrieved {history['total']} generations")
    for gen in history['generations'][:5]:
        print(f"   - {gen['document_type']}: {gen['status']} (ATS: {gen['ats_score']})")
else:
    print(f"❌ Failed to get history: {response.status_code}")
    print(response.text)

print("\n" + "="*70)
print("AI GENERATION API TEST COMPLETE!")
print("="*70)
print("\nGenerated files:")
print("  - data/test_resume.txt")
print("  - data/test_cover_letter.txt")
print("\nAPI Documentation: http://localhost:8000/docs")
