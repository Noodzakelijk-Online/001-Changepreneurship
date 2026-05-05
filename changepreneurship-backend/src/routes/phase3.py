"""
Phase 3 API — Sprint 9
=======================
CEO Section 3.3: "Does the world care?"

Endpoints:
  GET  /api/v1/phase3/assumptions            — assumptions from Phase 2 CVC
  POST /api/v1/phase3/evidence               — submit an evidence item
  GET  /api/v1/phase3/evidence               — list evidence for active venture
  DELETE /api/v1/phase3/evidence/<id>        — remove evidence item
  POST /api/v1/phase3/competitors            — add a competitor
  GET  /api/v1/phase3/competitors            — list competitors
  DELETE /api/v1/phase3/competitors/<id>     — remove competitor
  POST /api/v1/phase3/submit                 — evaluate + generate Market Validity Report
  GET  /api/v1/phase3/report                 — latest Market Validity Report
  GET  /api/v1/phase3/interview-script       — AI-prepared interview script
  PATCH /api/v1/phase3/market-data           — save market context (pain, WTP, size)
"""
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db, Assessment
from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport
from src.models.venture_record import (
    VentureRecord, EvidenceItem,
    VENTURE_STATUS_VALIDATED,
    EVIDENCE_STRENGTH_ORDER, EVIDENCE_TYPE_CHOICES,
)
from src.services.phase3_market_service import Phase3MarketService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase3_bp = Blueprint('phase3', __name__)
_svc = Phase3MarketService()


def _active_venture(user_id: int) -> VentureRecord | None:
    return (
        VentureRecord.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(VentureRecord.version.desc())
        .first()
    )


# ─── GET /api/v1/phase3/assumptions ─────────────────────────────────────────

@phase3_bp.route('/phase3/assumptions', methods=['GET'])
@limiter.limit('60 per hour')
def get_assumptions():
    """Return assumptions list from the active VentureRecord (Phase 2 CVC)."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'assumptions': [], 'message': 'Complete Phase 2 first'}), 200

    return jsonify({'assumptions': venture.assumptions or [], 'venture_id': venture.id}), 200


# ─── POST /api/v1/phase3/evidence ───────────────────────────────────────────

@phase3_bp.route('/phase3/evidence', methods=['POST'])
@limiter.limit('60 per hour')
def add_evidence():
    """
    Submit an evidence item.
    Body: {evidence_type, strength, description, source?, evidence_date?, affects_dimensions?}
    """
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    data = request.get_json(silent=True) or {}
    evidence_type = (data.get('evidence_type') or '').upper()
    strength      = (data.get('strength') or 'DIRECT').upper()
    description   = (data.get('description') or '').strip()

    if evidence_type not in EVIDENCE_TYPE_CHOICES:
        return jsonify({'error': f'Invalid evidence_type. Must be one of: {EVIDENCE_TYPE_CHOICES}'}), 400
    if strength not in EVIDENCE_STRENGTH_ORDER:
        return jsonify({'error': f'Invalid strength. Must be one of: {EVIDENCE_STRENGTH_ORDER}'}), 400
    if not description:
        return jsonify({'error': 'description is required'}), 400
    if len(description) > 2000:
        return jsonify({'error': 'description too long (max 2000 chars)'}), 400

    venture = _active_venture(user.id)

    # Parse optional date
    evidence_date = None
    raw_date = data.get('evidence_date')
    if raw_date:
        try:
            evidence_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            pass

    item = EvidenceItem(
        user_id=user.id,
        venture_id=venture.id if venture else None,
        evidence_type=evidence_type,
        strength=strength,
        description=description,
        source=data.get('source', '')[:255],
        evidence_date=evidence_date,
        affects_dimensions=data.get('affects_dimensions', []),
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'evidence': item.to_dict()}), 201


# ─── GET /api/v1/phase3/evidence ────────────────────────────────────────────

@phase3_bp.route('/phase3/evidence', methods=['GET'])
@limiter.limit('60 per hour')
def list_evidence():
    """List all evidence items for the user's active venture."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'evidence': []}), 200

    items = EvidenceItem.query.filter_by(user_id=user.id).order_by(EvidenceItem.created_at.desc()).all()
    return jsonify({'evidence': [i.to_dict() for i in items], 'count': len(items)}), 200


# ─── DELETE /api/v1/phase3/evidence/<id> ────────────────────────────────────

