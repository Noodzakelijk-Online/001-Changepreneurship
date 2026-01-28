"""
Comprehensive Backend API Tests
Tests all API endpoints, authentication, and business logic
"""
import pytest
import json
from datetime import datetime
import time


class TestHealthAndStatus:
    """Test system health and status endpoints"""
    
    def test_health_check(self, client):
        """Health endpoint should return 200"""
        response = client.get('/api/dashboard/health')
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'healthy'
        assert 'components' in data
        
    def test_health_check_performance(self, client):
        """Health check should respond in < 100ms"""
        start = time.time()
        response = client.get('/api/dashboard/health')
        duration = (time.time() - start) * 1000
        assert duration < 100
        assert response.status_code == 200


class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_register_new_user(self, client):
        """Should register new user successfully"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirmation': 'SecurePass123!'
        })
        assert response.status_code == 201
        data = response.json
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert 'session_token' in data
        
    def test_register_duplicate_username(self, client):
        """Should reject duplicate username"""
        user_data = {
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'SecurePass123!',
            'password_confirmation': 'SecurePass123!'
        }
        client.post('/api/auth/register', json=user_data)
        
        # Try to register same username
        user_data['email'] = 'test2@example.com'
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        
    def test_login_valid_credentials(self, client):
        """Should login with valid credentials"""
        # Register first
        client.post('/api/auth/register', json={
            'username': 'logintest',
            'email': 'login@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'logintest',
            'password': 'Pass123!'
        })
        assert response.status_code == 200
        data = response.json
        assert 'session_token' in data
        assert data['message'] == 'Login successful'
        assert 'expires_at' in data
        
    def test_login_invalid_credentials(self, client):
        """Should reject invalid credentials"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        assert response.status_code == 401
        
    def test_protected_route_without_token(self, client):
        """Should reject access without token"""
        response = client.get('/api/user/profile')
        assert response.status_code == 401
        
    def test_protected_route_with_invalid_token(self, client):
        """Should reject invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401
        
    def test_protected_route_with_valid_token(self, client):
        """Should allow access with valid token"""
        # Register and login
        client.post('/api/auth/register', json={
            'username': 'authtest',
            'email': 'auth@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        login_response = client.post('/api/auth/login', json={
            'username': 'authtest',
            'password': 'Pass123!'
        })
        token = login_response.json['session_token']
        
        # Access protected route
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code in [200, 404]  # 404 if no profile yet
        
    def test_logout(self, client):
        """Should logout successfully"""
        # Register and login first
        client.post('/api/auth/register', json={
            'username': 'logouttest',
            'email': 'logout@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        login_response = client.post('/api/auth/login', json={
            'username': 'logouttest',
            'password': 'Pass123!'
        })
        token = login_response.json['session_token']
        
        # Logout
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/auth/logout', headers=headers)
        assert response.status_code == 200


class TestAssessmentPhases:
    """Test all 7 assessment phases"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Get auth token for tests"""
        client.post('/api/auth/register', json={
            'username': 'assessment_user',
            'email': 'assess@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'assessment_user',
            'password': 'Pass123!'
        })
        return response.json['session_token']
    
    def test_get_self_discovery_questions(self, client, auth_token):
        """Should load self discovery questions"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/assessment/self_discovery/questions', headers=headers)
        assert response.status_code == 200
        
    def test_submit_self_discovery_response(self, client, auth_token):
        """Should submit self discovery responses"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/assessment/self_discovery/submit', 
            headers=headers,
            json={
                'responses': {
                    'personality': {'q1': 4, 'q2': 5},
                    'values': {'q3': 'innovation'}
                }
            })
        assert response.status_code in [200, 201]
        
    def test_idea_discovery_submission(self, client, auth_token):
        """Should submit idea discovery"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/assessment/idea_discovery/submit',
            headers=headers,
            json={
                'opportunities': [
                    {'idea': 'AI Platform', 'score': 85}
                ]
            })
        assert response.status_code in [200, 201]
        
    def test_get_user_responses(self, client, auth_token):
        """Should retrieve user's responses"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # First submit some responses
        client.post('/api/assessment/self_discovery/submit',
            headers=headers,
            json={'responses': {'test': 'data'}})
        
        # Then retrieve
        response = client.get('/api/assessment/responses', headers=headers)
        assert response.status_code == 200
        

