"""
Routing API — Sprint 2 (S2-03)
================================
Endpoints:
  POST /api/v1/routing/evaluate
    → PathDecisionEngine evaluation (Layer 1, sync, max 2s)

  GET  /api/v1/routing/reentry
    → ReentrySnapshot for returning user

  POST /api/v1/routing/change-impact
    → ChangeImpactAnalyzer for a field change

  POST /api/v1/routing/contradictions
    → ContradictionDetector standalone check
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db
from src.models.founder_profile import FounderReadinessProfile
from src.models.user_action import BlockerEvent
from src.services.path_decision_engine import PathDecisionEngine, RoutingDecision
from src.services.reentry_service import ReentryService
from src.services.change_impact_analyzer import ChangeImpactAnalyzer
from src.services.contradiction_detector import ContradictionDetector
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

routing_bp = Blueprint('routing', __name__)

_path_engine = PathDecisionEngine()
_reentry_service = ReentryService()
_impact_analyzer = ChangeImpactAnalyzer()
_contradiction_detector = ContradictionDetector()


# ---------------------------------------------------------------------------
# POST /api/v1/routing/evaluate
# ---------------------------------------------------------------------------
@routing_bp.route('/routing/evaluate', methods=['POST'])
@limiter.limit('30 per hour')
def evaluate_routing():
    """
    Evaluate routing decision for the authenticated user.

    Request body:
      {
        "responses": {...},          // current assessment responses
        "current_phase": 1,          // optional, default 1
        "session_data": {...}         // optional timing/session metadata
      }

    Response: RoutingDecision serialised as JSON + persisted BlockerEvents.
    CEO requirement: Layer 1 only — max 2s, no AI wait.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    responses = data.get('responses', {})
    current_phase = int(data.get('current_phase', 1))
    session_data = data.get('session_data', {})

    # Load the user's latest FounderReadinessProfile (if exists)
    profile = (
        FounderReadinessProfile.query
        .filter_by(user_id=user.id, is_latest=True)
        .first()
    )
    founder_profile_dict = profile.to_dict() if profile else {}

    # Run PathDecisionEngine (Layer 1 — pure Python, no AI, fast)
    try:
        decision = _path_engine.evaluate_routing(
            founder_profile=founder_profile_dict,
            responses=responses,
            current_phase=current_phase,
            session_data=session_data,
        )
    except Exception as exc:
        logger.exception("PathDecisionEngine failed for user %s: %s", user.id, exc)
        return jsonify({'error': 'Routing evaluation failed'}), 500

    # Persist new BlockerEvents for any new hard blockers
    try:
        _persist_blocker_events(user.id, decision, profile.id if profile else None)
    except Exception as exc:
        logger.warning("BlockerEvent persistence failed: %s", exc)

    return jsonify(_serialise_decision(decision)), 200


# ---------------------------------------------------------------------------
# GET /api/v1/routing/reentry
# ---------------------------------------------------------------------------
@routing_bp.route('/routing/reentry', methods=['GET'])
@limiter.limit('20 per hour')
def get_reentry_snapshot():
    """
    Generate a re-entry snapshot for a returning user.
    Uses last_seen from their session record.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    # Determine last_seen (session last used / user last login)
    last_seen = getattr(user, 'last_login', None) or getattr(session, 'created_at', None)

    # Load latest profile to determine current phase and active blockers
    profile = (
        FounderReadinessProfile.query
        .filter_by(user_id=user.id, is_latest=True)
        .first()
    )
    current_phase = 1
    active_blockers = []
    current_outputs = {}

    if profile:
        active_blockers = profile.get_active_blockers()
        # Build outputs dict from profile timestamps
        if profile.created_at:
            current_outputs['FOUNDER_READINESS_PROFILE'] = profile.updated_at or profile.created_at
        if profile.overall_readiness_level is not None and profile.overall_readiness_level <= 2:
            current_phase = 2

    snapshot = _reentry_service.generate_reentry_snapshot(
        last_seen=last_seen,
        current_outputs=current_outputs,
        current_phase=current_phase,
        last_action=None,
        active_blockers=active_blockers,
    )

    return jsonify(snapshot.to_dict()), 200


# ---------------------------------------------------------------------------
# POST /api/v1/routing/change-impact
# ---------------------------------------------------------------------------
@routing_bp.route('/routing/change-impact', methods=['POST'])
@limiter.limit('60 per hour')
def analyze_change_impact():
    """
    Analyse the impact of a user changing a single answer.

    Request body:
      {
        "field": "target_user_description",
        "old_value": "...",
        "new_value": "...",
        "current_outputs": ["FOUNDER_READINESS_PROFILE", ...]  // optional
      }
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    field = data.get('field')
    if not field:
        return jsonify({'error': 'field is required'}), 400

    result = _impact_analyzer.analyze(
        changed_field=field,
        old_value=data.get('old_value'),
        new_value=data.get('new_value'),
        current_outputs=data.get('current_outputs', []),
        responses=data.get('responses', {}),
    )

    return jsonify({
        'severity_level': result.severity_level,
        'changed_field': result.changed_field,
        'requires_user_approval': result.requires_user_approval,
        'is_venture_restart': result.is_venture_restart,
        'affected_outputs': [
            {
                'output_type': a.output_type,
                'status': a.status,
                'action_required': a.action_required,
                'reason': a.reason,
            }
            for a in result.affected_outputs
        ],
        'downstream_impact': result.downstream_impact,
        'sidestream_impact': result.sidestream_impact,
        'recommendation': result.recommendation,
    }), 200


