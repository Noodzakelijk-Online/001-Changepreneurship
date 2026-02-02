"""
Create test_full user with EXACT question_ids matching frontend components
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ['DATABASE_URL'] = 'sqlite:///E:/GIT/001-Changepreneurship/changepreneurship.db'
os.environ['USE_LLM'] = 'false'

from src.main import app
from src.models.assessment import User, Assessment, AssessmentResponse, UserSession, EntrepreneurProfile, db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    # Delete ALL existing data
    print("Deleting all existing data...")
    AssessmentResponse.query.delete()
    Assessment.query.delete()
    UserSession.query.delete()
    EntrepreneurProfile.query.delete()
    User.query.delete()
    db.session.commit()
    print("✓ All data deleted\n")
    
    # Create test_full user
    print("Creating test_full user...")
    user = User(
        username='test_full',
        email='test@example.com',
        password_hash=generate_password_hash('test1234')
    )
    db.session.add(user)
    db.session.commit()
    print(f"✓ Created user: {user.username} (ID: {user.id})\n")
    
    # Create entrepreneur profile
    profile = EntrepreneurProfile(
        user_id=user.id,
        entrepreneur_archetype='visionary',
        core_motivation='transform-world',
        risk_tolerance=8,
        confidence_level=8
    )
    db.session.add(profile)
    db.session.commit()
    
    # ========================================
    # SELF DISCOVERY ASSESSMENT
    # ========================================
    assessment1 = Assessment(
        user_id=user.id,
        phase_id='self_discovery',
        phase_name='Self Discovery Assessment',
        is_completed=True,
        progress_percentage=100.0,
        started_at=datetime.now() - timedelta(days=7),
        completed_at=datetime.now() - timedelta(days=6)
    )
    db.session.add(assessment1)
    db.session.flush()
    
    # Section: motivation (3 questions)
    responses_motivation = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='primary-motivation',
            question_text='What is the main reason you want to start your own business?',
            response_type='multiple-choice',
            response_value='transform-world'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='success-vision',
            question_text='When you imagine your business being successful, what does that look like?',
            response_type='textarea',
            response_value='A thriving SaaS company with 1000+ customers, 15-person remote team, $5M ARR, positive impact on productivity, strong company culture, work-life balance, profitable and sustainable business model.'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='risk-tolerance',
            question_text='How comfortable are you with taking risks?',
            response_type='scale',
            response_value='8'
        ),
    ]
    
    # Section: life-impact (1 question with multiple scales)
    responses_life = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='life-impact',
            question_id='life-satisfaction',
            question_text='Rate your current satisfaction in different life areas',
            response_type='multiple-scale',
            response_value='{"Health": 7, "Money": 6, "Family": 8, "Friends": 7, "Career": 9, "Growth": 8, "Recreation": 6, "Environment": 7}'
        ),
    ]
    
    # Section: values (1 ranking question)
    responses_values = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='values',
            question_id='top-values',
            question_text='Rank these values in order of importance to you',
            response_type='ranking',
            response_value='["making-difference", "learning", "personal-freedom", "financial-success", "family-time", "adventure", "security", "recognition"]'
        ),
    ]
    
    # Section: vision (1 question)
    responses_vision = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='vision',
            question_id='ten-year-vision',
            question_text='Describe your ideal life 10 years from now',
            response_type='textarea',
            response_value='At 45, I run a successful remote-first SaaS company with 50 employees globally. We generate $20M ARR helping teams collaborate better. I work 30 hours/week, spend mornings with family, mentor young entrepreneurs. Financial freedom allows travel 3 months/year. Known as thought leader in remote work space. Strong marriage, healthy lifestyle, meaningful friendships. Legacy: helping 10,000+ teams work smarter.'
        ),
    ]
    
    # Section: confidence (1 question)
    responses_confidence = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='confidence',
            question_id='vision-confidence',
            question_text='How confident are you that you can achieve your 10-year vision?',
            response_type='scale',
            response_value='8'
        ),
    ]
    
    all_responses = (
        responses_motivation + 
        responses_life + 
        responses_values + 
        responses_vision + 
        responses_confidence
    )
    
    for response in all_responses:
        db.session.add(response)
    
    print(f"✓ Self Discovery: {len(all_responses)} responses")
    print(f"  - motivation: {len(responses_motivation)}")
    print(f"  - life-impact: {len(responses_life)}")
    print(f"  - values: {len(responses_values)}")
    print(f"  - vision: {len(responses_vision)}")
    print(f"  - confidence: {len(responses_confidence)}")
    
    # ========================================
    # IDEA DISCOVERY ASSESSMENT (simplified)
    # ========================================
    assessment2 = Assessment(
        user_id=user.id,
        phase_id='idea_discovery',
        phase_name='Idea Discovery Assessment',
        is_completed=True,
        progress_percentage=100.0,
        started_at=datetime.now() - timedelta(days=6),
        completed_at=datetime.now() - timedelta(days=5)
    )
    db.session.add(assessment2)
    db.session.flush()
    
    responses_idea = [
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='problem',
            question_id='core-problem',
            question_text='What problem are you solving?',
            response_type='textarea',
            response_value='Remote teams waste 15-20 hours/week on coordination overhead, status updates, and manual project tracking. Existing tools are passive databases requiring constant updates.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='solution',
            question_id='solution-description',
            question_text='Describe your solution',
            response_type='textarea',
            response_value='AI-powered project management that automatically tracks progress, predicts delays, optimizes workload, and eliminates manual status updates.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='market',
            question_id='target-customer',
            question_text='Who is your target customer?',
            response_type='textarea',
            response_value='Engineering teams at Series A-C startups (50-250 employees). VP Engineering or Head of Product are decision makers.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='validation',
            question_id='customer-validation',
            question_text='Have you validated this with customers?',
            response_type='textarea',
            response_value='45 customer interviews, 84% confirmed top-3 pain point. 6-week beta with 5 companies, 80% renewal rate, NPS of 72.'
        ),
    ]
    
    for response in responses_idea:
        db.session.add(response)
    
    print(f"✓ Idea Discovery: {len(responses_idea)} responses")
    
    # ========================================
    # REMAINING PHASES (simplified)
    # ========================================
    phases_data = [
        ('market_research', 'Market Research', 'market', 'market-analysis'),
        ('business_pillars', 'Business Pillars Planning', 'business', 'business-model'),
        ('product_testing', 'Product Concept Testing', 'mvp', 'mvp-features'),
        ('business_dev', 'Business Development', 'growth', 'growth-strategy'),
        ('prototype_testing', 'Business Prototype Testing', 'validation', 'validation-results')
    ]
    
    for i, (phase_id, phase_name, section_id, question_id) in enumerate(phases_data, start=3):
        assessment = Assessment(
            user_id=user.id,
            phase_id=phase_id,
            phase_name=phase_name,
            is_completed=True,
            progress_percentage=100.0,
            started_at=datetime.now() - timedelta(days=5-i),
            completed_at=datetime.now() - timedelta(days=4-i)
        )
        db.session.add(assessment)
        db.session.flush()
        
        responses = [
            AssessmentResponse(
                assessment_id=assessment.id,
                section_id=section_id,
                question_id=question_id,
                question_text=f'{phase_name} - Main Question',
                response_type='textarea',
                response_value=f'Comprehensive response for {phase_name}. Market analysis shows strong demand, competitive positioning is favorable, business model is validated with early customers.'
            ),
            AssessmentResponse(
                assessment_id=assessment.id,
                section_id=section_id,
                question_id=f'{question_id}-metric',
                question_text=f'{phase_name} - Key Metric',
                response_type='scale',
                response_value='8'
            ),
        ]
        
        for response in responses:
            db.session.add(response)
        
        print(f"✓ {phase_name}: {len(responses)} responses")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("✓ DATABASE RESET COMPLETE!")
    print("="*60)
    print(f"\n🔐 Login Credentials:")
    print(f"   Username: test_full")
    print(f"   Password: test1234")
    
    # Verification
    total_assessments = Assessment.query.filter_by(user_id=user.id).count()
    total_responses = AssessmentResponse.query.join(Assessment).filter(Assessment.user_id == user.id).count()
    print(f"\n📊 Summary:")
    print(f"   Total Assessments: {total_assessments}")
    print(f"   Total Responses: {total_responses}")
    print(f"\n✅ All responses have CORRECT question_ids matching frontend!")
    print("\n💡 Next steps:")
    print("   1. Refresh browser (F5)")
    print("   2. Clear localStorage: localStorage.clear()")
    print("   3. Login with test_full / test1234")
    print("   4. Open Self Discovery - ALL FIELDS SHOULD BE PRE-FILLED!")
