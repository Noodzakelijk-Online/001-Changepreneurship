"""
Actions API — Sprint 4 (S4-03)
==================================
Endpoints:
  GET  /api/v1/actions/pending          — list pending actions requiring approval
  GET  /api/v1/actions/history          — user's action history
  POST /api/v1/actions/propose          — propose a new action
  POST /api/v1/actions/<id>/approve     — user approves an action
  POST /api/v1/actions/<id>/reject      — user rejects an action
  POST /api/v1/actions/<id>/cancel      — user cancels an action
  POST /api/v1/actions/<id>/outcome     — record outcome of executed action
  GET  /api/v1/actions/mentors          — search mentors (MicroMentor)
  POST /api/v1/actions/outreach/draft   — draft outreach message
"""
import logging

from flask import Blueprint, request, jsonify

from src.services.user_action_service import UserActionService
from src.services.micromentor_integration import MicroMentorIntegration
from src.services.action_queue_worker import ActionQueueWorker
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

actions_bp = Blueprint('actions', __name__)

_action_service = UserActionService()
_mentor_integration = MicroMentorIntegration()
_queue_worker = ActionQueueWorker()  # Redis not connected in dev → safe fallback


# ---------------------------------------------------------------------------
# GET /api/v1/actions/pending
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/pending', methods=['GET'])
@limiter.limit('60 per hour')
def get_pending_actions():
    """List actions awaiting user approval."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    pending = _action_service.get_pending_actions(user.id)
    return jsonify({'pending': pending, 'count': len(pending)}), 200


# ---------------------------------------------------------------------------
# GET /api/v1/actions/history
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/history', methods=['GET'])
@limiter.limit('30 per hour')
def get_action_history():
    """Return recent action history."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    limit = min(int(request.args.get('limit', 20)), 100)
    history = _action_service.get_action_history(user.id, limit=limit)
    return jsonify({'history': history}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/actions/propose
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/propose', methods=['POST'])
@limiter.limit('20 per hour')
def propose_action():
    """Propose a new action."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    action_type = data.get('action_type')
    action_data = data.get('action_data', {})
    rationale = data.get('rationale', '')
    external_platform = data.get('external_platform')

    if not action_type:
        return jsonify({'error': 'action_type is required'}), 400

    try:
        action = _action_service.propose_action(
            user_id=user.id,
            action_type=action_type,
            action_data=action_data,
            rationale=rationale,
            external_platform=external_platform,
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 409

    # If auto-approved and has platform, enqueue
    if action.approval_status == 'APPROVED':
        _queue_worker.enqueue(action.id)

    return jsonify({'action': action.to_dict()}), 201


# ---------------------------------------------------------------------------
# POST /api/v1/actions/<id>/approve
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/<int:action_id>/approve', methods=['POST'])
@limiter.limit('30 per hour')
def approve_action(action_id):
    """User approves a pending action."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        action = _action_service.approve_action(
            action_id=action_id,
            user_id=user.id,
            actor=f'user:{user.id}',
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    # Enqueue for execution
    _queue_worker.enqueue(action.id)

    return jsonify({'action': action.to_dict(), 'queued': True}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/actions/<id>/reject
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/<int:action_id>/reject', methods=['POST'])
@limiter.limit('30 per hour')
def reject_action(action_id):
    """User rejects a pending action."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    reason = data.get('reason', '')

    try:
        action = _action_service.reject_action(
            action_id=action_id,
            user_id=user.id,
            reason=reason,
            actor=f'user:{user.id}',
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify({'action': action.to_dict()}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/actions/<id>/cancel
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/<int:action_id>/cancel', methods=['POST'])
@limiter.limit('20 per hour')
def cancel_action(action_id):
    """User cancels a pending or approved action."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    reason = data.get('reason', '')

    try:
        action = _action_service.cancel_action(
            action_id=action_id,
            user_id=user.id,
            reason=reason,
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify({'action': action.to_dict()}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/actions/<id>/outcome
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/<int:action_id>/outcome', methods=['POST'])
@limiter.limit('30 per hour')
def record_outcome(action_id):
    """Record what actually happened after execution."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    outcome = data.get('outcome')
    if not outcome:
        return jsonify({'error': 'outcome is required'}), 400

    # Verify ownership
    from src.models.user_action import UserAction
    action = UserAction.query.filter_by(id=action_id, user_id=user.id).first()
    if not action:
        return jsonify({'error': 'Action not found'}), 404

    try:
        action = _action_service.record_outcome(
            action_id=action_id,
            outcome=outcome,
            outcome_data=data.get('outcome_data'),
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify({'action': action.to_dict()}), 200


# ---------------------------------------------------------------------------
# GET /api/v1/actions/mentors
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/mentors', methods=['GET'])
@limiter.limit('20 per hour')
def search_mentors():
    """Search MicroMentor for matching mentors (AUTO_APPROVE, read-only)."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    expertise = request.args.getlist('expertise') or ['entrepreneurship']
    location = request.args.get('location')

    # Propose as AUTO_APPROVE action
    try:
        _action_service.propose_action(
            user_id=user.id,
            action_type='SEARCH_MENTORS',
            action_data={'expertise': expertise, 'location': location},
        )
    except ValueError:
        pass  # Duplicate is fine — search again anyway

    mentors = _mentor_integration.search_mentors(expertise, location=location)
    return jsonify({'mentors': [
        {
            'id': m.id,
            'name': m.name,
            'expertise': m.expertise,
            'location': m.location,
            'bio': m.bio,
            'availability': m.availability,
            'match_score': m.match_score,
        }
        for m in mentors
    ]}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/actions/outreach/draft
# ---------------------------------------------------------------------------
@actions_bp.route('/actions/outreach/draft', methods=['POST'])
@limiter.limit('10 per hour')
def draft_outreach():
    """Draft a mentor outreach message (AUTO_APPROVE — draft, not sent)."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    mentor_data = data.get('mentor', {})
    founder_context = data.get('founder_context', {})

    if not mentor_data:
        return jsonify({'error': 'mentor object required'}), 400

    from src.services.micromentor_integration import MentorProfile
    mentor = MentorProfile(
        id=mentor_data.get('id', 'unknown'),
        name=mentor_data.get('name', 'Mentor'),
        expertise=mentor_data.get('expertise', []),
        location=mentor_data.get('location', 'Remote'),
        bio=mentor_data.get('bio', ''),
        availability=mentor_data.get('availability', 'Available'),
        match_score=mentor_data.get('match_score', 0.8),
    )
    draft = _mentor_integration.draft_outreach(mentor, founder_context)

    # Propose as draft action
    try:
        action = _action_service.propose_action(
            user_id=user.id,
            action_type='DRAFT_OUTREACH',
            action_data={
                'mentor_id': mentor.id,
                'subject': draft.subject,
                'body_preview': draft.body[:100],
            },
            external_platform='micromentor',
        )
    except ValueError as exc:
        logger.warning("Draft outreach propose failed: %s", exc)
        action = None

    return jsonify({
        'draft': {
            'subject': draft.subject,
            'body': draft.body,
            'mentor_id': draft.mentor_id,
            'platform': draft.platform,
        },
        'action_id': action.id if action else None,
        'requires_approval_to_send': True,
    }), 200
