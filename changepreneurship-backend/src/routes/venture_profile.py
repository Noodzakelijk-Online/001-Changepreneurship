"""
Venture Profile API — Sprint 14 / Sprint 16
==============================================
CEO Concept: Cross-phase synthesis — "Who are you, what are you building, and how far have you come?"
Sprint 16 adds: Founder Operating Matrix (all 13 dims + status labels), pattern tags,
                evidence breakdown, ai_narrative, operating_recommendation, phase gate statuses.

Endpoints:
  GET /api/v1/ventures/profile  — full cross-phase venture profile (all deliverables)
  GET /api/v1/ventures/active   — active VentureRecord only (for dashboard)
"""
import logging

from flask import Blueprint, jsonify

from src.models.assessment import db
from src.models.business_development import VentureEnvironment
from src.models.business_pillars import BusinessPillarsBlueprint
from src.models.concept_testing import ConceptTestResult
from src.models.founder_profile import FounderReadinessProfile, PhaseGate
from src.models.market_research import MarketContext, MarketValidityReport
from src.models.prototype_testing import PrototypeTestResult
from src.models.venture_record import EvidenceItem, VentureRecord
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

venture_profile_bp = Blueprint('venture_profile', __name__)

# All 13 dimension names (includes legal_employment + health_energy added in Sprint 16)
_ALL_DIMENSIONS = [
    'financial_readiness',
    'time_capacity',
    'personal_stability',
    'motivation_quality',
    'skills_experience',
    'founder_idea_fit',
    'founder_market_fit',
    'idea_clarity',
    'market_validity',
    'business_model',
    'legal_employment',
    'health_energy',
    'network_mentorship',
]

# Human-readable labels for each dimension
_DIM_LABELS = {
    'financial_readiness':  'Financial Readiness',
    'time_capacity':        'Time & Capacity',
    'personal_stability':   'Personal Stability',
    'motivation_quality':   'Motivation & Purpose',
    'skills_experience':    'Skills & Experience',
    'founder_idea_fit':     'Founder-Idea Fit',
    'founder_market_fit':   'Founder-Market Fit',
    'idea_clarity':         'Idea Clarity',
    'market_validity':      'Market Validity',
    'business_model':       'Business Model',
    'legal_employment':     'Legal & Employment',
    'health_energy':        'Health & Energy',
    'network_mentorship':   'Network & Mentorship',
}

# Map level (0-5) → status label (CEO doc: Healthy→Strong, OK→Adequate, Warning, SoftBlock, HardBlock, HardStop)
_LEVEL_LABELS = {
    0: 'Strong',
    1: 'Adequate',
    2: 'Watch',
    3: 'Soft Block',
    4: 'Hard Block',
    5: 'Hard Stop',
}

# Evidence strength ordering (weakest → strongest)
_EVIDENCE_STRENGTHS = ['BELIEF', 'OPINION', 'AI_RESEARCH', 'DESK_RESEARCH', 'INDIRECT', 'DIRECT', 'BEHAVIORAL']


def _level_label(level):
    if level is None:
        return 'Unknown'
    return _LEVEL_LABELS.get(int(level), 'Unknown')


