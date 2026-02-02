"""Check test_full user structure vs sarah_chen"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ['DATABASE_URL'] = 'sqlite:///E:/GIT/001-Changepreneurship/changepreneurship.db'
os.environ['USE_LLM'] = 'false'

from src.main import app
from src.models.assessment import User, Assessment, AssessmentResponse

with app.app_context():
    user = User.query.filter_by(username='test_full').first()
    if not user:
        print("test_full user not found!")
        exit(1)
    
    print(f'=== TEST_FULL USER (ID: {user.id}) ===\n')
    
    assessments = Assessment.query.filter_by(user_id=user.id).order_by(Assessment.id).all()
    print(f'Total Assessments: {len(assessments)}\n')
    
    for assessment in assessments:
        responses = AssessmentResponse.query.filter_by(assessment_id=assessment.id).all()
        print(f'{assessment.phase_name}:')
        print(f'  Assessment ID: {assessment.id}')
        print(f'  Progress: {assessment.progress_percentage}%')
        print(f'  Responses: {len(responses)}')
        
        # Group by section_id
        sections = {}
        for r in responses:
            section = r.section_id or 'general'
            if section not in sections:
                sections[section] = []
            sections[section].append({
                'qid': r.question_id,
                'text': r.question_text[:50] if r.question_text else 'N/A'
            })
        
        print(f'  Sections:')
        for section, questions in sections.items():
            print(f'    {section}: {len(questions)} questions')
            for q in questions:
                print(f'      - {q["qid"]}: {q["text"]}...')
        print()
