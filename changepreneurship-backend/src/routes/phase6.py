"""
Phase 6 API — Sprint 12
========================
CEO Section 6: "Can we build the necessary business components so the venture can actually function?"

Endpoints:
  GET  /api/v1/phase6/business-dev      — load current responses
  PATCH /api/v1/phase6/business-dev     — upsert responses
  GET  /api/v1/phase6/readiness         — live readiness assessment
  POST /api/v1/phase6/submit            — generate Personalized Venture Environment
  GET  /api/v1/phase6/environment       — latest Venture Environment
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.business_development import BusinessDevData, VentureEnvironment
from src.models.venture_record import VentureRecord
from src.services.phase6_business_dev_service import Phase6BusinessDevService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase6_bp = Blueprint('phase6', __name__)
_svc = Phase6BusinessDevService()


def _active_venture(user_id: int) -> VentureRecord | None:
    return (
        VentureRecord.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(VentureRecord.version.desc())
        .first()
    )


def _get_or_create_data(user_id: int, venture_id: int | None) -> BusinessDevData:
    record = BusinessDevData.query.filter_by(user_id=user_id).first()
    if not record:
        record = BusinessDevData(
            user_id=user_id,
            venture_id=venture_id,
            responses={},
        )
        db.session.add(record)
        db.session.flush()
    return record


# ─── GET /api/v1/phase6/business-dev ───────────────────────────────────────

@phase6_bp.route('/phase6/business-dev', methods=['GET'])
@limiter.limit('60 per hour')
def get_business_dev():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = BusinessDevData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'responses': {}, 'completed': False, 'completion_pct': 0}), 200

    total_q = 19
    answered = sum(1 for v in (record.responses or {}).values()
                   if v is not None and str(v).strip())
    pct = int(min(answered / total_q, 1.0) * 100)

    return jsonify({
        'responses':      record.responses or {},
        'completed':      record.completed,
        'completion_pct': pct,
        'updated_at':     record.updated_at.isoformat() if record.updated_at else None,
    }), 200


# ─── PATCH /api/v1/phase6/business-dev ─────────────────────────────────────

@phase6_bp.route('/phase6/business-dev', methods=['PATCH'])
@limiter.limit('120 per hour')
def upsert_business_dev():
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

    total_q = 19
    answered = sum(1 for v in merged.values() if v is not None and str(v).strip())
    pct = int(min(answered / total_q, 1.0) * 100)

    return jsonify({
        'responses':      merged,
        'completion_pct': pct,
        'updated_at':     record.updated_at.isoformat(),
    }), 200


# ─── GET /api/v1/phase6/readiness ──────────────────────────────────────────

@phase6_bp.route('/phase6/readiness', methods=['GET'])
@limiter.limit('60 per hour')
def readiness():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = BusinessDevData.query.filter_by(user_id=user.id).first()
    responses = record.responses if record else {}
    result = _svc.assess_readiness(responses)
    return jsonify(result), 200


# ─── POST /api/v1/phase6/submit ────────────────────────────────────────────

@phase6_bp.route('/phase6/submit', methods=['POST'])
@limiter.limit('20 per hour')
def submit_business_dev():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = BusinessDevData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'error': 'No business development data found. Save responses first.'}), 404

    ok, msg = _svc.validate_for_submit(record.responses or {})
    if not ok:
        return jsonify({'error': msg}), 422

    venture = _active_venture(user.id)
    env_dict = _svc.generate_environment(venture, record.responses)

    env_row = VentureEnvironment(
        user_id=user.id,
        venture_id=venture.id if venture else None,
        environment_data=env_dict,
        readiness_score=env_dict['readiness_score'],
        operational_ready=env_dict['operational_ready'],
        decision=env_dict['decision'],
    )
    db.session.add(env_row)

    record.completed  = True
    record.updated_at = datetime.utcnow()
    db.session.commit()

    # Sync Assessment record (drives sidebar unlocking)
    try:
        _upsert_assessment_phase6(user.id, env_dict['operational_ready'])
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    return jsonify(env_row.to_dict()), 201


# ─── GET /api/v1/phase6/environment ────────────────────────────────────────

@phase6_bp.route('/phase6/environment', methods=['GET'])
@limiter.limit('60 per hour')
def get_environment():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    row = (
        VentureEnvironment.query
        .filter_by(user_id=user.id)
        .order_by(VentureEnvironment.generated_at.desc())
        .first()
    )
    if not row:
        return jsonify({'environment': None}), 200
    return jsonify(row.to_dict()), 200


def _upsert_assessment_phase6(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 6 (business_development)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='business_development').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='business_development',
            phase_name='Business Development',
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


def _upsert_assessment_phase6(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 6 (business_development)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='business_development').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='business_development',
            phase_name='Business Development',
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
