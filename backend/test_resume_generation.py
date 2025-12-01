"""Test resume generation to see actual order."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY0NjI2OTg0LCJ0eXBlIjoiYWNjZXNzIn0.2v8i6zqrqMw_TnFTS-idN5l9pWOv9V6DlEk06-QJ9jA"
PROFILE_ID = "53cac499-04c2-4d21-84a0-f10ed31ce4dc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("="*80)
print("TESTING RESUME GENERATION WITH RANKED EXPERIENCES")
print("="*80)

# Create a Software Engineer job
job_data = {
    "source": "test",
    "title": "Senior Python Backend Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "description": "We need a Senior Python Developer with FastAPI, PostgreSQL, and AWS experience. Strong Python and backend skills required.",
    "requirements": ["5+ years Python", "FastAPI expertise", "PostgreSQL"],
    "parsed_keywords": ["python", "fastapi", "postgresql", "aws"],
    "benefits": ["Remote work"],
    "salary_range": "120000-180000",
    "remote": True
}

print("\n1. Creating job...")
response = requests.post(f"{BASE_URL}/api/v1/jobs", headers=headers, json=job_data)
if response.status_code not in [200, 201]:
    print(f"Failed: {response.status_code}")
    exit(1)

job = response.json()
job_id = job["id"]
print(f"✓ Job created: {job_id}")

print("\n2. Generating resume (this will create ranking automatically)...")
print("   CHECK SERVER LOGS for ranking details\n")

response = requests.post(
    f"{BASE_URL}/api/v1/generations/resume",
    headers=headers,
    json={
        "profile_id": PROFILE_ID,
        "job_id": job_id,
        "max_experiences": 4,
        "max_projects": 3,
        "include_summary": True
    }
)

if response.status_code != 200:
    print(f"Failed: {response.status_code}")
    print(response.text)
    exit(1)

resume = response.json()
print(f"Response keys: {resume.keys() if isinstance(resume, dict) else 'Not a dict'}")
print(f"✓ Resume generated")
if 'id' in resume:
    print(f"  ID: {resume['id']}")
if 'ats_score' in resume:
    print(f"  ATS Score: {resume.get('ats_score', 'N/A')}")

# Display the resume content
print("\n" + "="*80)
print("GENERATED RESUME CONTENT")
print("="*80)
print(resume.get('content_text', 'No content'))

# Now check the ranking that was created
print("\n" + "="*80)
print("CHECKING RANKING ORDER")
print("="*80)

response = requests.get(f"{BASE_URL}/api/v1/rankings/job/{job_id}", headers=headers)
if response.status_code == 200:
    ranking = response.json()
    print(f"\nRanked Experience IDs (in order):")
    for i, exp_id in enumerate(ranking.get('ranked_experience_ids', []), 1):
        print(f"  {i}. {exp_id}")
    
    # Get experience details
    response = requests.get(
        f"{BASE_URL}/api/v1/profiles/{PROFILE_ID}/experiences",
        headers=headers
    )
    if response.status_code == 200:
        exp_data = response.json()
        experiences = exp_data.get('experiences', [])
        exp_map = {exp['id']: exp for exp in experiences}
        
        print(f"\nRanked Experiences (with titles):")
        for i, exp_id in enumerate(ranking.get('ranked_experience_ids', []), 1):
            exp = exp_map.get(exp_id)
            if exp:
                print(f"  {i}. {exp['title']} at {exp['company']}")
            else:
                print(f"  {i}. [NOT FOUND] {exp_id}")
        
        print(f"\n✓ Barista position should be LAST in the ranking above!")
        print(f"✓ Check if the resume content matches this ranking order!")

print("\n" + "="*80)
