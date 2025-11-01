"""
Database seeding script for test users.
Run this after fresh database initialization to create test users.

Usage:
    python seed_database.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.assessment import db
from src.services.complete_user_generator import CompleteUserGenerator

def seed_database():
    """Seed the database with test users."""
    with app.app_context():
        print("[Seed] Starting database seeding...")
        
        # Check if Sarah Chen already exists
        from src.models.user import User
        existing = User.query.filter_by(username='sarah_chen_founder').first()
        if existing:
            print(f"[Seed] Sarah Chen already exists (ID: {existing.id})")
            print("[Seed] Skipping seed. To recreate, delete the user first.")
            return
        
        # Create Sarah Chen complete test user
        print("[Seed] Creating Sarah Chen test user...")
        generator = CompleteUserGenerator(db.session)
        
        try:
            result = generator.create_complete_user()
            
            if result.get('success'):
                print(f"[Seed] ✓ Successfully created Sarah Chen")
                print(f"[Seed]   Username: sarah_chen_founder")
                print(f"[Seed]   Email: sarah.chen@techvision.io")
                print(f"[Seed]   Password: test123")
                print(f"[Seed]   User ID: {result.get('user_id')}")
                print(f"[Seed]   Completion: {result.get('completion')}")
                print("[Seed] Database seeding complete!")
            else:
                print(f"[Seed] ✗ Failed: {result.get('error')}")
                sys.exit(1)
                
        except Exception as e:
            print(f"[Seed] ✗ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    seed_database()
