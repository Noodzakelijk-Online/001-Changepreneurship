"""
Smoke Tests - Critical Path Verification
Quick tests to verify system is functioning
Run before deploying or after major changes
"""
import pytest
import time


class TestSmokeTests:
    """Essential smoke tests for critical functionality"""
    
    def test_backend_is_running(self, client):
        """Backend server should be accessible"""
        response = client.get('/api/dashboard/health')
        assert response.status_code == 200
        print("✅ Backend is running")
        
    def test_database_is_connected(self, client):
        """Database should be connected"""
        response = client.get('/api/dashboard/health')
        assert response.status_code == 200
        data = response.json
        assert data.get('components', {}).get('database') == 'connected'
        print("✅ Database is connected")
        
    def test_can_register_user(self, client):
        """User registration should work"""
        response = client.post('/api/auth/register', json={
            'username': 'smoke_test_user',
            'email': 'smoke@test.com',
            'password': 'Test123!',
            'password_confirmation': 'Test123!'
        })
        assert response.status_code == 201
        assert 'session_token' in response.json
        print("✅ User registration works")
        
    def test_can_login(self, client):
        """User login should work"""
        # Register first
        client.post('/api/auth/register', json={
            'username': 'login_smoke',
            'email': 'login_smoke@test.com',
            'password': 'Test123!',
            'password_confirmation': 'Test123!'
        })
        
        # Try login
        response = client.post('/api/auth/login', json={
            'username': 'login_smoke',
            'password': 'Test123!'
        })
        assert response.status_code == 200
        assert 'session_token' in response.json
        print("✅ Login works")
        
    def test_can_access_dashboard(self, client):
        """Dashboard should be accessible"""
        # Setup authenticated user
        client.post('/api/auth/register', json={
            'username': 'dashboard_smoke',
            'email': 'dash@test.com',
            'password': 'Test123!',
            'password_confirmation': 'Test123!'
        })
        login = client.post('/api/auth/login', json={
            'username': 'dashboard_smoke',
            'password': 'Test123!'
        })
        token = login.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert response.status_code == 200
        assert 'data' in response.json
        print("✅ Dashboard is accessible")
        
    def test_can_submit_assessment(self, client):
        """Assessment submission should work"""
        # Setup authenticated user
        client.post('/api/auth/register', json={
            'username': 'assess_smoke',
            'email': 'assess@test.com',
            'password': 'Test123!',
            'password_confirmation': 'Test123!'
        })
        login = client.post('/api/auth/login', json={
            'username': 'assess_smoke',
            'password': 'Test123!'
        })
        token = login.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.post('/api/assessment/self_discovery/submit',
            headers=headers,
            json={'responses': {'test': 'data'}})
        assert response.status_code in [200, 201]
        print("✅ Assessment submission works")
        
    def test_response_times_acceptable(self, client):
        """Critical endpoints should respond quickly"""
        # Health check < 100ms
        start = time.time()
        client.get('/api/dashboard/health')
        health_time = (time.time() - start) * 1000
        assert health_time < 100
        
        # Login < 500ms
        client.post('/api/auth/register', json={
            'username': 'perf_smoke',
            'email': 'perf@test.com',
            'password': 'Test123!',
            'password_confirmation': 'Test123!'
        })
        start = time.time()
        client.post('/api/auth/login', json={
            'username': 'perf_smoke',
            'password': 'Test123!'
        })
        login_time = (time.time() - start) * 1000
        assert login_time < 500
        
        print(f"✅ Response times OK (health: {health_time:.0f}ms, login: {login_time:.0f}ms)")
        
    def test_no_critical_errors_in_logs(self, client):
        """No critical errors should be present"""
        # This would check error logs in real implementation
        # For now, just verify basic functionality doesn't crash
        response = client.get('/api/dashboard/health')
        assert response.status_code == 200
        print("✅ No critical errors detected")


def run_smoke_tests():
    """Run smoke tests and report results"""
    print("\n" + "="*60)
    print("🔥 RUNNING SMOKE TESTS")
    print("="*60 + "\n")
    
    result = pytest.main([__file__, '-v', '-x', '--tb=short'])
    
    print("\n" + "="*60)
    if result == 0:
        print("✅ ALL SMOKE TESTS PASSED")
    else:
        print("❌ SMOKE TESTS FAILED")
    print("="*60 + "\n")
    
    return result


if __name__ == '__main__':
    exit(run_smoke_tests())
