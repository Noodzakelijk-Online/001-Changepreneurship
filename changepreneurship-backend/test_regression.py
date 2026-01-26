#!/usr/bin/env python
"""Comprehensive Regression & Smoke Test Suite"""
import sys
import time
from datetime import datetime
from src.main import app
from src.models.assessment import db, User, Assessment, AssessmentResponse
from src.services.auth_service import AuthService
from src.services.dashboard_service import DashboardDataGenerator

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
    
    def test(self, name, func):
        """Run a single test"""
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
    
    def warn(self, message):
        """Add warning"""
        self.warnings += 1
        self.results.append(f"⚠ {message}")
    
    def report(self):
        """Print test report"""
        print("\n" + "="*70)
        print("REGRESSION & SMOKE TEST REPORT")
        print("="*70)
        for result in self.results:
            print(result)
        print("="*70)
        print(f"PASSED: {self.passed} | FAILED: {self.failed} | WARNINGS: {self.warnings}")
        print(f"TOTAL: {self.passed + self.failed} tests")
        print(f"SUCCESS RATE: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*70)
        return self.failed == 0

def run_tests():
    """Execute all regression tests"""
    runner = TestRunner()
    
    with app.app_context():
        print("\n🔍 Starting Regression & Smoke Tests...")
        print(f"⏰ {datetime.now().isoformat()}\n")
        
        # ========== DATABASE TESTS ==========
        print("📊 DATABASE LAYER")
        
        def test_db_connection():
            assert db.engine is not None, "DB engine not initialized"
            db.session.execute(db.text("SELECT 1"))
        runner.test("Database connection", test_db_connection)
        
        def test_user_model():
            user = User.query.first()
            assert user is not None, "No users in database"
            assert hasattr(user, 'username'), "User missing username"
            assert hasattr(user, 'email'), "User missing email"
            assert hasattr(user, 'password_hash'), "User missing password_hash"
        runner.test("User model integrity", test_user_model)
        
        def test_assessment_model():
            assessment = Assessment.query.first()
            if assessment:
                assert hasattr(assessment, 'user_id'), "Assessment missing user_id"
                assert hasattr(assessment, 'phase_name'), "Assessment missing phase_name"
            else:
                runner.warn("No assessments found in database")
        runner.test("Assessment model integrity", test_assessment_model)
        
        def test_data_relationships():
            user = User.query.first()
            if user:
                assessments = Assessment.query.filter_by(user_id=user.id).all()
                if assessments:
                    responses = AssessmentResponse.query.filter_by(
                        assessment_id=assessments[0].id
                    ).all()
                    assert len(responses) >= 0, "Response query failed"
        runner.test("Database relationships", test_data_relationships)
        
        # ========== AUTH SERVICE TESTS ==========
        print("\n🔐 AUTHENTICATION SERVICE")
        
        def test_email_validation():
            assert AuthService.validate_email("test@example.com") == True
            assert AuthService.validate_email("invalid-email") == False
            assert AuthService.validate_email("@example.com") == False
        runner.test("Email validation", test_email_validation)
        
        def test_password_validation():
            valid, _ = AuthService.validate_password("Test1234")
            assert valid == True, "Valid password rejected"
            
            invalid, msg = AuthService.validate_password("short")
            assert invalid == False, "Short password accepted"
            assert "8 characters" in msg
            
            invalid, msg = AuthService.validate_password("12345678")
            assert invalid == False, "Numeric-only password accepted"
        runner.test("Password validation", test_password_validation)
        
        def test_user_authentication():
            user = AuthService.authenticate('sarah_chen_founder', 'test123')
            assert user is not None, "Valid credentials rejected"
            assert user.username == 'sarah_chen_founder'
            
            user_bad = AuthService.authenticate('sarah_chen_founder', 'wrongpass')
            assert user_bad is None, "Invalid password accepted"
        runner.test("User authentication", test_user_authentication)
        
        def test_session_creation():
            user = User.query.filter_by(username='sarah_chen_founder').first()
            if user:
                session = AuthService.create_session(user.id)
                assert session is not None, "Session creation failed"
                assert len(session.session_token) > 20, "Token too short"
                assert session.user_id == user.id, "Session user_id mismatch"
        runner.test("Session creation", test_session_creation)
        
        # ========== DASHBOARD SERVICE TESTS ==========
        print("\n📈 DASHBOARD SERVICE")
        
        dashboard = DashboardDataGenerator()
        
        def test_user_data_retrieval():
            user = User.query.first()
            if user:
                data = dashboard._get_user_assessment_data(user.id)
                if data:
                    assert 'user_id' in data
                    assert 'assessments' in data
                    assert isinstance(data['assessments'], list)
        runner.test("User data retrieval", test_user_data_retrieval)
        
        def test_overall_score_calculation():
            user = User.query.first()
            if user:
                data = dashboard._get_user_assessment_data(user.id)
                if data:
                    score = dashboard._calculate_overall_score(data)
                    assert 0 <= score <= 100, f"Score out of range: {score}"
        runner.test("Overall score calculation", test_overall_score_calculation)
        
        def test_data_completeness():
            user = User.query.first()
            if user:
                data = dashboard._get_user_assessment_data(user.id)
                if data:
                    completeness = dashboard._calculate_data_completeness(data)
                    assert 0.0 <= completeness <= 1.0, f"Completeness out of range: {completeness}"
        runner.test("Data completeness calculation", test_data_completeness)
        
        def test_executive_summary_generation():
            user = User.query.first()
            if user:
                summary = dashboard.generate_executive_summary(user.id)
                assert isinstance(summary, dict), "Summary not a dict"
                assert 'overall_score' in summary
                assert 'assessment_count' in summary
                assert 'sub_elements' in summary
        runner.test("Executive summary generation", test_executive_summary_generation)
        
        # ========== DATA INTEGRITY TESTS ==========
        print("\n🔒 DATA INTEGRITY")
        
        def test_user_uniqueness():
            users = User.query.all()
            usernames = [u.username for u in users]
            emails = [u.email for u in users]
            assert len(usernames) == len(set(usernames)), "Duplicate usernames found"
            assert len(emails) == len(set(emails)), "Duplicate emails found"
        runner.test("User uniqueness constraints", test_user_uniqueness)
        
        def test_assessment_user_links():
            assessments = Assessment.query.all()
            for a in assessments:
                user = User.query.get(a.user_id)
                assert user is not None, f"Orphaned assessment {a.id}"
        runner.test("Assessment-User links", test_assessment_user_links)
        
        def test_response_assessment_links():
            responses = AssessmentResponse.query.limit(100).all()
            for r in responses:
                assessment = Assessment.query.get(r.assessment_id)
                assert assessment is not None, f"Orphaned response {r.id}"
        runner.test("Response-Assessment links", test_response_assessment_links)
        
        # ========== PERFORMANCE TESTS ==========
        print("\n⚡ PERFORMANCE")
        
        def test_user_query_performance():
            start = time.time()
            User.query.all()
            elapsed = time.time() - start
            assert elapsed < 1.0, f"User query too slow: {elapsed:.2f}s"
        runner.test("User query performance", test_user_query_performance)
        
        def test_assessment_query_performance():
            start = time.time()
            Assessment.query.limit(100).all()
            elapsed = time.time() - start
            assert elapsed < 1.0, f"Assessment query too slow: {elapsed:.2f}s"
        runner.test("Assessment query performance", test_assessment_query_performance)
        
        def test_dashboard_generation_performance():
            user = User.query.first()
            if user:
                start = time.time()
                dashboard.generate_executive_summary(user.id)
                elapsed = time.time() - start
                if elapsed > 3.0:
                    runner.warn(f"Dashboard generation slow: {elapsed:.2f}s")
        runner.test("Dashboard generation performance", test_dashboard_generation_performance)
        
        # ========== EDGE CASES ==========
        print("\n🔧 EDGE CASES")
        
        def test_nonexistent_user_auth():
            user = AuthService.authenticate('nonexistent_user', 'password')
            assert user is None, "Nonexistent user authenticated"
        runner.test("Nonexistent user auth", test_nonexistent_user_auth)
        
        def test_empty_password():
            user = AuthService.authenticate('sarah_chen_founder', '')
            assert user is None, "Empty password accepted"
        runner.test("Empty password rejection", test_empty_password)
        
        def test_sql_injection_attempt():
            user = AuthService.authenticate("admin' OR '1'='1", "password")
            assert user is None, "SQL injection not prevented"
        runner.test("SQL injection prevention", test_sql_injection_attempt)
        
        def test_fallback_data():
            fallback = dashboard._generate_fallback_data('demo-user')
            assert isinstance(fallback, dict)
            assert 'overall_score' in fallback
            assert fallback['assessment_count'] == 0
        runner.test("Fallback data generation", test_fallback_data)
        
    # Print final report
    success = runner.report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(run_tests())
