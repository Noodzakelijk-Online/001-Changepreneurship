"""
Phase 2 API — Sprint 3 (S3-02, S3-05)
========================================
Endpoints:
  POST /api/v1/phase2/submit            — evaluate idea + generate CVC
  GET  /api/v1/phase2/venture           — get active VentureRecord
  PUT  /api/v1/phase2/venture/<id>      — update venture (versioned)
  POST /api/v1/phase2/assumptions/test  — mark assumption as tested
  POST /api/v1/phase2/evidence          — submit evidence item
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.venture_record import (
    VentureRecord, EvidenceItem,
    VENTURE_STATUS_CLARIFIED, VENTURE_STATUS_DRAFT,
)
from src.services.phase2_idea_service import Phase2IdeaService
from src.services.assumption_tracker import AssumptionTracker
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase2_bp = Blueprint('phase2', __name__)

_phase2_service = Phase2IdeaService()
_assumption_tracker = AssumptionTracker()


# ---------------------------------------------------------------------------
# POST /api/v1/phase2/submit
# ---------------------------------------------------------------------------
@phase2_bp.route('/phase2/submit', methods=['POST'])
@limiter.limit('20 per hour')
def submit_phase2():
    """
    Evaluate idea clarity (Layer 1) and generate CVC (Layer 3 template).
    Creates or updates the active VentureRecord.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    responses = data.get('responses', {})
    if not responses:
        return jsonify({'error': 'responses is required'}), 400

    # Layer 1: evaluate idea clarity
    result = _phase2_service.evaluate_idea_clarity(responses)

    # Layer 3: generate CVC if no hard block
    if result.can_generate_cvc:
        result = _phase2_service.generate_cvc_from_responses(responses, result)

    # Persist VentureRecord
    try:
        venture = _upsert_venture(user.id, responses, result)
        venture_id = venture.id
        venture_dict = venture.to_dict()
    except Exception as exc:
        logger.exception("Failed to persist VentureRecord for user %s: %s", user.id, exc)
        return jsonify({'error': 'Failed to save venture record'}), 500

    # Sync Assessment record (drives sidebar unlocking)
    try:
        is_complete = result.idea_block_level < 4  # no hard block
        _upsert_assessment_phase2(user.id, is_complete)
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    return jsonify({
        'venture_id': venture_id,
        'idea_block_level': result.idea_block_level,
        'can_generate_cvc': result.can_generate_cvc,
        'clarity_score': result.clarity_score,
        'cvc_generated': result.cvc_generated,
        'missing_elements': result.missing_elements,
        'venture_type_hint': result.venture_type_hint,
        'blockers': [
            {
                'type': b.type,
                'level': b.level,
                'explanation': b.explanation,
                'what_is_blocked': b.what_is_blocked,
                'what_is_allowed': b.what_is_allowed,
                'unlock_condition': b.unlock_condition,
            }
            for b in result.blockers
        ],
        'cvc': {
            'problem_statement': result.problem_statement,
            'target_user_hypothesis': result.target_user_hypothesis,
            'value_proposition': result.value_proposition,
            'assumptions': result.assumptions,
            'open_questions': result.open_questions,
        } if result.cvc_generated else None,
        'venture': venture_dict,
    }), 200


# ---------------------------------------------------------------------------
# GET /api/v1/phase2/venture
# ---------------------------------------------------------------------------
@phase2_bp.route('/phase2/venture', methods=['GET'])
@limiter.limit('60 per hour')
def get_venture():
    """Return the user's active VentureRecord."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    venture = VentureRecord.query.filter_by(user_id=user.id, is_active=True).first()
    if not venture:
        return jsonify({'venture': None}), 200

    summary = _assumption_tracker.compute_summary(venture.assumptions or [], venture.id)
    d = venture.to_dict()
    d['assumption_summary'] = {
        'total': summary.total,
        'tested': summary.tested,
        'untested': summary.untested,
        'tested_pct': summary.tested_pct,
        'high_risk_untested_count': len(summary.high_risk_untested),
    }
    return jsonify({'venture': d}), 200


# ---------------------------------------------------------------------------
# PUT /api/v1/phase2/venture/<int:venture_id>
# ---------------------------------------------------------------------------
@phase2_bp.route('/phase2/venture/<int:venture_id>', methods=['PUT'])
@limiter.limit('30 per hour')
def update_venture(venture_id):
    """
    Update a venture (versioned).
    Strategic changes trigger ChangeImpactAnalyzer.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    venture = VentureRecord.query.filter_by(id=venture_id, user_id=user.id).first()
    if not venture:
        return jsonify({'error': 'Venture not found'}), 404

    data = request.get_json(silent=True) or {}

    # Allowed direct updates
    allowed_fields = [
        'idea_raw', 'idea_clarified', 'problem_statement',
        'target_user_hypothesis', 'value_proposition',
        'venture_type', 'founder_motivation_summary',
        'assumptions', 'open_questions', 'status',
    ]
    for field in allowed_fields:
        if field in data:
            setattr(venture, field, data[field])

    venture.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'venture': venture.to_dict()}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/phase2/assumptions/test