def _compute_pattern_tags(frp):
    """Derive pattern tags from dimension levels + signals. CEO doc section 5.5 tag list."""
    tags = []
    if frp is None:
        return tags

    def lvl(dim):
        v = getattr(frp, f'{dim}_level', None)
        return int(v) if v is not None else None

    # Financial constraint
    if lvl('financial_readiness') is not None and lvl('financial_readiness') >= 3:
        tags.append('Financial constraint')
    elif lvl('financial_readiness') == 2:
        tags.append('Financial watch')

    # Burnout / overload
    if getattr(frp, 'burnout_signal', False):
        tags.append('Burnout watch')
    if getattr(frp, 'overload_signal', False):
        tags.append('Overload risk')

    # Time constraint
    if lvl('time_capacity') is not None and lvl('time_capacity') >= 3:
        tags.append('Low time capacity')

    # Skills gap
    if lvl('skills_experience') is not None and lvl('skills_experience') >= 3:
        tags.append('Skills gap')

    # Network / mentor gap
    if lvl('network_mentorship') is not None and lvl('network_mentorship') >= 3:
        tags.append('Mentor needed')

    # Legal flag
    if lvl('legal_employment') is not None and lvl('legal_employment') >= 3:
        tags.append('Legal employment risk')

    # Health / energy flag
    if lvl('health_energy') is not None and lvl('health_energy') >= 2:
        tags.append('Health & energy watch')

    # Founder-idea / founder-market fit
    if lvl('founder_idea_fit') is not None and lvl('founder_idea_fit') >= 3:
        tags.append('Weak founder-idea fit')
    if lvl('founder_market_fit') is not None and lvl('founder_market_fit') >= 3:
        tags.append('Market access gap')

    # Vision strength (low motivation levels = strong dimension = level 0-1)
    if lvl('motivation_quality') is not None and lvl('motivation_quality') <= 1:
        tags.append('Vision strength')

    # Evidence weakness (market_validity high level)
    if lvl('market_validity') is not None and lvl('market_validity') >= 3:
        tags.append('Evidence weakness')

    # Business model gap
    if lvl('business_model') is not None and lvl('business_model') >= 3:
        tags.append('Business model gap')

    # Route-based tags
    route = (frp.recommended_route or '').upper()
    if route == 'STOP':
        tags.append('Hard Stop active')
    elif route == 'PAUSE':
        tags.append('Pause recommended')
    elif route == 'PIVOT':
        tags.append('Pivot signal')

    # Compensation applied
    if frp.compensation_rules_applied:
        tags.append('Compensated gaps present')

    return tags


def _compute_operating_recommendation(frp):
    """Derive a short operating recommendation from route + readiness level."""
    if frp is None:
        return None
    route = (frp.recommended_route or 'CONTINUE').upper()
    level = int(frp.overall_readiness_level or 0)

    if route == 'STOP' or level == 5:
        return 'Stop current direction. Address hard stops before any further venture activity.'
    if route == 'PAUSE' or level == 4:
        return 'Pause active development. Resolve hard blockers (financial, legal, personal) before proceeding.'
    if level == 3:
        return 'Proceed cautiously. Resolve soft blockers in parallel with low-risk validation steps.'
    if route == 'PIVOT':
        return 'Explore a strategic pivot. Current direction has significant unresolved gaps.'
    if level == 2:
        return 'Continue with monitoring. Watch-level dimensions need attention alongside validation.'
    return 'Continue. Focus on evidence collection and customer validation as the next priority.'


