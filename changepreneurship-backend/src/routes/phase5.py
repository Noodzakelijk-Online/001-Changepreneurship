"""
Phase 5 API — Sprint 11
========================
CEO Section 5: "Do real people respond positively to this specific concept?"

Endpoints:
  GET  /api/v1/phase5/concept-tests     — load current responses
  PATCH /api/v1/phase5/concept-tests    — upsert responses
  GET  /api/v1/phase5/adoption-signal   — live adoption signal (no submit)
  POST /api/v1/phase5/submit            — assess adoption + generate result
  GET  /api/v1/phase5/result            — latest Product Concept Test Result
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.concept_testing import ConceptTestData, ConceptTestResult
from src.models.venture_record import VentureRecord
from src.services.phase5_concept_service import Phase5ConceptService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase5_bp = Blueprint('phase5', __name__)
_svc = Phase5ConceptService()


def _active_venture(user_id: int) -> VentureRecord | None:
    return (
        VentureRecord.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(VentureRecord.version.desc())
        .first()
    )


def _get_or_create_data(user_id: int, venture_id: int | None) -> ConceptTestData:
    record = ConceptTestData.query.filter_by(user_id=user_id).first()
    if not record:
        record = ConceptTestData(
            user_id=user_id,
            venture_id=venture_id,
            responses={},
        )
        db.session.add(record)
        db.session.flush()
    return record


# ─── GET /api/v1/phase5/concept-tests ──────────────────────────────────────

@phase5_bp.route('/phase5/concept-tests', methods=['GET'])
@limiter.limit('60 per hour')
def get_concept_tests():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = ConceptTestData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'responses': {}, 'completed': False, 'completion_pct': 0}), 200

    total_q = 17  # total questions across all 4 sections
    answered = sum(1 for v in (record.responses or {}).values()
                   if v is not None and str(v).strip())
    pct = int(min(answered / total_q, 1.0) * 100)

    return jsonify({
        'responses':      record.responses or {},
        'completed':      record.completed,
        'completion_pct': pct,
        'updated_at':     record.updated_at.isoformat() if record.updated_at else None,
    }), 200


# ─── PATCH /api/v1/phase5/concept-tests ────────────────────────────────────

@phase5_bp.route('/phase5/concept-tests', methods=['PATCH'])
@limiter.limit('120 per hour')
def upsert_concept_tests():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    body = request.get_json(silent=True) or {}
    new_responses = body.get('responses', {})
    if not isinstance(new_responses, dict):
        return jsonify({'error': 'responses must be a dict'}), 422

    venture = _active_venture(user.id)
    record  = _get_or_create_data(user.id, venture.id if venture else None)

    merged = {**(record.responses or {}), **new_responses}
    record.responses  = merged
    record.updated_at = datetime.utcnow()
    db.session.commit()

    total_q = 17
    answered = sum(1 for v in merged.values() if v is not None and str(v).strip())
    pct = int(min(answered / total_q, 1.0) * 100)

    return jsonify({
        'responses':      merged,
        'completion_pct': pct,
        'updated_at':     record.updated_at.isoformat(),
    }), 200


# ─── GET /api/v1/phase5/adoption-signal ────────────────────────────────────

@phase5_bp.route('/phase5/adoption-signal', methods=['GET'])
@limiter.limit('60 per hour')
def adoption_signal():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = ConceptTestData.query.filter_by(user_id=user.id).first()
    responses = record.responses if record else {}
    result = _svc.assess_adoption(responses)
    return jsonify(result), 200


# ─── POST /api/v1/phase5/submit ────────────────────────────────────────────

@phase5_bp.route('/phase5/submit', methods=['POST'])
@limiter.limit('20 per hour')
def submit_concept_test():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = ConceptTestData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'error': 'No concept test data found. Save responses first.'}), 404

    ok, msg = _svc.validate_for_submit(record.responses or {})
    if not ok:
        return jsonify({'error': msg}), 422

    venture = _active_venture(user.id)
    result_dict = _svc.generate_result(venture, record.responses)

    # Persist result (allow multiple; latest is the one we return)
    result_row = ConceptTestResult(
        user_id=user.id,
        venture_id=venture.id if venture else None,
        result_data=result_dict,
        adoption_signal=result_dict['adoption_signal'],
        decision=result_dict['decision'],
        ready_for_business_dev=result_dict['ready_for_business_dev'],
    )
    db.session.add(result_row)

    record.completed  = True
    record.updated_at = datetime.utcnow()
    db.session.commit()

    # Sync Assessment record (drives sidebar unlocking)
    try:
        _upsert_assessment_phase5(user.id, result_dict['ready_for_business_dev'])
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    return jsonify(result_row.to_dict()), 201


# ─── GET /api/v1/phase5/result ─────────────────────────────────────────────

@phase5_bp.route('/phase5/result', methods=['GET'])
@limiter.limit('60 per hour')
def get_result():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    row = (
        ConceptTestResult.query
        .filter_by(user_id=user.id)
        .order_by(ConceptTestResult.generated_at.desc())
        .first()
    )
    if not row:
        return jsonify({'result': None}), 200
    return jsonify(row.to_dict()), 200


def _upsert_assessment_phase5(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 5 (product_concept_testing)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='product_concept_testing').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='product_concept_testing',
            phase_name='Product Concept Testing',
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
