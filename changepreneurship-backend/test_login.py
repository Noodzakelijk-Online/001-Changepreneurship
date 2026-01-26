#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test login functionality"""

from src.main import app
from src.models.assessment import User
from werkzeug.security import check_password_hash

with app.app_context():
    # Test 1: Find user
    user = User.query.filter_by(username='sarah_chen_founder').first()
    print(f"[TEST 1] User found: {user is not None}")
    
    if user:
        print(f"  - User ID: {user.id}")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Password hash length: {len(user.password_hash)}")
        
        # Test 2: Password verification
        password_correct = check_password_hash(user.password_hash, 'test123')
        print(f"\n[TEST 2] Password 'test123' correct: {password_correct}")
        
        # Test 3: Try wrong password
        wrong_password = check_password_hash(user.password_hash, 'wrongpass')
        print(f"[TEST 3] Wrong password rejected: {not wrong_password}")
        
        # Test 4: Try to call to_dict
        try:
            user_dict = user.to_dict()
            print(f"\n[TEST 4] user.to_dict() successful")
            print(f"  Keys: {list(user_dict.keys())}")
        except Exception as e:
            print(f"\n[TEST 4] user.to_dict() FAILED: {e}")
    else:
        print("  - User NOT found in database!")