# ---------------------------------------------------------------------------
# POST /api/v1/routing/contradictions
# ---------------------------------------------------------------------------
@routing_bp.route('/routing/contradictions', methods=['POST'])
@limiter.limit('30 per hour')
def check_contradictions():
    """
    Run contradiction detection against a set of responses.

    Request body: { "responses": {...} }
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    responses = data.get('responses', {})
    result = _contradiction_detector.evaluate(responses)

    return jsonify({
        'has_blocking_contradiction': result.has_blocking_contradiction,
        'max_level': result.max_level,
        'summary': result.summary,
        'contradictions': [
            {
                'type': c.type,
                'level': c.level,
                'dimension_a': c.dimension_a,
                'dimension_b': c.dimension_b,
                'explanation': c.explanation,
                'recommendation': c.recommendation,
                'affected_actions': c.affected_actions,
            }
            for c in result.contradictions
        ],
    }), 200


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _persist_blocker_events(user_id: int, decision: RoutingDecision, profile_id=None):
    """
    Persist BlockerEvents for new hard blockers from a routing decision.
    Only creates events for blockers with severity >= 3 that are not already active.
    """
    for blocker in decision.blocked_actions:
        severity = blocker.get('severity', 3)
        if severity < 3:
            continue
        blocker_type = blocker.get('type') or blocker.get('action', 'UNKNOWN')

        # Check if already active
        existing = BlockerEvent.query.filter_by(
            user_id=user_id,
            blocker_type=blocker_type,
            resolved_at=None,
        ).first()
        if existing:
            continue

        event = BlockerEvent(
            user_id=user_id,
            blocker_type=blocker_type,
            dimension=blocker.get('dimension'),
            severity_level=severity,
            source_service='path_decision_engine',
            what_is_blocked=blocker.get('what_is_blocked') or [blocker.get('action')],
            what_is_allowed=decision.allowed_actions,
            unlock_condition=blocker.get('unlock') or blocker.get('unlock_condition'),
            trigger_signal={'routing_category': decision.category},
            founder_readiness_profile_id=profile_id,
        )
        db.session.add(event)

    db.session.commit()


def _serialise_decision(decision: RoutingDecision) -> dict:
    """Serialise RoutingDecision to JSON-safe dict."""
    na = decision.next_action
    rm = decision.reroute_message

    result = {
        'category': decision.category,
        'priority_level': decision.priority_level,
        'is_reroute': decision.is_reroute,
        'allowed_actions': decision.allowed_actions,
        'blocked_actions': decision.blocked_actions,
        'next_action': {
            'type': na.type,
            'description': na.description,
            'success_criteria': na.success_criteria,
            'template': na.template,
            'estimated_time': na.estimated_time,
        },
        'overperformance_signal': decision.overperformance_signal,
        'verification_tasks': decision.verification_tasks,
        'contradictions_summary': decision.contradictions_summary,
    }

    if rm:
        result['reroute_message'] = {
            'detected': rm.detected,
            'why': rm.why,
            'blocked_action': rm.blocked_action,
            'allowed_action': rm.allowed_action,
            'unlock_condition': rm.unlock_condition,
            'full_text': _path_engine.compute_reroute_message_text(decision),
        }
    else:
        result['reroute_message'] = None

    return result
