"""
Database seeding script for development
Creates demo user with complete assessment data
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from src.main import app
from src.models.assessment import db, User, Assessment, AssessmentResponse, EntrepreneurProfile
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_demo_user():
    """Create demo user with completed assessments"""
    with app.app_context():
        # Remove existing demo user
        existing = User.query.filter_by(username='demo').first()
        if existing:
            Assessment.query.filter_by(user_id=existing.id).delete()
            EntrepreneurProfile.query.filter_by(user_id=existing.id).delete()
            db.session.delete(existing)
            db.session.commit()
            print("Removed existing demo user")
        
        # Create demo user
        user = User(
            username='demo',
            email='demo@test.com',
            password_hash=generate_password_hash('demo123'),
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        db.session.add(user)
        db.session.flush()
        
        # Create entrepreneur profile
        profile = EntrepreneurProfile(user_id=user.id)
        db.session.add(profile)
        
        print(f"Created user: {user.username}")
        
        # Create completed assessments
        phases = [
            ('self_discovery', 'Self Discovery'),
            ('idea_discovery', 'Idea Discovery'),
            ('market_validation', 'Market Validation'),
            ('business_model', 'Business Model'),
            ('financial_planning', 'Financial Planning'),
            ('execution_roadmap', 'Execution Roadmap'),
            ('resilience_mindset', 'Resilience & Mindset')
        ]
        
        for i, (phase_id, phase_name) in enumerate(phases):
            assessment = Assessment(
                user_id=user.id,
                phase_id=phase_id,
                phase_name=phase_name,
                progress_percentage=100.0,
                is_completed=True,
                started_at=datetime.utcnow() - timedelta(days=30-i*4),
                completed_at=datetime.utcnow() - timedelta(days=29-i*4)
            )
            db.session.add(assessment)
            db.session.flush()
            
            # Add sample responses
            for j in range(5):
                response = AssessmentResponse(
                    assessment_id=assessment.id,
                    section_id=f'section_{j}',
                    question_id=f'question_{j}',
                    question_text=f'Sample question {j+1} for {phase_name}',
                    response_type='text',
                    response_value=f'Detailed answer for question {j+1} in {phase_name}. This response provides sufficient context for AI analysis and recommendations.'
                )
                db.session.add(response)
            
            print(f"  ✓ {phase_name}: {assessment.progress_percentage}% complete")
        
        db.session.commit()
        
        print(f"\n✅ Demo user created successfully!")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Email: demo@test.com")
        print(f"   Assessments: 7/7 completed (100%)")
        print(f"   Total responses: 35\n")

if __name__ == "__main__":
    seed_demo_user()
