"""Quick test to check API response format."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY0NjI2OTg0LCJ0eXBlIjoiYWNjZXNzIn0.2v8i6zqrqMw_TnFTS-idN5l9pWOv9V6DlEk06-QJ9jA"
PROFILE_ID = "53cac499-04c2-4d21-84a0-f10ed31ce4dc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("Fetching experiences...")
response = requests.get(
    f"{BASE_URL}/api/v1/profiles/{PROFILE_ID}/experiences",
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response type: {type(response.json())}")
print(f"Response:")
print(json.dumps(response.json(), indent=2)[:1000])
