#!/usr/bin/env python3
"""
Test script for upload endpoints using sample files with authentication
"""
import requests
import os

def register_and_login():
    """Register a test user and get authentication token"""
    base_url = "http://localhost:8000"
    
    # Test user data
    user_data = {
        "email": "test_upload@example.com",
        "password": "TestPassword123!",
        "full_name": "Test Upload User"
    }
    
    print("🔐 Registering test user...")
    
    try:
        # Try to register (might fail if user already exists)
        register_response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data)
        
        if register_response.status_code == 201:
            print("✅ User registered successfully")
            tokens = register_response.json()
            return tokens["access_token"]
        elif register_response.status_code == 400 and "already exists" in register_response.text:
            print("ℹ️  User already exists, attempting login...")
            
            # User exists, try to login
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                print("✅ User logged in successfully")
                tokens = login_response.json()
                return tokens["access_token"]
            else:
                print(f"❌ Login failed: {login_response.text}")
                return None
        else:
            print(f"❌ Registration failed: {register_response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Authentication error: {str(e)}")
        return None

def test_resume_upload(auth_token):
    """Test resume upload endpoint"""
    url = "http://localhost:8000/api/v1/preferences/upload-sample-resume"
    
    # Use the sample resume file
    resume_path = "sample_resume.txt"
    
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        return False
    
    print(f"📄 Testing resume upload with file: {resume_path}")
    
    try:
        with open(resume_path, 'rb') as f:
            files = {'file': (resume_path, f, 'text/plain')}
            data = {'is_primary': 'true'}
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Resume upload successful!")
            return True
        else:
            print(f"❌ Resume upload failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception during resume upload: {str(e)}")
        return False

def test_cover_letter_upload(auth_token):
    """Test cover letter upload endpoint"""
    url = "http://localhost:8000/api/v1/preferences/upload-cover-letter"
    
    # Use the sample cover letter file
    cover_letter_path = "sample_cover_letter.txt"
    
    if not os.path.exists(cover_letter_path):
        print(f"❌ Cover letter file not found: {cover_letter_path}")
        return False
    
    print(f"📄 Testing cover letter upload with file: {cover_letter_path}")
    
    try:
        with open(cover_letter_path, 'rb') as f:
            files = {'file': (cover_letter_path, f, 'text/plain')}
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            response = requests.post(url, files=files, headers=headers)
            
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Cover letter upload successful!")
            return True
        else:
            print(f"❌ Cover letter upload failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception during cover letter upload: {str(e)}")
        return False

def main():
    """Run all upload tests"""
    print("🚀 Testing JobWise Upload Endpoints")
    print("=" * 50)
    
    # Get authentication token
    auth_token = register_and_login()
    if not auth_token:
        print("❌ Failed to get authentication token. Cannot proceed with tests.")
        return
    
    # Test resume upload
    print("\n1. Testing Resume Upload")
    print("-" * 30)
    resume_success = test_resume_upload(auth_token)
    
    # Test cover letter upload
    print("\n2. Testing Cover Letter Upload")
    print("-" * 30)
    cover_letter_success = test_cover_letter_upload(auth_token)
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    print(f"Resume Upload: {'✅ PASS' if resume_success else '❌ FAIL'}")
    print(f"Cover Letter Upload: {'✅ PASS' if cover_letter_success else '❌ FAIL'}")
    
    if resume_success and cover_letter_success:
        print("\n🎉 All upload tests passed!")
    else:
        print("\n⚠️  Some upload tests failed. Check logs above.")

if __name__ == "__main__":
    main()