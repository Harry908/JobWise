"""Test login with the new test credentials."""

import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000', timeout=10.0) as client:
        try:
            response = await client.post('/api/v1/auth/login', json={
                'email': 'sarah.chen@example.com',
                'password': 'TestPassword123'
            })
            print(f'Login Status: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print('✅ Login successful!')
                user_id = data['user']['id']
                user_email = data['user']['email']
                access_token = data['access_token'][:50] + '...'
                print(f'User ID: {user_id}')
                print(f'Email: {user_email}')
                print(f'Access Token: {access_token}')
                
                # Test getting profile
                token = data['access_token']
                headers = {'Authorization': f'Bearer {token}'}
                profile_response = await client.get('/api/v1/profiles', headers=headers)
                print(f'\nProfile List Status: {profile_response.status_code}')
                if profile_response.status_code == 200:
                    profiles = profile_response.json()
                    print(f'Found {len(profiles)} profiles')
                    if profiles:
                        profile = profiles[0]
                        profile_id = profile['id']
                        full_name = profile['personal_info']['full_name']
                        experiences_count = len(profile['experiences'])
                        projects_count = len(profile['projects'])
                        print(f'Profile ID: {profile_id}')
                        print(f'Full Name: {full_name}')
                        print(f'Experiences: {experiences_count}')
                        print(f'Projects: {projects_count}')
                else:
                    print(f'Profile fetch failed: {profile_response.text}')
            else:
                print(f'Login failed: {response.text}')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_login())