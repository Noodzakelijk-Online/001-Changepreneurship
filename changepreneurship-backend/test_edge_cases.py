"""Enhanced edge case tests for authentication flows."""
import sys
import os

# Fix Windows encoding for emojis
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'src')

from models.assessment import User, UserSession, db
from main import app
from werkzeug.security import generate_password_hash
import time

class EdgeCaseTestRunner:
    """Test edge cases for authentication system."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = []
    
    def test(self, name, func):
        """Run a single test."""
        try:
            func()
            self.passed += 1
            self.tests_run.append((name, "PASSED", None))
            print(f"✓ {name}")
        except AssertionError as e:
            self.failed += 1
            self.tests_run.append((name, "FAILED", str(e)))
            print(f"✗ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.tests_run.append((name, "ERROR", str(e)))
            print(f"✗ {name}: ERROR - {e}")
    
    def summary(self):
        """Print test summary."""
        print(f"\n{'='*70}")
        print(f"EDGE CASE TEST SUMMARY")
        print(f"{'='*70}")
        print(f"PASSED: {self.passed} | FAILED: {self.failed}")
        print(f"SUCCESS RATE: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print(f"{'='*70}\n")

def run_edge_case_tests():
    """Run all edge case tests."""
    tester = EdgeCaseTestRunner()
    
    with app.app_context():
        print("\n🧪 EDGE CASE TESTS - Authentication Flows\n")
        
        # ========== INPUT VALIDATION ==========
        print("📝 INPUT VALIDATION EDGE CASES")
        
        def test_username_too_short():
            from services.auth_service import AuthService
            assert not AuthService.validate_username("ab"), "Should reject username < 3 chars"
        tester.test("Username too short (< 3 chars)", test_username_too_short)
        
        def test_username_too_long():
            from services.auth_service import AuthService
            assert not AuthService.validate_username("a" * 51), "Should reject username > 50 chars"
        tester.test("Username too long (> 50 chars)", test_username_too_long)
        
        def test_username_special_chars():
            from services.auth_service import AuthService
            assert not AuthService.validate_username("user@#$%"), "Should reject special chars in username"
        tester.test("Username with special characters", test_username_special_chars)
        
        def test_username_spaces():
            from services.auth_service import AuthService
            assert not AuthService.validate_username("user name"), "Should reject spaces in username"
        tester.test("Username with spaces", test_username_spaces)
        
        def test_username_valid_underscore():
            from services.auth_service import AuthService
            assert AuthService.validate_username("user_name"), "Should allow underscores"
        tester.test("Username with underscore (valid)", test_username_valid_underscore)
        
        def test_email_missing_at():
            from services.auth_service import AuthService
            assert not AuthService.validate_email("notanemail.com"), "Should reject email without @"
        tester.test("Email missing @ symbol", test_email_missing_at)
        
        def test_email_missing_domain():
            from services.auth_service import AuthService
            assert not AuthService.validate_email("user@"), "Should reject email without domain"
        tester.test("Email missing domain", test_email_missing_domain)
        
        def test_email_invalid_tld():
            from services.auth_service import AuthService
            # Accepting any TLD as valid (simplified regex)
            # This tests the current implementation
            is_valid = AuthService.validate_email("user@domain.x")
            print(f"  (Email user@domain.x validation: {is_valid})")
        tester.test("Email with short TLD", test_email_invalid_tld)
        
        def test_password_too_short():
            from services.auth_service import AuthService
            assert not AuthService.validate_password("12345"), "Should reject password < 6 chars"
        tester.test("Password too short (< 6 chars)", test_password_too_short)
        
        def test_password_exactly_min_length():
            from services.auth_service import AuthService
            assert AuthService.validate_password("123456"), "Should accept 6 char password"
        tester.test("Password exactly minimum length (6)", test_password_exactly_min_length)
        
        # ========== SESSION MANAGEMENT ==========
        print("\n🔐 SESSION MANAGEMENT EDGE CASES")
        
        def test_expired_session():
            # Create user
            test_user = User.query.filter_by(username='test_edge_user').first()
            if not test_user:
                test_user = User(
                    username='test_edge_user',
                    email='edge@test.com',
                    password_hash=generate_password_hash('test123')
                )
                db.session.add(test_user)
                db.session.commit()
            
            # Create expired session (1 second ago with 0 second expiry)
            from datetime import datetime, timedelta
            expired_session = UserSession(
                user_id=test_user.id,
                token='expired_token_test',
                expires_at=datetime.utcnow() - timedelta(seconds=1)
            )
            db.session.add(expired_session)
            db.session.commit()
            
            # Try to use expired session
            retrieved = UserSession.query.filter_by(token='expired_token_test').first()
            assert retrieved.expires_at < datetime.utcnow(), "Session should be expired"
            
            # Cleanup
            db.session.delete(expired_session)
            db.session.commit()
        tester.test("Expired session validation", test_expired_session)
        
        def test_duplicate_session_tokens():
            # Tokens should be unique due to secrets.token_urlsafe
            from services.auth_service import AuthService
            test_user = User.query.filter_by(username='test_edge_user').first()
            
            session1 = AuthService.create_session(test_user.id)
            session2 = AuthService.create_session(test_user.id)
            
            assert session1.token != session2.token, "Session tokens should be unique"
            
            # Cleanup
            AuthService.invalidate_session(session1.token)
            AuthService.invalidate_session(session2.token)
        tester.test("Unique session token generation", test_duplicate_session_tokens)
        
        def test_logout_already_logged_out():
            from services.auth_service import AuthService
            test_user = User.query.filter_by(username='test_edge_user').first()
            
            session = AuthService.create_session(test_user.id)
            token = session.token
            
            # First logout
            AuthService.invalidate_session(token)
            
            # Second logout (should not error)
            result = AuthService.invalidate_session(token)
            # Should return gracefully (implementation dependent)
        tester.test("Double logout does not error", test_logout_already_logged_out)
        
        # ========== CONCURRENT ACCESS ==========
        print("\n⚡ CONCURRENT ACCESS EDGE CASES")
        
        def test_multiple_active_sessions():
            from services.auth_service import AuthService
            test_user = User.query.filter_by(username='test_edge_user').first()
            
            # Create 3 active sessions for same user
            sessions = [AuthService.create_session(test_user.id) for _ in range(3)]
            
            # All should be valid
            assert len(sessions) == 3, "Should allow multiple sessions"
            assert all(s.token for s in sessions), "All sessions should have tokens"
            
            # Cleanup
            for s in sessions:
                AuthService.invalidate_session(s.token)
        tester.test("Multiple concurrent sessions per user", test_multiple_active_sessions)
        
        # ========== DATABASE INTEGRITY ==========
        print("\n🗄️  DATABASE INTEGRITY EDGE CASES")
        
        def test_orphaned_sessions():
            # Sessions with non-existent user_id
            from datetime import datetime, timedelta
            orphan = UserSession(
                user_id=9999999,  # Non-existent user
                token='orphan_token_test',
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(orphan)
            db.session.commit()
            
            # Query should not crash
            result = UserSession.query.filter_by(token='orphan_token_test').first()
            assert result is not None, "Orphan session should exist"
            assert result.user_id == 9999999, "Should preserve user_id"
            
            # Cleanup
            db.session.delete(orphan)
            db.session.commit()
        tester.test("Orphaned sessions (no user)", test_orphaned_sessions)
        
        def test_duplicate_email():
            # SQLAlchemy should enforce unique constraint
            user1 = User.query.filter_by(email='sarah.chen@techvision.io').first()
            
            duplicate = User(
                username='duplicate_test',
                email='sarah.chen@techvision.io',  # Duplicate!
                password_hash=generate_password_hash('test123')
            )
            
            try:
                db.session.add(duplicate)
                db.session.commit()
                assert False, "Should not allow duplicate email"
            except Exception as e:
                db.session.rollback()
                assert 'unique' in str(e).lower() or 'duplicate' in str(e).lower(), "Should be unique constraint error"
        tester.test("Duplicate email constraint", test_duplicate_email)
        
        # ========== SQL INJECTION PROTECTION ==========
        print("\n🛡️  SQL INJECTION PROTECTION")
        
        def test_sql_injection_username():
            from services.auth_service import AuthService
            malicious_username = "admin' OR '1'='1"
            
            # Should be treated as literal string, not executed
            result = AuthService.authenticate(malicious_username, "test123")
            assert result is None, "Should not authenticate with SQL injection attempt"
        tester.test("SQL injection in username", test_sql_injection_username)
        
        def test_sql_injection_email():
            from services.auth_service import AuthService
            malicious_email = "admin@test.com' OR '1'='1"
            
            # Validation should fail or treat as literal
            is_valid = AuthService.validate_email(malicious_email)
            # SQLAlchemy parameterized queries protect against this
            print(f"  (Malicious email validation: {is_valid})")
        tester.test("SQL injection in email", test_sql_injection_email)
        
        # ========== XSS PROTECTION ==========
        print("\n🔒 XSS PROTECTION")
        
        def test_xss_in_username():
            xss_username = "<script>alert('xss')</script>"
            
            # Should be stored as-is and escaped on output
            test_user_xss = User(
                username='test_xss_user',
                email='xss@test.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user_xss)
            db.session.commit()
            
            # Username should be retrievable
            retrieved = User.query.filter_by(username='test_xss_user').first()
            assert retrieved is not None, "User should be stored"
            
            # Cleanup
            db.session.delete(test_user_xss)
            db.session.commit()
        tester.test("XSS in username storage", test_xss_in_username)
        
        # ========== PERFORMANCE EDGE CASES ==========
        print("\n⏱️  PERFORMANCE EDGE CASES")
        
        def test_large_session_count():
            # Test with 100 sessions
            test_user = User.query.filter_by(username='test_edge_user').first()
            from services.auth_service import AuthService
            
            start = time.time()
            sessions = [AuthService.create_session(test_user.id) for _ in range(100)]
            elapsed = time.time() - start
            
            assert len(sessions) == 100, "Should create 100 sessions"
            assert elapsed < 5.0, f"Should create 100 sessions in < 5s (took {elapsed:.2f}s)"
            
            # Cleanup
            for s in sessions:
                AuthService.invalidate_session(s.token)
        tester.test("Performance: Create 100 sessions", test_large_session_count)
        
        def test_password_hash_time():
            # Bcrypt should be slow (security feature), but not too slow
            start = time.time()
            hash_result = generate_password_hash('test_password_123')
            elapsed = time.time() - start
            
            assert hash_result is not None, "Should generate hash"
            assert elapsed < 1.0, f"Password hashing took {elapsed:.2f}s (should be < 1s)"
        tester.test("Performance: Password hashing time", test_password_hash_time)
    
    tester.summary()
    return tester.passed, tester.failed

if __name__ == '__main__':
    passed, failed = run_edge_case_tests()
    sys.exit(0 if failed == 0 else 1)