# ---------------------------------------------------------------------------
@phase2_bp.route('/phase2/assumptions/test', methods=['POST'])
@limiter.limit('60 per hour')
def mark_assumption_tested():
    """
    User explicitly marks an assumption as tested.
    Updates VentureRecord.assumptions JSON.
    """
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}
    venture_id = data.get('venture_id')
    assumption_id = data.get('assumption_id')
    test_result = data.get('test_result')
    new_type = data.get('new_type')

    if not all([venture_id, assumption_id, test_result]):
        return jsonify({'error': 'venture_id, assumption_id, test_result required'}), 400

    venture = VentureRecord.query.filter_by(id=venture_id, user_id=user.id).first()
    if not venture:
        return jsonify({'error': 'Venture not found'}), 404

    assumptions = list(venture.assumptions or [])
    updated = False
    for a in assumptions:
        if a.get('id') == assumption_id:
            a['tested'] = True
            a['test_result'] = test_result
            a['tested_at'] = datetime.utcnow().isoformat()
            if new_type:
                a['assumption_type'] = new_type
            updated = True
            break

    if not updated:
        return jsonify({'error': 'Assumption not found'}), 404

    venture.assumptions = assumptions
    db.session.commit()

    summary = _assumption_tracker.compute_summary(assumptions, venture_id)
    return jsonify({
        'updated': True,
        'assumption_summary': {
            'total': summary.total,
            'tested': summary.tested,
            'tested_pct': summary.tested_pct,
        },
    }), 200


# ---------------------------------------------------------------------------
# POST /api/v1/phase2/evidence
# ---------------------------------------------------------------------------
@phase2_bp.route('/phase2/evidence', methods=['POST'])
@limiter.limit('30 per hour')
def submit_evidence():
    """Submit a new EvidenceItem linked to a venture."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json(silent=True) or {}

    venture_id = data.get('venture_id')
    evidence_type = data.get('evidence_type')
    strength = data.get('strength', 'BELIEF')
    description = data.get('description', '')

    if not evidence_type or not description:
        return jsonify({'error': 'evidence_type and description required'}), 400

    # Verify venture belongs to user
    if venture_id:
        venture = VentureRecord.query.filter_by(id=venture_id, user_id=user.id).first()
        if not venture:
            return jsonify({'error': 'Venture not found'}), 404

    item = EvidenceItem(
        user_id=user.id,
        venture_id=venture_id,
        evidence_type=evidence_type,
        strength=strength,
        description=description,
        source=data.get('source', ''),
        affects_dimensions=data.get('affects_dimensions', []),
        is_validated=False,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'evidence_id': item.id, 'evidence': item.to_dict()}), 201


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _upsert_venture(user_id: int, responses: dict, result) -> VentureRecord:
    """Create or update the active VentureRecord."""
    existing = VentureRecord.query.filter_by(user_id=user_id, is_active=True).first()

    if existing:
        # Update in place (keep version — major changes would bump version)
        if result.problem_statement:
            existing.problem_statement = result.problem_statement
        if result.target_user_hypothesis:
            existing.target_user_hypothesis = result.target_user_hypothesis
        if result.value_proposition:
            existing.value_proposition = result.value_proposition
        if result.assumptions:
            existing.assumptions = result.assumptions
        if result.open_questions:
            existing.open_questions = result.open_questions
        if responses.get('idea_description'):
            existing.idea_raw = responses['idea_description']
        if result.venture_type_hint and not existing.venture_type:
            existing.venture_type = result.venture_type_hint
        if result.cvc_generated and existing.status == VENTURE_STATUS_DRAFT:
            existing.status = VENTURE_STATUS_CLARIFIED
        existing.updated_at = datetime.utcnow()
        db.session.commit()
        return existing

    # Create new
    venture = VentureRecord(
        user_id=user_id,
        version=1,
        is_active=True,
        idea_raw=responses.get('idea_description', ''),
        idea_clarified=responses.get('idea_clarified', ''),
        problem_statement=result.problem_statement,
        target_user_hypothesis=result.target_user_hypothesis,
        value_proposition=result.value_proposition,
        venture_type=result.venture_type_hint,
        founder_motivation_summary=responses.get('founder_motivation_summary', ''),
        assumptions=result.assumptions,
        open_questions=result.open_questions,
        status=VENTURE_STATUS_CLARIFIED if result.cvc_generated else VENTURE_STATUS_DRAFT,
    )
    db.session.add(venture)
    db.session.commit()
    return venture


def _upsert_assessment_phase2(user_id: int, force_complete: bool) -> Assessment:
    """
    Ensure an Assessment record exists for Phase 2 (idea_discovery).
    Drives ProgressDashboardService phase-gate unlocking.
    """
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='idea_discovery').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='idea_discovery',
            phase_name='Idea Discovery Assessment',
            started_at=datetime.utcnow(),
        )
        db.session.add(assessment)

    if force_complete and not assessment.is_completed:
        assessment.is_completed = True
        assessment.progress_percentage = 100.0
        assessment.completed_at = datetime.utcnow()
    elif not force_complete and assessment.progress_percentage < 50:
        assessment.progress_percentage = 50.0

    db.session.commit()
    return assessment
