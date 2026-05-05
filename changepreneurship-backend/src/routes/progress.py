"""
Progress API — Sprint 6 (S6-04)
=================================
Endpoints:
  GET  /api/v1/progress/dashboard      — full dashboard aggregation
  GET  /api/v1/progress/phases         — 7-phase status list
  GET  /api/v1/progress/current-phase  — current/active phase
  GET  /api/v1/progress/next-action    — recommended next step
  GET  /api/v1/progress/blockers       — active blockers
  POST /api/v1/benchmark/outcome       — record anonymised outcome
  GET  /api/v1/benchmark/insight       — get benchmark message
"""
import logging

from flask import Blueprint, request, jsonify

from src.services.progress_dashboard_service import ProgressDashboardService
from src.services.benchmark_intelligence_service import (
    BenchmarkIntelligenceService, ALL_METRIC_TYPES,
)
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__)

_dashboard_svc  = ProgressDashboardService()
_benchmark_svc  = BenchmarkIntelligenceService()


# ---------------------------------------------------------------------------
# GET /api/v1/progress/dashboard
# ---------------------------------------------------------------------------
@progress_bp.route('/progress/dashboard', methods=['GET'])
@limiter.limit('30 per hour')
def get_dashboard():
    """Full user progress dashboard."""
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    try:
        data = _dashboard_svc.get_user_dashboard(user.id)
        return jsonify({'dashboard': data}), 200
    except Exception:
        logger.exception('[Progress] get_dashboard user_id=%d', user.id)
        return jsonify({'error': 'Failed to load dashboard'}), 500


# ---------------------------------------------------------------------------
# GET /api/v1/progress/phases
# ---------------------------------------------------------------------------
@progress_bp.route('/progress/phases', methods=['GET'])
@limiter.limit('60 per hour')
def get_phases():
    """7-phase status list (LOCKED / NOT_STARTED / IN_PROGRESS / COMPLETED)."""
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    try:
        phases = _dashboard_svc._get_phase_statuses(user.id)
        stats  = _dashboard_svc._compute_stats(phases)
        return jsonify({'phases': phases, 'stats': stats}), 200
    except Exception:
        logger.exception('[Progress] get_phases user_id=%d', user.id)
        return jsonify({'error': 'Failed to load phases'}), 500


# ---------------------------------------------------------------------------
# GET /api/v1/progress/current-phase
# ---------------------------------------------------------------------------
@progress_bp.route('/progress/current-phase', methods=['GET'])
@limiter.limit('60 per hour')
def get_current_phase():
    """Returns the current/active phase summary."""
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    try:
        summary = _dashboard_svc.get_current_stage_summary(user.id)
        return jsonify({'current_phase': summary}), 200
    except Exception:
        logger.exception('[Progress] get_current_phase user_id=%d', user.id)
        return jsonify({'error': 'Failed to load current phase'}), 500


# ---------------------------------------------------------------------------
# GET /api/v1/progress/next-action
# ---------------------------------------------------------------------------
@progress_bp.route('/progress/next-action', methods=['GET'])
@limiter.limit('30 per hour')
def get_next_action():
    """Recommended next step (always concrete, never vague)."""
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    try:
        action = _dashboard_svc.get_next_recommended_action(user.id)
        return jsonify({'next_action': action}), 200
    except Exception:
        logger.exception('[Progress] get_next_action user_id=%d', user.id)
        return jsonify({'error': 'Failed to compute next action'}), 500


# ---------------------------------------------------------------------------
# GET /api/v1/progress/blockers
# ---------------------------------------------------------------------------
@progress_bp.route('/progress/blockers', methods=['GET'])
@limiter.limit('60 per hour')
def get_blockers():
    """Active (unresolved) blockers for the user."""
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    try:
        blockers = _dashboard_svc._get_active_blockers(user.id)
        return jsonify({'blockers': blockers, 'count': len(blockers)}), 200
    except Exception:
        logger.exception('[Progress] get_blockers user_id=%d', user.id)
        return jsonify({'error': 'Failed to load blockers'}), 500


# ---------------------------------------------------------------------------
# POST /api/v1/benchmark/outcome
# ---------------------------------------------------------------------------
@progress_bp.route('/benchmark/outcome', methods=['POST'])
@limiter.limit('20 per hour')
def record_benchmark_outcome():
    """
    Record an anonymised benchmark outcome.
    Body: {metric_type, metric_value, founder_type, venture_type, phase_id}
    """
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    metric_type  = data.get('metric_type', '')
    metric_value = data.get('metric_value', {})
    founder_type = data.get('founder_type', 'UNKNOWN')
    venture_type = data.get('venture_type', 'UNKNOWN')
    phase_id     = data.get('phase_id', 'UNKNOWN')

    if metric_type not in ALL_METRIC_TYPES:
        return jsonify({
            'error': 'Invalid metric_type',
            'valid_types': sorted(ALL_METRIC_TYPES),
        }), 400

    if not isinstance(metric_value, dict):
        return jsonify({'error': 'metric_value must be an object'}), 400

    recorded = _benchmark_svc.record_outcome(
        user_id      = user.id,
        metric_type  = metric_type,
        metric_value = metric_value,
        founder_type = founder_type,
        venture_type = venture_type,
        phase_id     = phase_id,
    )

    if recorded:
        return jsonify({'recorded': True, 'message': 'Outcome recorded anonymously'}), 201
    return jsonify({'recorded': False, 'message': 'Opted out or invalid metric — not recorded'}), 200


# ---------------------------------------------------------------------------
# GET /api/v1/benchmark/insight
# ---------------------------------------------------------------------------
@progress_bp.route('/benchmark/insight', methods=['GET'])
@limiter.limit('60 per hour')
def get_benchmark_insight():
    """
    Returns a benchmark insight message for the user's current context.
    Query params: metric_type, founder_type, venture_type, phase_id
    """
    user, session, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    metric_type  = request.args.get('metric_type', '')
    founder_type = request.args.get('founder_type', 'UNKNOWN')
    venture_type = request.args.get('venture_type', 'UNKNOWN')
    phase_id     = request.args.get('phase_id', 'UNKNOWN')

    if metric_type not in ALL_METRIC_TYPES:
        return jsonify({
            'error': 'Invalid metric_type',
            'valid_types': sorted(ALL_METRIC_TYPES),
        }), 400

    message = _benchmark_svc.get_personalized_benchmark_message(
        user_id      = user.id,
        metric_type  = metric_type,
        founder_type = founder_type,
        venture_type = venture_type,
        phase_id     = phase_id,
    )

    return jsonify({
        'message':      message,
        'has_data':     message is not None,
        'metric_type':  metric_type,
        'phase_id':     phase_id,
    }), 200
