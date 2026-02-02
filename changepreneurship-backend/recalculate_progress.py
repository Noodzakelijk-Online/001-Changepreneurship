"""Recalculate progress_percentage for all assessments based on responses"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.assessment import db, Assessment, AssessmentResponse
from src.main import app

def recalculate_all_progress():
    """Recalculate progress for all assessments"""
    with app.app_context():
        assessments = Assessment.query.all()
        
        for assessment in assessments:
            # Count responses
            response_count = AssessmentResponse.query.filter_by(
                assessment_id=assessment.id
            ).count()
            
            # Estimate progress based on responses
            # Most phases have 7-10 questions
            expected_questions = {
                'self_discovery': 7,
                'idea_discovery': 8,
                'market_research': 5,
                'business_pillars': 6,
                'product_concept_testing': 3,
                'business_development': 4,
                'business_prototype_testing': 3
            }
            
            expected = expected_questions.get(assessment.phase_id, 7)
            progress = min(100, round((response_count / expected) * 100))
            
            old_progress = assessment.progress_percentage
            assessment.progress_percentage = progress
            
            if response_count >= expected and not assessment.is_completed:
                assessment.is_completed = True
            
            print(f"Assessment {assessment.id} ({assessment.phase_id}): "
                  f"{response_count} responses, "
                  f"progress {old_progress}% -> {progress}%, "
                  f"completed: {assessment.is_completed}")
        
        db.session.commit()
        print("\n✅ Progress recalculated for all assessments")

if __name__ == '__main__':
    recalculate_all_progress()
