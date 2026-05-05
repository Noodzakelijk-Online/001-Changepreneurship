"""
Phase 7 API — Sprint 13
========================
CEO Section 7: "Does the venture work when real people, money, operations, and constraints are involved?"

Endpoints:
  GET  /api/v1/phase7/prototype-test    — load current responses
  PATCH /api/v1/phase7/prototype-test   — upsert responses
  GET  /api/v1/phase7/readiness         — live scale readiness assessment
  POST /api/v1/phase7/submit            — generate Business Prototype Test Report
  GET  /api/v1/phase7/report            — latest Test Report
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.prototype_testing import PrototypeTestData, PrototypeTestResult
from src.models.venture_record import VentureRecord
from src.services.phase7_prototype_service import (
    assess_scale_readiness,
    generate_report,
    validate_for_submit,
    REQUIRED_FOR_SUBMIT,
)
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase7_bp = Blueprint('phase7', __name__)

TOTAL_QUESTIONS = 12  # 6 sections × 2 questions each


def _active_venture(user_id: int) -> VentureRecord | None:
    return (
        VentureRecord.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(VentureRecord.version.desc())
        .first()
    )


def _get_or_create_data(user_id: int, venture_id) -> PrototypeTestData:
    record = PrototypeTestData.query.filter_by(user_id=user_id).first()
    if not record:
        record = PrototypeTestData(
            user_id=user_id,
            venture_id=venture_id,
            responses={},
        )
        db.session.add(record)
        db.session.flush()
    return record


# ─── GET /api/v1/phase7/prototype-test ─────────────────────────────────────

@phase7_bp.route('/phase7/prototype-test', methods=['GET'])
@limiter.limit('60 per hour')
def get_prototype_test():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = PrototypeTestData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'responses': {}, 'completed': False, 'completion_pct': 0}), 200

    answered = sum(1 for v in (record.responses or {}).values()
                   if v is not None and str(v).strip())
    pct = int(min(answered / TOTAL_QUESTIONS, 1.0) * 100)

    return jsonify({
        'responses':      record.responses or {},
        'completed':      record.completed,
        'completion_pct': pct,
        'updated_at':     record.updated_at.isoformat() if record.updated_at else None,
    }), 200


# ─── PATCH /api/v1/phase7/prototype-test ───────────────────────────────────

@phase7_bp.route('/phase7/prototype-test', methods=['PATCH'])
@limiter.limit('120 per hour')
def upsert_prototype_test():
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

    return jsonify({'saved': True, 'total_responses': len(merged)}), 200


# ─── GET /api/v1/phase7/readiness ──────────────────────────────────────────

@phase7_bp.route('/phase7/readiness', methods=['GET'])
@limiter.limit('60 per hour')
def get_readiness():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = PrototypeTestData.query.filter_by(user_id=user.id).first()
    responses = record.responses if record else {}

    assessment = assess_scale_readiness(responses)
    can_submit, msg = validate_for_submit(responses)

    return jsonify({
        'scale_readiness': assessment['signal'],
        'scale_score':     assessment['score'],
        'components':      assessment['components'],
        'blockers':        assessment['blockers'],
        'can_submit':      can_submit,
        'submit_message':  msg if not can_submit else None,
    }), 200


# ─── POST /api/v1/phase7/submit ────────────────────────────────────────────

@phase7_bp.route('/phase7/submit', methods=['POST'])
@limiter.limit('10 per hour')
def submit_prototype_test():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = PrototypeTestData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'error': 'No prototype test data found'}), 400

    can_submit, msg = validate_for_submit(record.responses or {})
    if not can_submit:
        return jsonify({'error': msg}), 422

    venture = _active_venture(user.id)
    venture_dict = {'venture_name': venture.idea_raw or 'Your Venture'} if venture else {}

    report_data = generate_report(venture_dict, record.responses or {})

    assessment = assess_scale_readiness(record.responses or {})
    decision   = report_data['decision']

    result = PrototypeTestResult(
        user_id        = user.id,
        venture_id     = venture.id if venture else None,
        result_data    = report_data,
        scale_readiness = assessment['signal'],
        scale_score    = assessment['score'],
        decision       = decision,
        ready_to_scale = report_data.get('ready_to_scale', False),
    )
    db.session.add(result)

    record.completed  = True
    record.updated_at = datetime.utcnow()
    db.session.commit()

    # Sync Assessment record (drives sidebar unlocking)
    try:
        _upsert_assessment_phase7(user.id, report_data.get('ready_to_scale', False))
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    logger.info('Phase7 submit user=%s decision=%s score=%s', user.id, decision, assessment['score'])
    return jsonify({'success': True, 'report': result.to_dict()}), 201


# ─── GET /api/v1/phase7/report ─────────────────────────────────────────────

@phase7_bp.route('/phase7/report', methods=['GET'])
@limiter.limit('60 per hour')
def get_report():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    result = (
        PrototypeTestResult.query
        .filter_by(user_id=user.id)
        .order_by(PrototypeTestResult.generated_at.desc())
        .first()
    )
    if not result:
        return jsonify({'report': None}), 200

    return jsonify({'report': result.to_dict()}), 200


def _upsert_assessment_phase7(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 7 (business_prototype_testing)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='business_prototype_testing').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='business_prototype_testing',
            phase_name='Business Prototype Testing',
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
