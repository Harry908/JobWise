#!/usr/bin/env python3
"""Test script for authentication API endpoints."""

import requests
import json
import sys
import time

def test_auth_flow():
    """Test the complete authentication flow."""
    base_url = "http://localhost:8000/api/v1/auth"

    # Use timestamp to ensure unique email
    timestamp = str(int(time.time()))
    email = f'test-api-{timestamp}@example.com'

    print("🚀 Testing Authentication API Flow")
    print("=" * 50)
    print(f"Using email: {email}")

    try:
        # Step 1: Register user
        print("\n1. Registering user...")
        register_data = {
            'email': email,
            'password': 'SecurePass123',
            'full_name': 'Test API User'
        }

        register_response = requests.post(
            f"{base_url}/register",
            json=register_data
        )

        print(f"   Status: {register_response.status_code}")
        if register_response.status_code == 201:
            user_data = register_response.json()
            user_id = user_data['id']
            print(f"   User ID: {user_id}")
            print(f"   Email: {user_data['email']}")
            print(f"   Verified: {user_data['is_verified']}")
        else:
            print(f"   Error: {register_response.text}")
            return False

        # Step 2: Verify user account
        print("\n2. Verifying user account...")
        verify_response = requests.post(
            f"{base_url}/verify-email/{user_id}"
        )

        print(f"   Status: {verify_response.status_code}")
        if verify_response.status_code != 200:
            print(f"   Error: {verify_response.text}")
            return False

        # Step 3: Login
        print("\n3. Logging in...")
        login_data = {
            'email': email,
            'password': 'SecurePass123'
        }

        login_response = requests.post(
            f"{base_url}/login",
            json=login_data
        )

        print(f"   Status: {login_response.status_code}")
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            print(f"   Token Type: {tokens['token_type']}")
            print(f"   Expires In: {tokens['expires_in']}")
            print(f"   Access Token: {access_token[:50]}...")
        else:
            print(f"   Error: {login_response.text}")
            return False

        # Step 4: Test protected endpoint
        print("\n4. Testing protected endpoint (/me)...")
        headers = {'Authorization': f'Bearer {access_token}'}
        me_response = requests.get(
            f"{base_url}/me",
            headers=headers
        )

        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"   User ID: {user_info['id']}")
            print(f"   Email: {user_info['email']}")
            print(f"   Full Name: {user_info['full_name']}")
            print(f"   Verified: {user_info['is_verified']}")
            print(f"   Active: {user_info['is_active']}")
        else:
            print(f"   Error: {me_response.text}")
            print(f"   Headers sent: {headers}")
            return False

        # Step 5: Test token refresh
        print("\n5. Testing token refresh...")
        refresh_data = {'refresh_token': refresh_token}
        refresh_response = requests.post(
            f"{base_url}/refresh",
            json=refresh_data
        )

        print(f"   Status: {refresh_response.status_code}")
        if refresh_response.status_code == 200:
            new_tokens = refresh_response.json()
            print("   ✅ Token refresh successful")
            print(f"   New access token: {new_tokens['access_token'][:50]}...")
        else:
            print(f"   Error: {refresh_response.text}")
            return False

        print("\n🎉 All tests passed!")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)