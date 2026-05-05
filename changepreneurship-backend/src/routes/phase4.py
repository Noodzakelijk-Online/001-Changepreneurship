"""
Phase 4 API — Sprint 10
========================
CEO Section 4: "Can this idea become a coherent business?"

Endpoints:
  GET  /api/v1/phase4/pillars          — load current pillar data
  PATCH /api/v1/phase4/pillars         — upsert one or more pillars
  POST /api/v1/phase4/submit           — assess coherence + generate blueprint
  GET  /api/v1/phase4/blueprint        — latest blueprint
  GET  /api/v1/phase4/coherence        — coherence assessment (no submit)
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.business_pillars import (
    BusinessPillarsData, BusinessPillarsBlueprint,
)
from src.models.market_research import MarketContext, MarketValidityReport
from src.models.venture_record import VentureRecord
from src.services.phase4_pillars_service import Phase4PillarsService, PILLAR_KEYS
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase4_bp = Blueprint('phase4', __name__)
_svc = Phase4PillarsService()


def _active_venture(user_id: int) -> VentureRecord | None:
    return (
        VentureRecord.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(VentureRecord.version.desc())
        .first()
    )


def _get_or_create_pillars(user_id: int, venture_id: int | None) -> BusinessPillarsData:
    """Return existing record or create a fresh one."""
    record = BusinessPillarsData.query.filter_by(user_id=user_id).first()
    if not record:
        record = BusinessPillarsData(
            user_id=user_id,
            venture_id=venture_id,
            pillars={},
        )
        db.session.add(record)
        db.session.flush()
    return record


# ─── GET /api/v1/phase4/pillars ─────────────────────────────────────────────

@phase4_bp.route('/phase4/pillars', methods=['GET'])
@limiter.limit('60 per hour')
def get_pillars():
    """Return the current Business Pillars state for the logged-in user."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = BusinessPillarsData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'pillars': {}, 'completed': False, 'completion_pct': 0}), 200

    filled = sum(1 for k in PILLAR_KEYS if (record.pillars or {}).get(k, '').strip())
    completion_pct = int(filled / len(PILLAR_KEYS) * 100)

    return jsonify({
        'pillars': record.pillars or {},
        'completed': record.completed,
        'completion_pct': completion_pct,
        'updated_at': record.updated_at.isoformat() if record.updated_at else None,
    }), 200


# ─── PATCH /api/v1/phase4/pillars ───────────────────────────────────────────

@phase4_bp.route('/phase4/pillars', methods=['PATCH'])
@limiter.limit('60 per hour')
def update_pillars():
    """
    Upsert one or more pillar fields.
    Body: {pillar_key: "text", ...}  (any subset of the 10 pillar keys)
    Also accepts the frontend section-based responses under 'section_responses'.
    """
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    venture = _active_venture(user.id)
    record = _get_or_create_pillars(user.id, venture.id if venture else None)

    current_pillars = dict(record.pillars or {})
    errors = []

    for key, value in data.items():
        if key == 'section_responses':
            # Accept the full section-response blob from the frontend assessment
            if isinstance(value, dict):
                current_pillars['_section_responses'] = value
            continue

        ok, msg = _svc.validate_pillar_update(key, str(value) if value is not None else '')
        if not ok:
            errors.append(msg)
            continue
        current_pillars[key] = str(value).strip()

    if errors:
        return jsonify({'errors': errors}), 400

    record.pillars = current_pillars
    record.updated_at = datetime.utcnow()

    # Auto-complete if all 10 pillars filled
    filled = sum(1 for k in PILLAR_KEYS if current_pillars.get(k, '').strip())
    if filled == len(PILLAR_KEYS) and not record.completed:
        record.completed = True
        record.completed_at = datetime.utcnow() if hasattr(record, 'completed_at') else None

    db.session.commit()

    completion_pct = int(filled / len(PILLAR_KEYS) * 100)
    return jsonify({
        'pillars': record.pillars,
        'completed': record.completed,
        'completion_pct': completion_pct,
    }), 200


