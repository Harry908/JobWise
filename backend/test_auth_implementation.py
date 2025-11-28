"""Test authentication implementation against documentation."""

import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
}


async def test_auth_flow():
    """Test complete authentication flow."""
    print("=" * 80)
    print("AUTHENTICATION API TESTING")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Test 1: Check server health
        print("\n[TEST 1] Checking server health...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            assert response.status_code == 200, "Health check failed"
            print("  [PASS] Server is running")
        except Exception as e:
            print(f"  [FAIL] Server not running: {e}")
            print("\n  Please start the server first:")
            print("  cd backend")
            print("  python -m uvicorn app.main:app --reload")
            return

        # Test 2: Register new user
        print("\n[TEST 2] POST /api/v1/auth/register - Register new user...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=TEST_USER
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
                print(f"  User ID: {data.get('user', {}).get('id')}")
                print(f"  Email: {data.get('user', {}).get('email')}")
                print(f"  Full Name: {data.get('user', {}).get('full_name')}")
                print(f"  Access Token: {data.get('access_token')[:50]}...")
                print(f"  Token Type: {data.get('token_type')}")
                print(f"  Expires In: {data.get('expires_in')}s")

                # Verify required fields
                assert 'access_token' in data, "Missing access_token"
                assert 'refresh_token' in data, "Missing refresh_token"
                assert 'user' in data, "Missing user object"
                assert data['token_type'] == 'Bearer', "Invalid token type"

                access_token = data['access_token']
                refresh_token = data['refresh_token']
                user_id = data['user']['id']

                print("  [PASS] Registration successful")
            elif response.status_code == 409:
                print(f"  [INFO] User already exists, trying login instead")
                # Try login instead
                response = await client.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json={
                        "email": TEST_USER["email"],
                        "password": TEST_USER["password"]
                    }
                )
                data = response.json()
                access_token = data['access_token']
                refresh_token = data['refresh_token']
                user_id = data['user']['id']
                print("  [PASS] Login successful")
            else:
                print(f"  [FAIL] Unexpected status: {response.text}")
                return

        except Exception as e:
            print(f"  [FAIL] {e}")
            return

        # Test 3: Login with existing user
        print("\n[TEST 3] POST /api/v1/auth/login - Login with credentials...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            print(f"  Status: {response.status_code}")
            assert response.status_code == 200, f"Login failed: {response.text}"

            data = response.json()
            print(f"  User ID: {data['user']['id']}")
            print(f"  Email: {data['user']['email']}")
            print(f"  Access Token: {data['access_token'][:50]}...")

            access_token = data['access_token']
            refresh_token = data['refresh_token']

            print("  [PASS] Login successful")
        except Exception as e:
            print(f"  [FAIL] {e}")
            return

        # Test 4: Get current user with token
        print("\n[TEST 4] GET /api/v1/auth/me - Get current user...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"  Status: {response.status_code}")
            assert response.status_code == 200, f"Get user failed: {response.text}"

            data = response.json()
            print(f"  User data: {json.dumps(data, indent=2)}")

            # Verify schema matches documentation
            required_fields = ['id', 'email', 'full_name', 'created_at', 'updated_at']
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            print("  [PASS] User retrieval successful")
        except Exception as e:
            print(f"  [FAIL] {e}")
            return

        # Test 5: Test without token (should fail)
        print("\n[TEST 5] GET /api/v1/auth/me - Test without token (should fail)...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/auth/me")
            print(f"  Status: {response.status_code}")
            assert response.status_code == 401, "Should require authentication"
            print(f"  Error: {response.json()}")
            print("  [PASS] Correctly requires authentication")
        except Exception as e:
            print(f"  [FAIL] {e}")

        # Test 6: Refresh token
        print("\n[TEST 6] POST /api/v1/auth/refresh - Refresh access token...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            print(f"  Status: {response.status_code}")
            assert response.status_code == 200, f"Refresh failed: {response.text}"

            data = response.json()
            print(f"  New Access Token: {data['access_token'][:50]}...")
            print(f"  New Refresh Token: {data['refresh_token'][:50]}...")

            new_access_token = data['access_token']

            # Verify new token works
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )
            assert response.status_code == 200, "New token doesn't work"

            print("  [PASS] Token refresh successful")
        except Exception as e:
            print(f"  [FAIL] {e}")

        # Test 7: Check email availability
        print("\n[TEST 7] GET /api/v1/auth/check-email - Check email availability...")
        try:
            # Check existing email
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/check-email",
                params={"email": TEST_USER["email"]}
            )
            print(f"  Status: {response.status_code}")
            data = response.json()
            print(f"  Existing email '{TEST_USER['email']}': {data}")
            assert data['available'] == False, "Should not be available"

            # Check new email
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/check-email",
                params={"email": "newuser@example.com"}
            )
            data = response.json()
            print(f"  New email 'newuser@example.com': {data}")
            assert data['available'] == True, "Should be available"

            print("  [PASS] Email availability check successful")
        except Exception as e:
            print(f"  [FAIL] {e}")

        # Test 8: Invalid credentials
        print("\n[TEST 8] POST /api/v1/auth/login - Test invalid credentials...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": "WrongPassword123"
                }
            )
            print(f"  Status: {response.status_code}")
            assert response.status_code == 401, "Should reject invalid password"
            print(f"  Error: {response.json()}")
            print("  [PASS] Correctly rejects invalid credentials")
        except Exception as e:
            print(f"  [FAIL] {e}")

        # Test 9: JWT token structure
        print("\n[TEST 9] Verify JWT token structure...")
        try:
            import base64
            # Decode JWT header and payload (without verification)
            parts = access_token.split('.')
            assert len(parts) == 3, "JWT should have 3 parts"

            # Decode header
            header = json.loads(base64.b64decode(parts[0] + '=='))
            print(f"  JWT Header: {header}")
            assert header['typ'] == 'JWT', "Invalid token type"
            assert header['alg'] in ['HS256', 'RS256'], "Invalid algorithm"

            # Decode payload
            payload = json.loads(base64.b64decode(parts[1] + '=='))
            print(f"  JWT Payload: {payload}")
            assert 'sub' in payload, "Missing subject claim"
            assert 'exp' in payload, "Missing expiration claim"

            print("  [PASS] JWT structure valid")
        except Exception as e:
            print(f"  [FAIL] {e}")

        # Test 10: Logout
        print("\n[TEST 10] POST /api/v1/auth/logout - Logout user...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"  Status: {response.status_code}")
            assert response.status_code in [200, 204], f"Logout failed: {response.text}"
            print("  [PASS] Logout successful")
        except Exception as e:
            print(f"  [FAIL] {e}")

        print("\n" + "=" * 80)
        print("AUTHENTICATION TESTING COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    print("\nStarting authentication tests...")
    print("Make sure the server is running: python -m uvicorn app.main:app --reload\n")
    asyncio.run(test_auth_flow())