@phase3_bp.route('/phase3/evidence/<int:item_id>', methods=['DELETE'])
@limiter.limit('30 per hour')
def delete_evidence(item_id):
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    item = EvidenceItem.query.filter_by(id=item_id, user_id=user.id).first()
    if not item:
        return jsonify({'error': 'Not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'deleted': True}), 200


# ─── POST /api/v1/phase3/competitors ────────────────────────────────────────

@phase3_bp.route('/phase3/competitors', methods=['POST'])
@limiter.limit('60 per hour')
def add_competitor():
    """Add a competitor entry."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    data = request.get_json(silent=True) or {}
    ok, msg = _svc.validate_competitor(data)
    if not ok:
        return jsonify({'error': msg}), 400

    venture = _active_venture(user.id)

    entry = CompetitorEntry(
        user_id=user.id,
        venture_id=venture.id if venture else None,
        name=data['name'].strip()[:200],
        description=data.get('description', '')[:500],
        strengths=data.get('strengths', '')[:500],
        weaknesses=data.get('weaknesses', '')[:500],
        positioning=data.get('positioning', '')[:200],
        is_direct=bool(data.get('is_direct', True)),
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'competitor': entry.to_dict()}), 201


# ─── GET /api/v1/phase3/competitors ─────────────────────────────────────────

@phase3_bp.route('/phase3/competitors', methods=['GET'])
@limiter.limit('60 per hour')
def list_competitors():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'competitors': []}), 200

    entries = CompetitorEntry.query.filter_by(user_id=user.id).order_by(CompetitorEntry.created_at.asc()).all()
    return jsonify({'competitors': [e.to_dict() for e in entries], 'count': len(entries)}), 200


# ─── DELETE /api/v1/phase3/competitors/<id> ──────────────────────────────────

@phase3_bp.route('/phase3/competitors/<int:entry_id>', methods=['DELETE'])
@limiter.limit('30 per hour')
def delete_competitor(entry_id):
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    entry = CompetitorEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return jsonify({'error': 'Not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'deleted': True}), 200


# ─── PATCH /api/v1/phase3/market-data ───────────────────────────────────────

@phase3_bp.route('/phase3/market-data', methods=['PATCH'])
@limiter.limit('30 per hour')
def update_market_data():
    """
    Save market context: pain intensity, WTP, target segment, etc.
    Creates or updates MarketContext for the user.
    """
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    data = request.get_json(silent=True) or {}

    PAIN_OPTIONS = ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    pain = (data.get('pain_intensity') or 'MEDIUM').upper()
    if pain not in PAIN_OPTIONS:
        return jsonify({'error': f'pain_intensity must be one of {PAIN_OPTIONS}'}), 400

    venture = _active_venture(user.id)

    ctx = MarketContext.query.filter_by(user_id=user.id).first()
    if not ctx:
        ctx = MarketContext(user_id=user.id, venture_id=venture.id if venture else None)
        db.session.add(ctx)

    ctx.target_segment        = (data.get('target_segment') or '')[:300]
    ctx.pain_intensity        = pain
    ctx.willingness_to_pay    = bool(data.get('willingness_to_pay', False))
    ctx.estimated_price_range = (data.get('estimated_price_range') or '')[:100]
    ctx.market_timing         = (data.get('market_timing') or '')[:200]
    ctx.market_size_note      = (data.get('market_size_note') or '')[:500]
    ctx.updated_at            = datetime.utcnow()

    db.session.commit()
    return jsonify({'market_data': ctx.to_dict()}), 200


# ─── GET /api/v1/phase3/market-data ─────────────────────────────────────────

@phase3_bp.route('/phase3/market-data', methods=['GET'])
@limiter.limit('60 per hour')
def get_market_data():
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    ctx = MarketContext.query.filter_by(user_id=user.id).first()
    if not ctx:
        return jsonify({'market_data': None}), 200

    return jsonify({'market_data': ctx.to_dict()}), 200


# ─── POST /api/v1/phase3/submit ─────────────────────────────────────────────

@phase3_bp.route('/phase3/submit', methods=['POST'])
@limiter.limit('10 per hour')
def submit_phase3():
    """
    Evaluate all evidence + generate Market Validity Report.
    Saves the MVR to DB and updates VentureRecord status to VALIDATED if ready.
    """
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'error': 'No active venture. Complete Phase 2 first.'}), 400

    evidence_items = EvidenceItem.query.filter_by(user_id=user.id).all()
    competitors    = CompetitorEntry.query.filter_by(user_id=user.id).all()
    ctx            = MarketContext.query.filter_by(user_id=user.id).first()

    market_data = ctx.to_dict() if ctx else {
        'pain_intensity': 'MEDIUM',
        'willingness_to_pay': False,
        'target_segment': '',
    }

    mvr_data = _svc.generate_market_validity_report(
        venture_record=venture,
        evidence_items=evidence_items,
        competitors=[c.to_dict() for c in competitors],
        market_data=market_data,
    )

    # Persist MVR
    existing = MarketValidityReport.query.filter_by(user_id=user.id, venture_id=venture.id).first()
    if existing:
        existing.report_data  = mvr_data
        existing.generated_at = datetime.utcnow()
        report = existing
    else:
        report = MarketValidityReport(
            user_id=user.id,
            venture_id=venture.id,
            report_data=mvr_data,
        )
        db.session.add(report)

    # Upgrade venture status if evidence is strong enough
    if mvr_data['ready_for_business_pillars'] and venture.status == 'CLARIFIED':
        venture.status = VENTURE_STATUS_VALIDATED

    db.session.commit()

    # Sync Assessment record (drives sidebar unlocking)
    try:
        _upsert_assessment_phase3(user.id, bool(mvr_data['ready_for_business_pillars']))
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user.id, exc)

    return jsonify({'report': mvr_data, 'report_id': report.id}), 200


# ─── GET /api/v1/phase3/report ──────────────────────────────────────────────

@phase3_bp.route('/phase3/report', methods=['GET'])
@limiter.limit('60 per hour')
def get_report():
    """Return the latest Market Validity Report."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'report': None}), 200

    report = (
        MarketValidityReport.query
        .filter_by(user_id=user.id, venture_id=venture.id)
        .first()
    )
    if not report:
        return jsonify({'report': None}), 200

    return jsonify({'report': report.report_data, 'generated_at': report.generated_at.isoformat()}), 200


# ─── GET /api/v1/phase3/interview-script ────────────────────────────────────

def _upsert_assessment_phase3(user_id: int, force_complete: bool) -> Assessment:
    """Ensure Assessment record exists for Phase 3 (market_research)."""
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id='market_research').first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id='market_research',
            phase_name='Market Research',
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


@phase3_bp.route('/phase3/interview-script', methods=['GET'])
@limiter.limit('20 per hour')
def get_interview_script():
    """Generate a personalised interview/outreach script from the venture concept."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify(error), code

    venture = _active_venture(user.id)
    if not venture:
        return jsonify({'error': 'Complete Phase 2 first to generate interview script'}), 400

    script = _svc.generate_interview_script(venture)
    return jsonify({'script': script}), 200
