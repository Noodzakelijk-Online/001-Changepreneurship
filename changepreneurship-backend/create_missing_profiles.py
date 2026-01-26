"""Create missing EntrepreneurProfile for existing users."""
import sys
import json
sys.path.insert(0, 'src')

from main import app, db
from models.assessment import User, EntrepreneurProfile

def create_missing_profiles():
    """Create EntrepreneurProfile for users that don't have one."""
    with app.app_context():
        users_without_profile = db.session.query(User).outerjoin(EntrepreneurProfile).filter(
            EntrepreneurProfile.id == None
        ).all()
        
        print(f"Found {len(users_without_profile)} users without profiles")
        
        for user in users_without_profile:
            print(f"Creating profile for user {user.id}: {user.username}")
            
            # Create basic profile
            profile = EntrepreneurProfile(
                user_id=user.id,
                entrepreneur_archetype="Tech Innovator",
                core_motivation="Building solutions to real problems",
                risk_tolerance=0.75,
                confidence_level=0.8,
                success_probability=0.72,
                ai_recommendations=json.dumps({
                    "recommendations": [
                        "Focus on customer validation",
                        "Build MVP to test core assumptions",
                        "Establish clear metrics for success"
                    ],
                    "strengths": ["Technical expertise", "Market understanding"],
                    "areas_for_growth": ["Sales and marketing", "Financial planning"]
                })
            )
            
            db.session.add(profile)
        
        db.session.commit()
        print(f"✓ Created {len(users_without_profile)} profiles successfully")

if __name__ == '__main__':
    create_missing_profiles()
