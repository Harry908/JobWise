import requests
import json

# Test registration endpoint
url = 'http://localhost:8000/api/v1/auth/register'
data = {
    'email': 'test5@example.com',
    'password': 'TestPass123!',
    'full_name': 'Test User 5'
}

try:
    response = requests.post(url, json=data)
    print(f'Status Code: {response.status_code}')
    print(f'Response Headers: {dict(response.headers)}')
    print(f'Response Body: {response.text}')

    if response.status_code == 201:
        try:
            json_data = response.json()
            print(f'Parsed JSON: {json.dumps(json_data, indent=2)}')
            print(f'Keys in response: {list(json_data.keys())}')
        except Exception as e:
            print(f'Failed to parse JSON: {e}')
    else:
        print(f'Error response: {response.text}')

except Exception as e:
    print(f'Error: {e}')