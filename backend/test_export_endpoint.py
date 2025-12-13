"""Test export endpoint directly to see the error."""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login first
login_data = {
    "username": "anakin.skywalker@tatooine.galaxy",
    "password": "Password123!"
}

print("Logging in...")
login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get generations to find a generation_id
print("\nGetting generations...")
gens_response = requests.get(
    f"{BASE_URL}/generations/history",
    headers=headers,
    params={"limit": 1}
)
print(f"Generations status: {gens_response.status_code}")

if gens_response.status_code != 200:
    print(f"Failed to get generations: {gens_response.text}")
    exit(1)

generations = gens_response.json()["generations"]
if not generations:
    print("No generations found")
    exit(1)

generation_id = generations[0]["id"]
print(f"Using generation_id: {generation_id}")

# Try to export to PDF
print("\nExporting to PDF...")
export_data = {
    "generation_id": generation_id,
    "template": "modern",
    "format": "pdf",
}

export_response = requests.post(
    f"{BASE_URL}/exports/pdf",
    headers=headers,
    json=export_data
)

print(f"Export status: {export_response.status_code}")
print(f"Export response: {export_response.text}")

if export_response.status_code == 200:
    print("\n✓ Export successful!")
    print(json.dumps(export_response.json(), indent=2))
else:
    print(f"\n✗ Export failed!")
    try:
        error = export_response.json()
        print(json.dumps(error, indent=2))
    except:
        print(export_response.text)
