"""
AI Consensus API Routes
Multi-LLM business insights endpoints
"""
from flask import Blueprint, jsonify, request
from src.services.ai_consensus import AIConsensusService
from src.services.insights_report_service import InsightsReportService
from src.services.phase_summary_service import PhaseSummaryService
from src.models.assessment import Assessment, AssessmentResponse, db
from src.utils.auth import verify_session_token
import logging

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/consensus', methods=['GET'])
def get_consensus():
    """
    Generate AI consensus insights for current user
    
    Returns:
        JSON with multi-LLM consensus analysis
    """
    # Verify authentication
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    try:
        user_id = user.id
        
        # Fetch all user assessments
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        
        if not assessments:
            return jsonify({
                'success': False,
                'error': 'No assessments found',
                'message': 'Complete at least one assessment phase to get insights'
            }), 404
        
        # Fetch all responses
        assessment_ids = [a.id for a in assessments]
        responses = AssessmentResponse.query.filter(
            AssessmentResponse.assessment_id.in_(assessment_ids)
        ).all()
        
        # Prepare data for AI analysis
        # Group responses by phase
        responses_by_phase = {}
        for r in responses:
            phase_id = next((a.phase_id for a in assessments if a.id == r.assessment_id), None)
            if phase_id:
                if phase_id not in responses_by_phase:
                    responses_by_phase[phase_id] = []
                responses_by_phase[phase_id].append({
                    'question_id': r.question_id,
                    'section_id': r.section_id,
                    'response_value': r.response_value,
                    'response_type': r.response_type
                })
        
        # Prepare phase metadata
        phase_data = {
            'total_phases': len(assessments),
            'completed_phases': sum(1 for a in assessments if a.is_completed),
            'phases': [
                {
                    'id': a.phase_id,
                    'name': a.phase_name,
                    'progress': a.progress_percentage,
                    'completed': a.is_completed
                }
                for a in assessments
            ]
        }
        
        # Generate consensus insights
        consensus_service = AIConsensusService()
        result = consensus_service.generate_consensus(responses_by_phase, phase_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Consensus generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/executive-summary', methods=['GET'])
def get_executive_summary():
    """
    Get executive summary (alias for consensus endpoint for compatibility)
    """
    return get_consensus()

@ai_bp.route('/dashboard/executive-summary', methods=['GET'])
def get_dashboard_executive_summary():
    """
    Dashboard executive summary endpoint (for compatibility with frontend)
    """
    return get_consensus()


@ai_bp.route('/health', methods=['GET'])
def health_check():
    """Check AI service health and available LLMs"""
    service = AIConsensusService()
    
    available_llms = []
    if service.gemini_key:
        available_llms.append('google-gemini')
    if service.groq_key:
        available_llms.append('groq-llama3')
    if service.hf_key:
        available_llms.append('huggingface-mistral')
    
    return jsonify({
        'status': 'healthy',
        'available_llms': available_llms,
        'llm_count': len(available_llms),
        'fallback_enabled': True
    }), 200


# ---------------------------------------------------------------------------
# Full AI Insights Report (Entrepreneur + Venture + Alignment)
# ---------------------------------------------------------------------------

@ai_bp.route('/insights-report', methods=['GET'])
def get_insights_report():
    """
    Generate the full AI-powered Entrepreneur & Venture insights report.

    The report is built by sending all assessment responses to the Groq LLM
    (llama-3.3-70b-versatile) with a structured JSON prompt, so every score,
    insight, sweet-spot and risk-zone is AI-reasoned — not deterministic.

    Query params:
        refresh=1  — bypass Redis cache and regenerate

    Returns:
        {
          success: true,
          report: { entrepreneur, venture, alignment, readiness, consensus, ... }
        }
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        force_refresh = request.args.get('refresh', '0') == '1'
        service = InsightsReportService()

        # Bust cache if requested
        if force_refresh:
            service.invalidate_cache(user.id)

        # Collect all assessments -------------------------------------------
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

        # Collect responses grouped by phase_id --------------------------------
        responses_by_phase: dict = {}
        if assessments:
            assessment_ids = [a.id for a in assessments]
            all_responses = AssessmentResponse.query.filter(
                AssessmentResponse.assessment_id.in_(assessment_ids)
            ).all()

            # Build a lookup: assessment_id → phase_id
            aid_to_phase = {a.id: a.phase_id for a in assessments}

            for r in all_responses:
                phase_id = aid_to_phase.get(r.assessment_id)
                if phase_id:
                    responses_by_phase.setdefault(phase_id, []).append({
                        'question_id': r.question_id,
                        'section_id': r.section_id,
                        'question_text': r.question_text or r.question_id,
                        'response_value': r.get_response_value(),
                        'response_type': r.response_type,
                    })

        assessment_data = {
            'phases': phases,
            'responses': responses_by_phase,
        }

        report = service.generate_report(user.id, assessment_data)

        return jsonify({
            'success': True,
            'report': report,
        }), 200

    except Exception as e:
        logger.error(f"[InsightsReport] Error for user {user.id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


# ---------------------------------------------------------------------------
# Phase Completion Summary
# ---------------------------------------------------------------------------

@ai_bp.route('/phase-summary', methods=['POST'])
def get_phase_summary():
    """
    Generate a brief AI-powered summary for a single completed assessment phase.
    Called immediately after the user finishes a phase.

    Request body:
        { "phase_id": "self_discovery" }

    Returns:
        {
          success: true,
          summary: { phase_id, score, headline, summary, key_findings, next_focus }
        }
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json() or {}
    phase_id = (data.get('phase_id') or '').strip()
    if not phase_id:
        return jsonify({'success': False, 'error': 'phase_id is required'}), 400

    assessment = Assessment.query.filter_by(
        user_id=user.id, phase_id=phase_id
    ).first()
    if not assessment:
        return jsonify({
            'success': False,
            'error': f'No assessment found for phase: {phase_id}',
        }), 404

    responses = AssessmentResponse.query.filter_by(
        assessment_id=assessment.id
    ).all()

    service = PhaseSummaryService()
    summary = service.generate_summary(phase_id, assessment.phase_name, responses)

    return jsonify({'success': True, 'summary': summary}), 200
