"""Quick single job test to see LLM prompt and response."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY0NjI2OTg0LCJ0eXBlIjoiYWNjZXNzIn0.2v8i6zqrqMw_TnFTS-idN5l9pWOv9V6DlEk06-QJ9jA"
PROFILE_ID = "53cac499-04c2-4d21-84a0-f10ed31ce4dc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("Creating Software Engineer job...")
job_data = {
    "source": "test",
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "location": "Remote",
    "description": "We need a Senior Python Developer with FastAPI, PostgreSQL, and AWS experience. You'll build REST APIs, design microservices, and work with Docker/Kubernetes. Strong Python skills required.",
    "requirements": [
        "5+ years Python experience",
        "FastAPI or Django expertise",
        "PostgreSQL database skills",
        "AWS cloud experience"
    ],
    "parsed_keywords": ["python", "fastapi", "postgresql", "aws", "docker"],
    "benefits": ["Remote work"],
    "salary_range": "120000-180000",
    "remote": True
}

response = requests.post(
    f"{BASE_URL}/api/v1/jobs",
    headers=headers,
    json=job_data
)

if response.status_code not in [200, 201]:
    print(f"Failed: {response.status_code}")
    exit(1)

job = response.json()
job_id = job["id"]
print(f"✓ Created job: {job_id}\n")

print("Creating ranking...")
print("CHECK SERVER LOGS NOW for:")
print("  - Full prompt being sent to LLM")
print("  - Raw LLM response")
print("  - Experience details\n")

response = requests.post(
    f"{BASE_URL}/api/v1/rankings/create",
    headers=headers,
    json={
        "profile_id": PROFILE_ID,
        "job_id": job_id
    }
)

if response.status_code == 200:
    ranking = response.json()
    print(f"✓ Ranking created: {ranking['id']}")
    print(f"  Experience IDs: {ranking.get('ranked_experience_ids', [])}")
    print(f"  Keyword matches: {ranking.get('keyword_matches', {})}")
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
