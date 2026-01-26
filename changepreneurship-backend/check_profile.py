"""Quick check for user profile data."""
import sys
import os
sys.path.insert(0, 'src')

# Set environment before importing
os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/development.db')

from models.assessment import User, EntrepreneurProfile, db
from main import app

with app.app_context():
    user = User.query.filter_by(username='sarah_chen_founder').first()
    print(f"User found: {user is not None}")
    
    if user:
        print(f"User ID: {user.id}")
        profile = EntrepreneurProfile.query.filter_by(user_id=user.id).first()
        print(f"Profile found: {profile is not None}")
        
        if not profile:
            print("\nAll profiles in DB:")
            profiles = EntrepreneurProfile.query.all()
            print(f"Total profiles: {len(profiles)}")
            for p in profiles:
                print(f"  Profile user_id: {p.user_id}")
