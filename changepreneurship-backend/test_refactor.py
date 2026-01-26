#!/usr/bin/env python
"""Quick test of refactored code"""
from src.main import app
from src.services.auth_service import AuthService
from src.models.assessment import User

with app.app_context():
    print("[TEST] AuthService loaded:", AuthService)
    print("[TEST] Testing authentication...")
    
    user = AuthService.authenticate('sarah_chen_founder', 'test123')
    if user:
        print(f"[TEST] ✓ Auth successful: {user.username}")
        
        session = AuthService.create_session(user.id)
        print(f"[TEST] ✓ Session created: {session.session_token[:16]}...")
    else:
        print("[TEST] ✗ Auth failed")