@venture_profile_bp.get('/ventures/active')
@limiter.limit('120/minute')
def get_active_venture():
    """Return the active VentureRecord for the authenticated user (dashboard use)."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code

    venture = VentureRecord.query.filter_by(
        user_id=user.id, is_active=True
    ).order_by(VentureRecord.id.desc()).first()

    if not venture:
        return jsonify({'venture': None})

    return jsonify({'venture': {
        'id':                        venture.id,
        'status':                    venture.status,
        'type':                      venture.venture_type,
        'idea_raw':                  venture.idea_raw,
        'idea_clarified':            venture.idea_clarified,
        'problem_statement':         venture.problem_statement,
        'target_user_hypothesis':    venture.target_user_hypothesis,
        'value_proposition':         venture.value_proposition,
        'founder_motivation_summary': venture.founder_motivation_summary,
        'updated_at':                venture.updated_at.isoformat() if venture.updated_at else None,
    }})


@venture_profile_bp.get('/ventures/profile')
@limiter.limit('60/minute')
def get_venture_profile():
    """Return a full cross-phase synthesis profile for the authenticated user."""
    user, _s, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code

    uid = user.id

    # ── Venture (Phase 2 anchor) ─────────────────────────────────────────────
    venture = VentureRecord.query.filter_by(user_id=uid, is_active=True).order_by(
        VentureRecord.id.desc()
    ).first()

    venture_data = None
    if venture:
        venture_data = {
            'id':                        venture.id,
            'status':                    venture.status,
            'type':                      venture.venture_type,
            'idea_raw':                  venture.idea_raw,
            'idea_clarified':            venture.idea_clarified,
            'problem_statement':         venture.problem_statement,
            'target_user_hypothesis':    venture.target_user_hypothesis,
            'value_proposition':         venture.value_proposition,
            'founder_motivation_summary': venture.founder_motivation_summary,
            'updated_at':                venture.updated_at.isoformat() if venture.updated_at else None,
        }

    # ── Phase 1 deliverable — Founder Readiness Profile + Founder Operating Matrix ──
    frp = FounderReadinessProfile.query.filter_by(
        user_id=uid, is_latest=True
    ).order_by(FounderReadinessProfile.id.desc()).first()

    phase1 = None
    founder_matrix = None
    if frp:
        # All 13 dimensions with score, level, status_label, display_name
        dims = {}
        for d in _ALL_DIMENSIONS:
            score = getattr(frp, f'{d}_score', None)
            level = getattr(frp, f'{d}_level', None)
            dims[d] = {
                'score':        score,
                'level':        level,
                'status_label': _level_label(level),
                'label':        _DIM_LABELS.get(d, d),
            }

        phase1 = {
            'overall_readiness_level':  frp.overall_readiness_level,
            'overall_status_label':     _level_label(frp.overall_readiness_level),
            'founder_type':             frp.founder_type,
            'recommended_route':        frp.recommended_route,
            'dimensions':               dims,
            'active_blockers':          frp.active_blockers or [],
            'compensation_rules':       frp.compensation_rules_applied or [],
            'burnout_signal':           bool(frp.burnout_signal),
            'overload_signal':          bool(frp.overload_signal),
            'detected_scenario':        frp.detected_scenario,
            'ai_narrative':             frp.ai_narrative,
            'ai_confidence':            frp.ai_confidence,
        }

        # Founder Operating Matrix (CEO doc section 5.5)
        founder_matrix = {
            'dimensions':               dims,
            'overall_readiness_level':  frp.overall_readiness_level,
            'overall_status_label':     _level_label(frp.overall_readiness_level),
            'recommended_route':        frp.recommended_route,
            'operating_recommendation': _compute_operating_recommendation(frp),
            'pattern_tags':             _compute_pattern_tags(frp),
            'active_blockers':          frp.active_blockers or [],
            'compensation_rules':       frp.compensation_rules_applied or [],
            'burnout_signal':           bool(frp.burnout_signal),
            'overload_signal':          bool(frp.overload_signal),
            'ai_narrative':             frp.ai_narrative,
            'ai_confidence':            frp.ai_confidence,
        }

    # ── Phase 3 deliverable — Market Validity Report ─────────────────────────
    mvr = None
    if venture:
        mvr = MarketValidityReport.query.filter_by(
            user_id=uid, venture_id=venture.id
        ).order_by(MarketValidityReport.id.desc()).first()

    mkt_ctx = MarketContext.query.filter_by(user_id=uid).first()

    # Evidence breakdown by strength
    evidence_items = EvidenceItem.query.filter_by(user_id=uid).all()
    evidence_count = len(evidence_items)
    evidence_by_strength = {}
    for item in evidence_items:
        s = item.strength or 'BELIEF'
        evidence_by_strength[s] = evidence_by_strength.get(s, 0) + 1

    # Compute quality score: weight stronger evidence types higher
    _STRENGTH_WEIGHT = {'BELIEF': 0, 'OPINION': 1, 'AI_RESEARCH': 1, 'DESK_RESEARCH': 2,
                        'INDIRECT': 3, 'DIRECT': 4, 'BEHAVIORAL': 5}
    if evidence_count > 0:
        raw_score = sum(_STRENGTH_WEIGHT.get(i.strength or 'BELIEF', 0) for i in evidence_items)
        evidence_quality_score = min(100, int(raw_score / evidence_count * 20))
    else:
        evidence_quality_score = 0

    phase3 = None
    if mvr:
        rd = mvr.report_data or {}
        phase3 = {
            'validity_score': rd.get('validity_score'),
            'verdict':        rd.get('verdict'),
            'market_data':    rd.get('market_data'),
            'generated_at':   mvr.generated_at.isoformat() if mvr.generated_at else None,
        }

    market = {
        'target_segment':       mkt_ctx.target_segment if mkt_ctx else None,
        'pain_intensity':       mkt_ctx.pain_intensity if mkt_ctx else None,
        'willingness_to_pay':   mkt_ctx.willingness_to_pay if mkt_ctx else None,
        'evidence_count':       evidence_count,
        'evidence_by_strength': evidence_by_strength,
        'evidence_quality_score': evidence_quality_score,
    }

    # ── Phase 4 deliverable — Business Pillars Blueprint ─────────────────────
    bpb = BusinessPillarsBlueprint.query.filter_by(user_id=uid).order_by(
        BusinessPillarsBlueprint.id.desc()
    ).first()

    phase4 = None
    if bpb:
        phase4 = {
            'coherence_score':           bpb.coherence_score,
            'ready_for_concept_testing': bpb.ready_for_concept_testing,
            'generated_at':              bpb.generated_at.isoformat() if bpb.generated_at else None,
        }

    # ── Phase 5 deliverable — Concept Test Result ────────────────────────────
    ctr = ConceptTestResult.query.filter_by(user_id=uid).order_by(
        ConceptTestResult.id.desc()
    ).first()

    phase5 = None
    if ctr:
        phase5 = {
            'adoption_signal':        ctr.adoption_signal,
            'decision':               ctr.decision,
            'ready_for_business_dev': ctr.ready_for_business_dev,
            'generated_at':           ctr.generated_at.isoformat() if ctr.generated_at else None,
        }

    # ── Phase 6 deliverable — Venture Environment ────────────────────────────
    ve = VentureEnvironment.query.filter_by(user_id=uid).order_by(
        VentureEnvironment.id.desc()
    ).first()

    phase6 = None
    if ve:
        phase6 = {
            'readiness_score':   ve.readiness_score,
            'operational_ready': ve.operational_ready,
            'decision':          ve.decision,
            'generated_at':      ve.generated_at.isoformat() if ve.generated_at else None,
        }

    # ── Phase 7 deliverable — Prototype Test Result ──────────────────────────
    ptr = PrototypeTestResult.query.filter_by(user_id=uid).order_by(
        PrototypeTestResult.id.desc()
    ).first()

    phase7 = None
    if ptr:
        phase7 = {
            'scale_readiness': ptr.scale_readiness,
            'scale_score':     ptr.scale_score,
            'decision':        ptr.decision,
            'ready_to_scale':  ptr.ready_to_scale,
            'generated_at':    ptr.generated_at.isoformat() if ptr.generated_at else None,
        }

    # ── Phase gates ───────────────────────────────────────────────────────────
    gates_raw = PhaseGate.query.filter_by(user_id=uid).all()
    phase_gates = {
        g.phase_number: {
            'status':          g.status,
            'blocking_reason': g.blocking_reason,
            'blockers':        g.blockers or [],
            'completed_at':    g.completed_at.isoformat() if g.completed_at else None,
        }
        for g in gates_raw
    }

    # ── Deliverables count ────────────────────────────────────────────────────
    deliverables = {
        'phase1': phase1,
        'phase3': phase3,
        'phase4': phase4,
        'phase5': phase5,
        'phase6': phase6,
        'phase7': phase7,
    }
    completed_count = sum(1 for v in deliverables.values() if v is not None)
    if venture_data:
        completed_count += 1  # Phase 2 counts as done when venture exists

    return jsonify({
        'venture':          venture_data,
        'founder_matrix':   founder_matrix,
        'deliverables':     deliverables,
        'market':           market,
        'phase_gates':      phase_gates,
        'completed_phases': completed_count,
        'total_phases':     7,
    })
