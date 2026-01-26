"""Test profile endpoint with real API calls."""
import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

# Login
print("1. Logging in...")
login_resp = requests.post(f"{BASE_URL}/login", json={
    "username": "sarah_chen_founder",
    "password": "test123"
})
print(f"Login status: {login_resp.status_code}")

if login_resp.status_code == 200:
    data = login_resp.json()
    print(f"Full login response: {json.dumps(data, indent=2)}")
    token = data.get('session_token')  # Fixed: token is at root level
    print(f"Token: {token[:30]}..." if token else "No token!")
    
    # Test profile endpoint
    print("\n2. Testing /profile endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_resp = requests.get(f"{BASE_URL}/profile", headers=headers)
    
    print(f"Profile status: {profile_resp.status_code}")
    print(f"Profile response:\n{json.dumps(profile_resp.json(), indent=2)}")
else:
    print(f"Login failed: {login_resp.json()}")
