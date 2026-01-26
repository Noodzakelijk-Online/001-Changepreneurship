#!/usr/bin/env python
"""API Endpoint Smoke Tests - HTTP Integration Tests"""
import sys
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

class APITester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.session_token = None
    
    def test(self, name, func):
        """Run API test"""
        try:
            start = time.time()
            func()
            elapsed = (time.time() - start) * 1000
            self.passed += 1
            self.results.append(f"✓ {name} ({elapsed:.0f}ms)")
            return True
        except AssertionError as e:
            self.failed += 1
            self.results.append(f"✗ {name}: {str(e)}")
            return False
        except Exception as e:
            self.failed += 1
            self.results.append(f"✗ {name}: ERROR - {str(e)}")
            return False
    
    def report(self):
        """Print test report"""
        print("\n" + "="*70)
        print("API SMOKE TEST REPORT")
        print("="*70)
        for result in self.results:
            print(result)
        print("="*70)
        print(f"PASSED: {self.passed} | FAILED: {self.failed}")
        print(f"SUCCESS RATE: {(self.passed/(self.passed+self.failed)*100):.1f}%" if (self.passed + self.failed) > 0 else "N/A")
        print("="*70)
        return self.failed == 0

def run_api_tests():
    """Execute API smoke tests"""
    try:
        import requests
    except ImportError:
        print("❌ 'requests' module not installed. Run: pip install requests")
        return 1
    
    tester = APITester()
    
    print("\n🌐 Starting API Smoke Tests...")
    print(f"⏰ {datetime.now().isoformat()}")
    print(f"🎯 Target: {BASE_URL}\n")
    
    # Check if server is running
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print(f"✓ Server is running (Status: {r.status_code})\n")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server not running at {BASE_URL}")
        print("   Start with: python run_dev.py\n")
        return 1
    
    # ========== AUTH ENDPOINTS ==========
    print("🔐 AUTHENTICATION ENDPOINTS")
    
    def test_login_valid():
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "sarah_chen_founder",
            "password": "test123"
        })
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert 'session_token' in data, "No session_token in response"
        assert 'user' in data, "No user in response"
        tester.session_token = data['session_token']
    tester.test("POST /api/auth/login (valid)", test_login_valid)
    
    def test_login_invalid():
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "sarah_chen_founder",
            "password": "wrongpassword"
        })
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    tester.test("POST /api/auth/login (invalid)", test_login_invalid)
    
    def test_login_missing_fields():
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "sarah_chen_founder"
        })
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    tester.test("POST /api/auth/login (missing fields)", test_login_missing_fields)
    
    def test_verify_session():
        if tester.session_token:
            r = requests.get(f"{BASE_URL}/api/auth/verify", headers={
                "Authorization": f"Bearer {tester.session_token}"
            })
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert data.get('valid') == True, "Session not valid"
    tester.test("GET /api/auth/verify", test_verify_session)
    
    def test_profile():
        if tester.session_token:
            r = requests.get(f"{BASE_URL}/api/auth/profile", headers={
                "Authorization": f"Bearer {tester.session_token}"
            })
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert 'user' in data, "No user in profile"
            assert 'profile' in data, "No profile data"
    tester.test("GET /api/auth/profile", test_profile)
    
    # ========== DASHBOARD ENDPOINTS ==========
    print("\n📊 DASHBOARD ENDPOINTS")
    
    def test_executive_summary():
        r = requests.get(f"{BASE_URL}/api/dashboard/executive-summary?user_id=1")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get('success') == True, "Success flag not true"
        assert 'data' in data, "No data in response"
        assert 'overall_score' in data['data'], "No overall_score"
    tester.test("GET /api/dashboard/executive-summary", test_executive_summary)
    
    def test_dashboard_metrics():
        r = requests.get(f"{BASE_URL}/api/dashboard/metrics")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get('success') == True, "Success flag not true"
    tester.test("GET /api/dashboard/metrics", test_dashboard_metrics)
    
    # ========== ERROR HANDLING ==========
    print("\n⚠️  ERROR HANDLING")
    
    def test_404():
        r = requests.get(f"{BASE_URL}/api/nonexistent")
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    tester.test("404 Not Found", test_404)
    
    def test_cors_headers():
        r = requests.options(f"{BASE_URL}/api/auth/login")
        assert r.status_code in [200, 204], f"OPTIONS failed: {r.status_code}"
    tester.test("CORS Preflight (OPTIONS)", test_cors_headers)
    
    def test_invalid_json():
        r = requests.post(f"{BASE_URL}/api/auth/login", 
                         data="invalid json",
                         headers={"Content-Type": "application/json"})
        assert r.status_code in [400, 500], f"Invalid JSON accepted: {r.status_code}"
    tester.test("Invalid JSON handling", test_invalid_json)
    
    # ========== PERFORMANCE ==========
    print("\n⚡ PERFORMANCE")
    
    def test_response_time():
        times = []
        for _ in range(5):
            start = time.time()
            r = requests.get(f"{BASE_URL}/api/dashboard/executive-summary?user_id=1")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            assert r.status_code == 200
        
        avg = sum(times) / len(times)
        assert avg < 500, f"Average response time too high: {avg:.0f}ms"
    tester.test("Response time (avg < 500ms)", test_response_time)
    
    # Logout
    if tester.session_token:
        def test_logout():
            r = requests.post(f"{BASE_URL}/api/auth/logout", headers={
                "Authorization": f"Bearer {tester.session_token}"
            })
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        tester.test("POST /api/auth/logout", test_logout)
    
    return 0 if tester.report() else 1

if __name__ == "__main__":
    sys.exit(run_api_tests())
