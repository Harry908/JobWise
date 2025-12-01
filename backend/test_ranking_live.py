"""Test the ranking service with live server."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY0NjI2OTg0LCJ0eXBlIjoiYWNjZXNzIn0.2v8i6zqrqMw_TnFTS-idN5l9pWOv9V6DlEk06-QJ9jA"
PROFILE_ID = "53cac499-04c2-4d21-84a0-f10ed31ce4dc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("=== Testing Integer ID Mapping in Ranking Service ===\n")

# Use the first mock job - Senior Python Backend Developer
job_data = {
    "source": "mock",
    "title": "Senior Python Backend Developer",
    "company": "TechCore Solutions",
    "location": "Seattle, WA",
    "description": "We are seeking a skilled Python Backend Developer to join our engineering team and build robust, scalable server-side applications.",
    "parsed_keywords": ["python", "fastapi", "django", "postgresql", "redis", "docker", "aws"],
    "requirements": [
        "5+ years of experience in backend development using Python",
        "Experience with web frameworks such as Flask or Django",
        "Strong understanding of database management systems"
    ],
    "benefits": ["Competitive salary: $120,000 - $180,000", "Remote work options"],
    "salary_range": "120000-180000",
    "remote": True
}

print("Step 1: Creating job listing...")
response = requests.post(
    f"{BASE_URL}/api/v1/jobs",
    headers=headers,
    json=job_data
)

if response.status_code not in [200, 201]:
    print(f"❌ Failed to create job: {response.status_code}")
    print(response.text)
    exit(1)

job = response.json()
job_id = job["id"]
print(f"✓ Created job with ID: {job_id}\n")

print("Step 2: Triggering ranking (this will send INTEGER IDs to LLM)...")
print("Watch the server logs for:")
print("  - 'Experience integer IDs being sent: [1, 2, 3, ...]'")
print("  - 'Integer-to-UUID mapping: {1: uuid..., 2: uuid...}'")
print("  - 'Ranked integer IDs from LLM: [...]'")
print("  - 'Mapped back to N experience UUIDs'\n")

response = requests.post(
    f"{BASE_URL}/api/v1/rankings/create",
    headers=headers,
    json={
        "profile_id": PROFILE_ID,
        "job_id": job_id
    }
)

if response.status_code != 200:
    print(f"❌ Failed to create ranking: {response.status_code}")
    print(response.text)
    exit(1)

ranking = response.json()
print(f"✓ Created ranking with ID: {ranking['id']}")
print(f"✓ Ranked {len(ranking.get('ranked_experience_ids', []))} experiences")
print(f"✓ Ranked {len(ranking.get('ranked_project_ids', []))} projects\n")

print("Step 3: Fetching ranking details...")
response = requests.get(
    f"{BASE_URL}/api/v1/rankings/job/{job_id}",
    headers=headers
)

if response.status_code == 200:
    ranking_details = response.json()
    print("\n=== Ranking Results ===")
    print(f"Experience IDs (should be UUIDs): {ranking_details.get('ranked_experience_ids', [])[:3]}...")
    print(f"Project IDs (should be UUIDs): {ranking_details.get('ranked_project_ids', [])[:3]}...")
    print("\n✓ Integer mapping test complete!")
    print("\nCheck the server terminal for debug logs showing:")
    print("  1. Integer IDs sent to LLM (1, 2, 3...)")
    print("  2. Mapping dictionaries")
    print("  3. UUID conversion back from integers")
else:
    print(f"❌ Failed to fetch ranking: {response.status_code}")

print("=== Testing Resume Generation ===")
print("Step 4: Generating resume with ranked content...")

response = requests.post(
    f"{BASE_URL}/api/v1/generations/resume",
    headers=headers,
    json={
        "profile_id": PROFILE_ID,
        "job_id": job_id
    }
)

if response.status_code == 200:
    resume = response.json()
    print(f"✓ Generated resume successfully")
    print(f"✓ Resume contains {len(resume.get('content', ''))} characters")
    
    # Show first few lines
    content_lines = resume.get('content', '').split('\n')[:10]
    print("\nFirst 10 lines of resume:")
    for line in content_lines:
        print(f"  {line}")
    print("\n✓ Resume generation test complete!")
else:
    print(f"❌ Failed to generate resume: {response.status_code}")
    print(response.text)
