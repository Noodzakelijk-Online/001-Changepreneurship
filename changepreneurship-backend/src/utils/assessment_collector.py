"""
Assessment Data Collector
-------------------------
Single source of truth for loading a user's full assessment state
(phases + responses grouped by phase_id) from the database.

Used by:
  - ai_routes.py  (insights-report endpoint)
  - ai_recommendations.py  (recommendations endpoints)
"""
from ..models.assessment import Assessment, AssessmentResponse


def collect_assessment_data(user_id: int) -> dict:
    """
    Load all assessments and responses for *user_id*.

    Returns:
        {
            'phases': [{'id', 'name', 'progress', 'completed'}, ...],
            'responses': { phase_id: [{'question_id', 'section_id',
                                       'question_text', 'response_value',
                                       'response_type'}, ...] }
        }
    """
    assessments = Assessment.query.filter_by(user_id=user_id).all()

    phases = [
        {
            'id': a.phase_id,
            'name': a.phase_name,
            'progress': a.progress_percentage,
            'completed': a.is_completed,
        }
        for a in assessments
    ]

    responses_by_phase: dict = {}
    if assessments:
        assessment_ids = [a.id for a in assessments]
        all_responses = AssessmentResponse.query.filter(
            AssessmentResponse.assessment_id.in_(assessment_ids)
        ).all()

        aid_to_phase = {a.id: a.phase_id for a in assessments}

        for r in all_responses:
            pid = aid_to_phase.get(r.assessment_id)
            if pid:
                responses_by_phase.setdefault(pid, []).append({
                    'question_id': r.question_id,
                    'section_id': r.section_id,
                    'question_text': r.question_text or r.question_id,
                    'response_value': r.get_response_value(),
                    'response_type': r.response_type,
                })

    return {'phases': phases, 'responses': responses_by_phase}
