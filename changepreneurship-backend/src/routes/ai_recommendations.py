"""
AI Recommendations API Routes
Provides endpoints for personalized AI-driven recommendations.

Primary path: powered by InsightsReportService (Groq llama-3.3-70b-versatile).
Fallback:     rule-based AIRecommendationsEngine if LLM call fails.

Security: all routes require authentication via verify_session_token().
          Users may only access their own recommendations.
"""
import logging

from flask import Blueprint, request, jsonify

from ..services.ai_recommendations_service import AIRecommendationsEngine
from ..services.insights_report_service import InsightsReportService
from ..models.assessment import Assessment, AssessmentResponse
from ..utils.auth import verify_session_token

logger = logging.getLogger(__name__)
ai_recommendations_bp = Blueprint('ai_recommendations', __name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _collect_assessment_data(user) -> dict:
    """Collect full assessment data needed by InsightsReportService."""
    assessments = Assessment.query.filter_by(user_id=user.id).all()

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


def _map_report_to_recommendations(report: dict, user_id: int) -> dict:
    """Extract recommendations-shaped payload from a full InsightsReport."""
    ent = report.get('entrepreneur', {})
    alignment = report.get('alignment', {})

    strengths = [
        {
            'title': s['name'],
            'description': '',
            'impact': 'High',
            'score': s.get('score', 0),
            'icon': 'brain',
        }
        for s in ent.get('strengths', [])
    ]

    gaps = [
        {
            'title': g['name'],
            'description': '',
            'priority': 'High',
            'score': g.get('score', 0),
            'icon': 'alert-circle',
        }
        for g in ent.get('growth_areas', [])
    ]

    recommendations = [
        {
            'category': ss.get('relation', ''),
            'title': f"{ss.get('ent_dim', '')} × {ss.get('ven_dim', '')}",
            'description': ss.get('insight', ''),
            'priority': 'High',
            'timeframe': '1-2 months',
        }
        for ss in alignment.get('sweet_spots', [])
    ]

    risks = [
        {
            'title': rz.get('relation', 'Risk'),
            'description': rz.get('insight', ''),
            'action': rz.get('action', ''),
            'priority': 'Critical',
        }
        for rz in alignment.get('risk_zones', [])
    ]

    next_steps = [
        {'title': rz.get('action', ''), 'priority': 'High'}
        for rz in alignment.get('risk_zones', [])
        if rz.get('action')
    ]

    return {
        'user_id': user_id,
        'founder_profile': {
            'archetype': ent.get('archetype', 'Founder'),
            'score': ent.get('score', 0),
            'tagline': ent.get('tagline', ''),
        },
        'success_probability': {
            'score': alignment.get('combined_score', ent.get('score', 0)),
            'category': 'AI-Analyzed',
        },
        'strengths': strengths,
        'gaps': gaps,
        'recommendations': recommendations,
        'next_steps': next_steps,
        'risks': risks,
        'ai_confidence': report.get('consensus', {}).get('confidence', 0.9),
        'powered_by': 'groq_llm',
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@ai_recommendations_bp.route('/api/ai/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get personalised AI recommendations for a user (Groq-powered).
    The authenticated user can only access their own recommendations.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    if user.id != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        assessment_data = _collect_assessment_data(user)
        service = InsightsReportService()
        report = service.generate_report(user.id, assessment_data)
        data = _map_report_to_recommendations(report, user_id)
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        logger.warning(
            f"[Recommendations] LLM failed (user={user_id}): {e} — falling back to rule-based"
        )
        try:
            engine = AIRecommendationsEngine()
            data = engine.generate_recommendations(user_id)
            return jsonify({'success': True, 'data': data}), 200
        except Exception as e2:
            logger.error(f"[Recommendations] Fallback also failed: {e2}")
            return jsonify({'success': False, 'error': str(e2)}), 500


@ai_recommendations_bp.route('/api/ai/recommendations/strengths/<int:user_id>', methods=['GET'])
def get_user_strengths(user_id):
    """
    Get strengths analysis for a user (Groq-powered).
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    if user.id != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        assessment_data = _collect_assessment_data(user)
        service = InsightsReportService()
        report = service.generate_report(user.id, assessment_data)
        ent = report.get('entrepreneur', {})
        return jsonify({
            'success': True,
            'data': {
                'strengths': [
                    {'title': s['name'], 'score': s.get('score', 0)}
                    for s in ent.get('strengths', [])
                ],
                'founder_profile': {
                    'archetype': ent.get('archetype', 'Founder'),
                    'tagline': ent.get('tagline', ''),
                    'score': ent.get('score', 0),
                },
                'ai_confidence': report.get('consensus', {}).get('confidence', 0.9),
            },
        }), 200
    except Exception as e:
        logger.error(f"[Strengths] Error for user {user_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_recommendations_bp.route('/api/ai/recommendations/action-plan/<int:user_id>', methods=['GET'])
def get_action_plan(user_id):
    """
    Get focused action plan (gaps + next steps), Groq-powered.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    if user.id != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        assessment_data = _collect_assessment_data(user)
        service = InsightsReportService()
        report = service.generate_report(user.id, assessment_data)
        data = _map_report_to_recommendations(report, user_id)
        return jsonify({
            'success': True,
            'data': {
                'gaps': data['gaps'],
                'next_steps': data['next_steps'],
                'recommendations': data['recommendations'],
                'success_probability': data['success_probability'],
            },
        }), 200
    except Exception as e:
        logger.error(f"[ActionPlan] Error for user {user_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


