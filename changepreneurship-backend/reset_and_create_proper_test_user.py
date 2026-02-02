"""
Reset database and create test_full user with CORRECT section_ids matching frontend components
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
    # Delete ALL users and data
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
        core_motivation='impact',
        risk_tolerance=4,
        confidence_level=4
    )
    db.session.add(profile)
    db.session.commit()
    
    # ========================================
    # SELF DISCOVERY ASSESSMENT
    # Frontend expects: motivation, life-impact, values, vision, confidence
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
    
    # Motivation section (3 questions)
    responses_self_discovery = [
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='why_entrepreneur',
            question_text='Why do you want to become an entrepreneur?',
            response_type='text',
            response_value='I want to solve real problems, build innovative products, and create value for customers while having autonomy over my work.'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='passion',
            question_text='What are you most passionate about?',
            response_type='text',
            response_value='Technology, product development, and helping teams work more efficiently.'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='motivation',
            question_id='drive',
            question_text='Rate your entrepreneurial drive',
            response_type='scale',
            response_value='5'
        ),
        
        # Life Impact section (2 questions)
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='life-impact',
            question_id='time_commitment',
            question_text='How much time can you commit?',
            response_type='scale',
            response_value='5'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='life-impact',
            question_id='financial_situation',
            question_text='Describe your financial readiness',
            response_type='text',
            response_value='I have 12 months of savings and can work part-time while building the business.'
        ),
        
        # Values section (2 questions)
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='values',
            question_id='core_values',
            question_text='What are your top 3 values?',
            response_type='text',
            response_value='Integrity, innovation, and customer success.'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='values',
            question_id='decision_making',
            question_text='How do you make important decisions?',
            response_type='text',
            response_value='Data-driven with strong intuition, consulting trusted advisors for critical choices.'
        ),
        
        # Vision section (2 questions)
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='vision',
            question_id='long_term_vision',
            question_text='What is your 5-year vision?',
            response_type='text',
            response_value='Build a profitable SaaS company with 1000+ customers, creating meaningful impact in the remote work space.'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='vision',
            question_id='success_definition',
            question_text='How do you define success?',
            response_type='text',
            response_value='Sustainable business generating $1M+ ARR, happy customers, and positive team culture.'
        ),
        
        # Confidence section (2 questions)
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='confidence',
            question_id='self_belief',
            question_text='Rate your confidence in succeeding',
            response_type='scale',
            response_value='4'
        ),
        AssessmentResponse(
            assessment_id=assessment1.id,
            section_id='confidence',
            question_id='resilience',
            question_text='How resilient are you to setbacks?',
            response_type='scale',
            response_value='5'
        ),
    ]
    
    for response in responses_self_discovery:
        db.session.add(response)
    
    print(f"✓ Self Discovery: {len(responses_self_discovery)} responses")
    
    # ========================================
    # IDEA DISCOVERY ASSESSMENT
    # Frontend expects: problem, solution, market, validation
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
        # Problem section
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='problem',
            question_id='core_problem',
            question_text='What problem are you solving?',
            response_type='text',
            response_value='Remote teams struggle with coordination overhead, wasting 15-20 hours per week on status updates and meetings.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='problem',
            question_id='problem_severity',
            question_text='How severe is this problem?',
            response_type='scale',
            response_value='5'
        ),
        
        # Solution section
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='solution',
            question_id='solution_description',
            question_text='Describe your solution',
            response_type='text',
            response_value='AI-powered project management that automatically tracks progress, predicts delays, and optimizes team workload.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='solution',
            question_id='unique_value',
            question_text='What makes it unique?',
            response_type='text',
            response_value='Proactive AI insights vs passive data entry. Non-invasive integration with existing tools. Built for remote-first teams.'
        ),
        
        # Market section
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='market',
            question_id='target_customer',
            question_text='Who is your target customer?',
            response_type='text',
            response_value='Engineering teams at Series A-C startups (50-250 employees). VP of Engineering or Head of Product decision makers.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='market',
            question_id='market_size',
            question_text='Estimate market size',
            response_type='text',
            response_value='TAM: $6.5B project management software market. SAM: $850M remote collaboration tools. Target $2M ARR in year 2.'
        ),
        
        # Validation section
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='validation',
            question_id='customer_validation',
            question_text='Have you validated this with customers?',
            response_type='text',
            response_value='45 customer interviews, 84% confirmed top-3 pain point. 6-week beta with 5 companies, 4/5 renewed, NPS 72.'
        ),
        AssessmentResponse(
            assessment_id=assessment2.id,
            section_id='validation',
            question_id='willingness_to_pay',
            question_text='Will customers pay for this?',
            response_type='scale',
            response_value='5'
        ),
    ]
    
    for response in responses_idea:
        db.session.add(response)
    
    print(f"✓ Idea Discovery: {len(responses_idea)} responses")
    
    # ========================================
    # REMAINING PHASES (simplified for now)
    # ========================================
    phases_data = [
        ('market_research', 'Market Research', 'market'),
        ('business_pillars', 'Business Pillars Planning', 'business_model'),
        ('product_testing', 'Product Concept Testing', 'mvp'),
        ('business_dev', 'Business Development', 'growth'),
        ('prototype_testing', 'Business Prototype Testing', 'validation')
    ]
    
    for i, (phase_id, phase_name, section_id) in enumerate(phases_data, start=3):
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
        
        # Add 2 sample responses per phase
        responses = [
            AssessmentResponse(
                assessment_id=assessment.id,
                section_id=section_id,
                question_id='q1',
                question_text=f'{phase_name} - Question 1',
                response_type='text',
                response_value=f'Comprehensive answer for {phase_name} question 1'
            ),
            AssessmentResponse(
                assessment_id=assessment.id,
                section_id=section_id,
                question_id='q2',
                question_text=f'{phase_name} - Question 2',
                response_type='scale',
                response_value='4'
            ),
        ]
        
        for response in responses:
            db.session.add(response)
        
        print(f"✓ {phase_name}: {len(responses)} responses")
    
    db.session.commit()
    
    print("\n✓ Database reset complete!")
    print(f"\nLogin credentials:")
    print(f"  Username: test_full")
    print(f"  Password: test1234")
    
    # Verify
    total_assessments = Assessment.query.filter_by(user_id=user.id).count()
    total_responses = AssessmentResponse.query.join(Assessment).filter(Assessment.user_id == user.id).count()
    print(f"\nTotal: {total_assessments} assessments, {total_responses} responses")
