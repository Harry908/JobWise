"""
Setup test account with complete profile data for API testing.

This script creates a test user account and populates it with a complete profile
including experiences, education, and projects. The test account can be used for
live API testing and development.

Usage:
    python setup_test_account.py [--force-new]
    
Options:
    --force-new    Create a new unique test account instead of using existing one
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Load test data
DATA_DIR = Path(__file__).parent / "data"
TEST_USER_FILE = DATA_DIR / "test_user.json"
TEST_PROFILE_FILE = DATA_DIR / "test_profile_create.json"
CREDS_FILE = DATA_DIR / "test_credentials.json"


def load_json_file(filepath):
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def login_existing_user():
    """Login with existing test user credentials."""
    user_data = load_json_file(TEST_USER_FILE)
    
    response = requests.post(
        f"{API_V1}/auth/login",
        json={
            "email": user_data['email'],
            "password": user_data['password']
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Logged in with existing account!")
        print(f"  User ID: {data['user']['id']}")
        print(f"  Email: {data['user']['email']}")
        return data['access_token'], data['user']['id']
    else:
        return None, None


def create_user(force_new=False):
    """Register a new test user account."""
    print("\n" + "="*70)
    print("STEP 1: Creating Test User Account")
    print("="*70)
    
    user_data = load_json_file(TEST_USER_FILE)
    
    # If force_new, create unique credentials
    if force_new:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_data['email'] = f"test_{timestamp}@example.com"
        user_data['username'] = f"testuser_{timestamp}"
        user_data['full_name'] = f"Test User {timestamp}"
    
    print(f"\nUser Data:")
    print(f"  Email: {user_data['email']}")
    print(f"  Username: {user_data['username']}")
    print(f"  Full Name: {user_data['full_name']}")
    
    response = requests.post(
        f"{API_V1}/auth/register",
        json=user_data
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ User created successfully!")
        print(f"  User ID: {data['user']['id']}")
        print(f"  Email: {data['user']['email']}")
        print(f"  Access Token: {data['access_token'][:50]}...")
        return data['access_token'], data['user']['id'], user_data
    elif response.status_code == 409 and not force_new:
        # User already exists, try to login
        print(f"\n⚠️  User already exists, attempting to login...")
        token, user_id = login_existing_user()
        if token:
            return token, user_id, user_data
        else:
            print(f"\n❌ Failed to login with existing credentials")
            return None, None, None
    else:
        print(f"\n❌ Failed to create user: {response.status_code}")
        print(f"  Response: {response.text}")
        return None, None, None


def create_profile(token):
    """Create master profile for the test user, or get existing profile."""
    print("\n" + "="*70)
    print("STEP 2: Creating Master Profile")
    print("="*70)
    
    profile_data = load_json_file(TEST_PROFILE_FILE)
    
    # First, check if user already has a profile
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V1}/profiles/me", headers=headers)
    
    if response.status_code == 200:
        # User already has a profile, use it
        data = response.json()
        print(f"\n✅ Using existing profile!")
        print(f"  Profile ID: {data['id']}")
        print(f"  Name: {data['personal_info']['full_name']}")
        return data['id']
    
    # Extract only profile-level data (no nested experiences/education/projects)
    profile_payload = {
        "personal_info": profile_data["personal_info"],
        "professional_summary": profile_data["professional_summary"],
        "skills": profile_data["skills"]
    }
    
    print(f"\nProfile Data:")
    print(f"  Name: {profile_payload['personal_info']['full_name']}")
    print(f"  Location: {profile_payload['personal_info']['location']}")
    print(f"  Summary: {profile_payload['professional_summary'][:60]}...")
    
    response = requests.post(
        f"{API_V1}/profiles",
        headers=headers,
        json=profile_payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Profile created successfully!")
        print(f"  Profile ID: {data['id']}")
        return data['id']
    else:
        print(f"\n❌ Failed to create profile: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def add_experiences(token, profile_id):
    """Add work experiences to the profile."""
    print("\n" + "="*70)
    print("STEP 3: Adding Work Experiences")
    print("="*70)
    
    profile_data = load_json_file(TEST_PROFILE_FILE)
    experiences = profile_data.get("experiences", [])
    
    if not experiences:
        print("\n⚠️  No experiences to add")
        return
    
    print(f"\nAdding {len(experiences)} experience(s)...")
    
    # Prepare experiences (set id to None for auto-generation)
    experiences_payload = [
        {**exp, "id": None} for exp in experiences
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/profiles/{profile_id}/experiences",
        headers=headers,
        json=experiences_payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Added {len(data)} experience(s)!")
        for i, exp in enumerate(data, 1):
            print(f"  {i}. {exp['title']} at {exp['company']}")
    else:
        print(f"\n❌ Failed to add experiences: {response.status_code}")
        print(f"  Response: {response.text}")


def add_education(token, profile_id):
    """Add education entries to the profile."""
    print("\n" + "="*70)
    print("STEP 4: Adding Education")
    print("="*70)
    
    profile_data = load_json_file(TEST_PROFILE_FILE)
    education = profile_data.get("education", [])
    
    if not education:
        print("\n⚠️  No education to add")
        return
    
    print(f"\nAdding {len(education)} education entry(ies)...")
    
    # Prepare education (set id to None for auto-generation)
    education_payload = [
        {**edu, "id": None} for edu in education
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/profiles/{profile_id}/education",
        headers=headers,
        json=education_payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Added {len(data)} education entry(ies)!")
        for i, edu in enumerate(data, 1):
            print(f"  {i}. {edu['degree']} in {edu['field_of_study']}")
            print(f"     {edu['institution']}")
    else:
        print(f"\n❌ Failed to add education: {response.status_code}")
        print(f"  Response: {response.text}")


def add_projects(token, profile_id):
    """Add projects to the profile."""
    print("\n" + "="*70)
    print("STEP 5: Adding Projects")
    print("="*70)
    
    profile_data = load_json_file(TEST_PROFILE_FILE)
    projects = profile_data.get("projects", [])
    
    if not projects:
        print("\n⚠️  No projects to add")
        return
    
    print(f"\nAdding {len(projects)} project(s)...")
    
    # Prepare projects (set id to None for auto-generation)
    projects_payload = [
        {**proj, "id": None} for proj in projects
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/profiles/{profile_id}/projects",
        headers=headers,
        json=projects_payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Added {len(data)} project(s)!")
        for i, proj in enumerate(data, 1):
            print(f"  {i}. {proj['name']}")
            print(f"     Technologies: {', '.join(proj['technologies'][:3])}...")
    else:
        print(f"\n❌ Failed to add projects: {response.status_code}")
        print(f"  Response: {response.text}")


def add_custom_fields(token, profile_id):
    """Add custom fields to the profile."""
    print("\n" + "="*70)
    print("STEP 6: Adding Custom Fields")
    print("="*70)
    
    profile_data = load_json_file(TEST_PROFILE_FILE)
    custom_fields = profile_data.get("custom_fields", {})
    
    if not custom_fields:
        print("\n⚠️  No custom fields to add")
        return
    
    print(f"\nAdding custom fields...")
    
    # Transform dict to list of {"key": k, "value": v} objects as required by API
    custom_fields_list = [
        {"key": key, "value": value}
        for key, value in custom_fields.items()
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/profiles/{profile_id}/custom-fields",
        headers=headers,
        json={"fields": custom_fields_list}  # API expects List[CustomFieldModel]
    )
    
    if response.status_code == 201:
        print(f"\n✅ Added custom fields!")
        print(f"  Fields: {', '.join(custom_fields.keys())}")
    else:
        print(f"\n❌ Failed to add custom fields: {response.status_code}")
        print(f"  Response: {response.text}")


def verify_profile(token, profile_id):
    """Verify the complete profile was created successfully."""
    print("\n" + "="*70)
    print("STEP 7: Verifying Complete Profile")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_V1}/profiles/{profile_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Profile verification successful!")
        print(f"\nProfile Summary:")
        print(f"  Profile ID: {data['id']}")
        print(f"  User ID: {data['user_id']}")
        print(f"  Full Name: {data['personal_info']['full_name']}")
        print(f"  Email: {data['personal_info']['email']}")
        print(f"  Location: {data['personal_info']['location']}")
        print(f"  Experiences: {len(data['experiences'])} entries")
        print(f"  Education: {len(data['education'])} entries")
        print(f"  Projects: {len(data['projects'])} entries")
        print(f"  Technical Skills: {len(data['skills']['technical'])} skills")
        return True
    else:
        print(f"\n❌ Failed to verify profile: {response.status_code}")
        return False


def save_credentials(token, user_id, profile_id, user_data):
    """Save test account credentials to file for easy access."""
    print("\n" + "="*70)
    print("STEP 8: Saving Test Credentials")
    print("="*70)
    
    credentials = {
        "user_id": user_id,
        "profile_id": profile_id,
        "email": user_data['email'],
        "password": user_data['password'],
        "username": user_data.get('username', 'testuser'),
        "access_token": token,
        "created_at": datetime.now().isoformat(),
        "note": "Test account credentials - DO NOT commit to version control"
    }
    
    with open(CREDS_FILE, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✅ Credentials saved to: {CREDS_FILE}")
    print(f"\n⚠️  IMPORTANT: Add test_credentials.json to .gitignore!")


def main():
    """Main setup workflow."""
    # Check for force-new flag
    force_new = '--force-new' in sys.argv
    
    print("\n" + "="*70)
    print("TEST ACCOUNT SETUP SCRIPT")
    print("="*70)
    print("\nThis script will create a complete test account with:")
    print("  - User account (email, password)")
    print("  - Master profile (personal info, summary, skills)")
    print("  - Work experiences")
    print("  - Education history")
    print("  - Projects")
    print("  - Custom fields")
    print("\nServer: " + BASE_URL)
    if force_new:
        print("Mode: Create NEW unique test account")
    else:
        print("Mode: Use existing account or create if needed")
    print("="*70)
    
    try:
        # Step 1: Create user account
        token, user_id, user_data = create_user(force_new)
        if not token:
            print("\n❌ Setup failed at user creation step")
            return
        
        # Step 2: Create profile
        profile_id = create_profile(token)
        if not profile_id:
            print("\n❌ Setup failed at profile creation step")
            return
        
        # Step 3: Add experiences
        add_experiences(token, profile_id)
        
        # Step 4: Add education
        add_education(token, profile_id)
        
        # Step 5: Add projects
        add_projects(token, profile_id)
        
        # Step 6: Add custom fields
        add_custom_fields(token, profile_id)
        
        # Step 7: Verify complete profile
        if not verify_profile(token, profile_id):
            print("\n⚠️  Profile verification failed")
            return
        
        # Step 8: Save credentials
        save_credentials(token, user_id, profile_id, user_data)
        
        # Final success message
        print("\n" + "="*70)
        print("✅ TEST ACCOUNT SETUP COMPLETE!")
        print("="*70)
        print(f"\nTest Account Details:")
        print(f"  Email: {user_data['email']}")
        print(f"  Password: {user_data['password']}")
        print(f"  User ID: {user_id}")
        print(f"  Profile ID: {profile_id}")
        print(f"\nCredentials saved to: {CREDS_FILE}")
        print(f"\nYou can now use this account for testing!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