# ─── GET /api/v1/phase4/coherence ───────────────────────────────────────────

@phase4_bp.route('/phase4/coherence', methods=['GET'])
@limiter.limit('60 per hour')
def get_coherence():
    """Return coherence assessment of current pillars without saving anything."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    record = BusinessPillarsData.query.filter_by(user_id=user.id).first()
    pillars = record.pillars if record else {}

    assessment = _svc.assess_coherence(pillars or {})
    return jsonify({'coherence': assessment}), 200


# ─── POST /api/v1/phase4/submit ─────────────────────────────────────────────

@phase4_bp.route('/phase4/submit', methods=['POST'])
@limiter.limit('10 per hour')
def submit_phase4():
    """
    Assess coherence and generate the Business Pillars Blueprint.
    Returns the blueprint JSON and saves it.
    """
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'error': 'No active venture. Complete Phase 2 first.'}), 400

    record = BusinessPillarsData.query.filter_by(user_id=user.id).first()
    if not record:
        return jsonify({'error': 'No pillar data found. Fill in at least the critical pillars first.'}), 400

    pillars = record.pillars or {}
    coherence = _svc.assess_coherence(pillars)

    # Fetch market context for richer blueprint
    market_ctx = MarketContext.query.filter_by(user_id=user.id).first()
    market_data = market_ctx.to_dict() if market_ctx else None

    mvr_record = (
        MarketValidityReport.query
        .filter_by(user_id=user.id, venture_id=venture.id)
        .first()
    )
    mvr_data = mvr_record.report_data if mvr_record else None

    blueprint_data = _svc.generate_blueprint(
        venture_record=venture,
        pillars=pillars,
        market_data=market_data,
        mvr=mvr_data,
    )

    # Persist blueprint (upsert)
    existing = BusinessPillarsBlueprint.query.filter_by(
        user_id=user.id, venture_id=venture.id
    ).first()
    if existing:
        existing.blueprint_data = blueprint_data
        existing.coherence_score = coherence['coherence_score']
        existing.ready_for_concept_testing = blueprint_data['ready_for_concept_testing']
        existing.generated_at = datetime.utcnow()
        blueprint = existing
    else:
        blueprint = BusinessPillarsBlueprint(
            user_id=user.id,
            venture_id=venture.id,
            blueprint_data=blueprint_data,
            coherence_score=coherence['coherence_score'],
            ready_for_concept_testing=blueprint_data['ready_for_concept_testing'],
        )
        db.session.add(blueprint)

    # Mark pillars as completed if coherent
    if coherence['is_coherent']:
        record.completed = True
        record.updated_at = datetime.utcnow()

    db.session.commit()

    # Sync Assessment record (drives sidebar unlocking)
    try:
        _upsert_assessment_phase4(user.id, coherence['is_coherent'])
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    return jsonify({
        'blueprint': blueprint_data,
        'blueprint_id': blueprint.id,
        'coherence': coherence,
    }), 200


# ─── GET /api/v1/phase4/blueprint ───────────────────────────────────────────

@phase4_bp.route('/phase4/blueprint', methods=['GET'])
@limiter.limit('60 per hour')
def get_blueprint():
    """Return the latest saved Business Pillars Blueprint."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'blueprint': None}), 200

    blueprint = (
        BusinessPillarsBlueprint.query
        .filter_by(user_id=user.id, venture_id=venture.id)
        .first()
    )
    if not blueprint:
        return jsonify({'blueprint': None}), 200

    return jsonify({
        'blueprint': blueprint.blueprint_data,
        'coherence_score': blueprint.coherence_score,
        'ready_for_concept_testing': blueprint.ready_for_concept_testing,
        'generated_at': blueprint.generated_at.isoformat(),
    }), 200


def _upsert_assessment_phase4(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 4 (business_pillars)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='business_pillars').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='business_pillars',
            phase_name='Business Pillars Planning',
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
