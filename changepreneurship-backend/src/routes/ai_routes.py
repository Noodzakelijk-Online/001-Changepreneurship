"""
AI Consensus API Routes
Multi-LLM business insights endpoints
"""
from flask import Blueprint, jsonify, request
from src.services.ai_consensus import AIConsensusService
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
