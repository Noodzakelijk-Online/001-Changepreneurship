#!/usr/bin/env python3
"""Create sarah_chen_founder test user with complete data."""
import os
os.environ['DATABASE_URL'] = 'sqlite:///E:/GIT/001-Changepreneurship/changepreneurship.db'

from src.main import app, db
from src.models.assessment import User, Assessment, AssessmentResponse
from werkzeug.security import generate_password_hash

with app.app_context():
    # Delete existing user
    existing = User.query.filter_by(username='sarah_chen_founder').first()
    if existing:
        AssessmentResponse.query.join(Assessment).filter(Assessment.user_id == existing.id).delete(synchronize_session=False)
        Assessment.query.filter_by(user_id=existing.id).delete()
        db.session.delete(existing)
        db.session.commit()
        print("✓ Deleted existing user")
    
    # Create user
    user = User(
        username='sarah_chen_founder',
        email='sarah@test.com',
        password_hash=generate_password_hash('Test1234!')
    )
    db.session.add(user)
    db.session.commit()
    
    # Create Self Discovery assessment
    self_disc = Assessment(
        user_id=user.id,
        phase_id='self-discovery',
        phase_name='Self Discovery',
        is_completed=True,
        progress_percentage=100
    )
    db.session.add(self_disc)
    db.session.commit()
    
    # Add responses
    responses_data = [
        ('core_motivation', 'primary-motivation', 'What drives you?', 'multiple_choice', 'financial-freedom'),
        ('vision', 'success-vision', 'Your vision of success', 'text', 'Building a billion-dollar AI company'),
        ('risk', 'risk-tolerance', 'Risk tolerance', 'scale', '8'),
        ('life_impact', 'life-satisfaction', 'Life satisfaction', 'matrix', '{"career": 9, "health": 7, "relationships": 8}'),
        ('values', 'top-values', 'Top values', 'multiple_choice', '["innovation", "impact", "growth"]'),
    ]
    
    for section, qid, qtext, rtype, val in responses_data:
        resp = AssessmentResponse(
            assessment_id=self_disc.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
    
    # Create Idea Discovery assessment
    idea_disc = Assessment(
        user_id=user.id,
        phase_id='idea-discovery',
        phase_name='Idea Discovery',
        is_completed=True,
        progress_percentage=100
    )
    db.session.add(idea_disc)
    db.session.commit()
    
    idea_responses = [
        ('vision', 'ten-year-vision', '10 year vision', 'text', 'Leading AI revolution with autonomous agents'),
        ('problems', 'problem-experiences', 'Problems experienced', 'text', 'People waste time on repetitive tasks'),
        ('confidence', 'vision-confidence', 'Vision confidence', 'scale', '9'),
    ]
    
    for section, qid, qtext, rtype, val in idea_responses:
        resp = AssessmentResponse(
            assessment_id=idea_disc.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
    
    db.session.commit()
    
    print("\n✅ USER CREATED:")
    print(f"   Username: sarah_chen_founder")
    print(f"   Password: Test1234!")
    print(f"   User ID: {user.id}")
    print(f"   Total Responses: {len(list(self_disc.responses) + list(idea_disc.responses))}")
    print(f"   Self Discovery: {len(self_disc.responses)} responses")
    print(f"   Idea Discovery: {len(idea_disc.responses)} responses")
    print("\n🎯 Ready for AI testing!")