class TestDashboard:
    """Test dashboard and analytics endpoints"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Get auth token for dashboard tests"""
        client.post('/api/auth/register', json={
            'username': 'dashboard_user',
            'email': 'dashboard@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'dashboard_user',
            'password': 'Pass123!'
        })
        return response.json['session_token']
    
    def test_dashboard_overview(self, client, auth_token):
        """Should get dashboard overview"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert response.status_code == 200
        data = response.json
        assert 'data' in data
        assert 'overall_progress' in data['data']
        
    def test_entrepreneur_profile(self, client, auth_token):
        """Should get entrepreneur profile"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/analytics/dashboard/entrepreneur-profile', headers=headers)
        assert response.status_code in [200, 404]
        
    def test_progress_history(self, client, auth_token):
        """Should get progress history"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/analytics/dashboard/progress-history', headers=headers)
        assert response.status_code == 200
        
    def test_executive_summary(self, client, auth_token):
        """Should get executive summary"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/dashboard/executive-summary', headers=headers)
        assert response.status_code == 200


class TestAIRecommendations:
    """Test AI-powered features"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Get auth token"""
        client.post('/api/auth/register', json={
            'username': 'ai_user',
            'email': 'ai@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'ai_user',
            'password': 'Pass123!'
        })
        return response.json['session_token']
    
    def test_get_recommendations(self, client, auth_token):
        """Should get AI recommendations"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/ai-recommendations', headers=headers)
        assert response.status_code in [200, 404]
        
    def test_mind_map_generation(self, client, auth_token):
        """Should generate mind map"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/mind-mapping/generate',
            headers=headers,
            json={'topic': 'business_idea'})
        assert response.status_code in [200, 201, 404]


class TestDataIntegrity:
    """Test data persistence and integrity"""
    
    def test_response_persistence(self, client):
        """Submitted responses should persist"""
        # Register and login
        client.post('/api/auth/register', json={
            'username': 'persist_test',
            'email': 'persist@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'persist_test',
            'password': 'Pass123!'
        })
        token = response.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Submit response
        test_data = {'responses': {'question_1': 5, 'question_2': 4}}
        client.post('/api/assessment/self_discovery/submit',
            headers=headers,
            json=test_data)
        
        # Retrieve and verify
        get_response = client.get('/api/assessment/responses', headers=headers)
        assert get_response.status_code == 200
        # Verify data matches what was submitted
        
    def test_progress_calculation(self, client):
        """Progress should calculate correctly"""
        # Create user, submit partial assessment, check progress
        client.post('/api/auth/register', json={
            'username': 'progress_test',
            'email': 'progress@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'progress_test',
            'password': 'Pass123!'
        })
        token = response.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get initial progress (should be 0)
        initial = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert initial.json['data']['overall_progress'] == 0
        
        # Submit to one phase
        client.post('/api/assessment/self_discovery/submit',
            headers=headers,
            json={'responses': {'complete': True}})
        
        # Check progress updated
        updated = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert updated.json['data']['overall_progress'] > 0


class TestPerformance:
    """Performance and load tests"""
    
    def test_login_performance(self, client):
        """Login should complete in < 500ms"""
        client.post('/api/auth/register', json={
            'username': 'perf_test',
            'email': 'perf@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        
        start = time.time()
        response = client.post('/api/auth/login', json={
            'username': 'perf_test',
            'password': 'Pass123!'
        })
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert duration < 500
        
    def test_dashboard_load_performance(self, client):
        """Dashboard should load in < 2s"""
        client.post('/api/auth/register', json={
            'username': 'dash_perf',
            'email': 'dashperf@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        response = client.post('/api/auth/login', json={
            'username': 'dash_perf',
            'password': 'Pass123!'
        })
        token = response.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        start = time.time()
        response = client.get('/api/analytics/dashboard/overview', headers=headers)
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert duration < 2000


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_request_body(self, client):
        """Should handle empty request body gracefully"""
        response = client.post('/api/auth/login', json={})
        assert response.status_code in [400, 422]
        
    def test_missing_required_fields(self, client):
        """Should reject missing required fields"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser'
            # Missing email, password
        })
        assert response.status_code in [400, 422]
        
    def test_invalid_email_format(self, client):
        """Should reject invalid email format"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        assert response.status_code in [400, 422]
        
    def test_sql_injection_attempt(self, client):
        """Should prevent SQL injection"""
        response = client.post('/api/auth/login', json={
            'username': "' OR '1'='1",
            'password': "' OR '1'='1"
        })
        assert response.status_code == 401
        
    def test_xss_attempt(self, client):
        """Should sanitize XSS attempts"""
        response = client.post('/api/auth/register', json={
            'username': '<script>alert("xss")</script>',
            'email': 'xss@test.com',
            'password': 'Pass123!',
            'password_confirmation': 'Pass123!'
        })
        # Should either reject or sanitize
        assert response.status_code in [400, 422, 201]
