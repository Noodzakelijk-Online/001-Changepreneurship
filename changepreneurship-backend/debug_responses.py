"""
Test: Check what responses are returned for test_full user
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from src.main import app

with app.test_client() as client:
    # Login
    login_resp = client.post('/api/auth/login', json={
        'username': 'test_full',
        'password': 'test1234'
    })
    
    token = login_resp.get_json().get('session_token')
    
    # Get phases
    phases_resp = client.get('/api/assessment/phases',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    phases = phases_resp.get_json().get('phases', [])
    first_phase = phases[0]
    
    print(f"\nTesting Phase: {first_phase['name']}")
    print(f"Assessment ID: {first_phase['assessment_id']}")
    print(f"Progress: {first_phase['progress_percentage']}%")
    print()
    
    # Get responses for first assessment
    responses_resp = client.get(
        f"/api/assessment/{first_phase['assessment_id']}/responses",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    responses_data = responses_resp.get_json()
    
    print("RESPONSES ENDPOINT RETURNS:")
    print("-" * 70)
    print(f"Keys: {list(responses_data.keys())}")
    print()
    
    if 'responses' in responses_data:
        print(f"Number of responses: {len(responses_data['responses'])}")
        if responses_data['responses']:
            print("\nFirst response structure:")
            first_resp = responses_data['responses'][0]
            for key, value in first_resp.items():
                print(f"  {key}: {value if len(str(value)) < 50 else str(value)[:47] + '...'}")
    
    print("\n" + "="*70)
    print("CHECKING FRONTEND EXPECTED FORMAT:")
    print("="*70)
    
    # Check sync-all format
    sync_resp = client.get('/api/assessment/sync-all',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    sync_data = sync_resp.get_json()
    
    if 'assessmentData' in sync_data:
        phase_data = sync_data['assessmentData'].get('self_discovery', {})
        print("\nself_discovery phase data from sync-all:")
        print(f"Keys: {list(phase_data.keys())}")
        print(f"responses type: {type(phase_data.get('responses'))}")
        if isinstance(phase_data.get('responses'), dict):
            print(f"responses sections: {list(phase_data.get('responses').keys())}")
            first_section = list(phase_data.get('responses').keys())[0] if phase_data.get('responses') else None
            if first_section:
                print(f"\nSection '{first_section}' has {len(phase_data['responses'][first_section])} items")
                if phase_data['responses'][first_section]:
                    print(f"First item keys: {list(phase_data['responses'][first_section][0].keys())}")
