"""
Phase 1 API Route — /api/v1/phase1/submit
==========================================
Orchestrates the 4-layer Phase 1 evaluation:
  Layer 1: Phase1RuleEngine (fixed rules) — always runs first
  Layer 2: FounderReadinessProfile (DB persistence)
  Layer 3: Phase1NarrativeService (AI reasoning) — after Layer 1
  Layer 4: PhaseGate management (unlock / lock gates)
"""
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from src.models.assessment import db
from src.models.founder_profile import FounderReadinessProfile, PhaseGate, initialize_phase_gates
from src.models.assessment import Assessment
from src.models.user_action import UserAction, AUTO_APPROVE
from src.services.phase1_rule_engine import Phase1RuleEngine, LEVEL_HARD_STOP, LEVEL_HARD_BLOCK
from src.services.phase1_narrative_service import Phase1NarrativeService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

logger = logging.getLogger(__name__)

phase1_bp = Blueprint('phase1', __name__)
_rule_engine = Phase1RuleEngine()
_narrative_service = Phase1NarrativeService()


@phase1_bp.route('/phase1/submit', methods=['POST'])
@limiter.limit('10 per hour')
def submit_phase1():
    """
    Evaluate Phase 1 (Self-Discovery) for the authenticated user.

    Request body: JSON dict of assessment responses (see Phase1RuleEngine.evaluate_all docstring)
    Returns: Full evaluation result including AI narrative and phase gate states.
    """
    # --- Auth ---
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify({'error': error}), status_code

    # --- Validate input ---
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    user_id = user.id

    # --- Layer 1: Rule Engine (pure Python, no DB, no AI) ---
    try:
        result = _rule_engine.evaluate_all(data)
    except Exception as exc:
        logger.exception("Phase1RuleEngine failed for user %s: %s", user_id, exc)
        return jsonify({'error': 'Rule engine evaluation failed', 'detail': str(exc)}), 500

    # --- Layer 2: Persist to DB ---
    try:
        profile = _upsert_profile(user_id, result, data)
    except Exception as exc:
        logger.exception("Failed to persist FounderReadinessProfile for user %s: %s", user_id, exc)
        return jsonify({'error': 'Failed to save assessment profile'}), 500

    # --- Layer 4 (gate management) runs before AI to avoid spending tokens on hard-stops ---
    try:
        gates = _update_phase_gates(user_id, result)
    except Exception as exc:
        logger.exception("Phase gate update failed for user %s: %s", user_id, exc)
        gates = {}  # Non-fatal — return what we have

    # --- Action Loop: auto-create first UserAction based on routing ---
    first_action = None
    try:
        if result.overall_level < LEVEL_HARD_STOP:
            first_action = _create_first_action(user_id, result, profile)
    except Exception as exc:
        logger.warning("Action loop failed for user %s: %s — skipping", user_id, exc)

    # --- Layer 3: AI Narrative (after rule engine, may fail gracefully) ---
    try:
        narrative = _narrative_service.generate_narrative(result, data)
    except Exception as exc:
        logger.warning("Narrative service failed for user %s: %s — using fallback", user_id, exc)
        narrative = {
            'founder_readiness_narrative': '',
            'primary_strength': '',
            'primary_risk': '',
            'next_step_explanation': '',
            'what_not_to_do': [],
            'confidence': 'LOW',
            'is_template': True,
        }

    # --- Persist AI narrative back to profile ---
    try:
        if narrative.get('founder_readiness_narrative'):
            profile.ai_narrative = narrative['founder_readiness_narrative']
            db.session.commit()
    except Exception:
        pass  # Non-fatal

    # --- Sync Assessment record (drives sidebar unlocking) ---
    try:
        is_complete = result.overall_level < LEVEL_HARD_BLOCK
        _upsert_assessment(user_id, 'self_discovery', 'Self Discovery Assessment', is_complete)
    except Exception as exc:
        logger.warning("Assessment sync failed for user %s: %s — non-fatal", user_id, exc)

    return jsonify(_build_response(profile, result, narrative, gates, first_action)), 200


def _upsert_assessment(user_id: int, phase_id: str, phase_name: str, force_complete: bool) -> Assessment:
    """
    Ensure an Assessment record exists for user + phase_id.
    Creates it if absent; marks is_completed=True when force_complete.
    This drives the ProgressDashboardService phase-gate unlocking.
    """
    assessment = Assessment.query.filter_by(user_id=user_id, phase_id=phase_id).first()
    if not assessment:
        assessment = Assessment(
            user_id=user_id,
            phase_id=phase_id,
            phase_name=phase_name,
            started_at=datetime.utcnow(),
        )
        db.session.add(assessment)

    if force_complete and not assessment.is_completed:
        assessment.is_completed = True
        assessment.progress_percentage = 100.0
        assessment.completed_at = datetime.utcnow()
    elif not force_complete and assessment.progress_percentage < 50:
        assessment.progress_percentage = 50.0  # Mark as in-progress

    db.session.commit()
    return assessment


def _upsert_profile(user_id: int, result, raw_responses: dict) -> FounderReadinessProfile:
    """
    Create a new versioned FounderReadinessProfile, marking any existing
    profiles for this user as is_latest=False.
    """
    # Determine next version number
    latest = (
        FounderReadinessProfile.query
        .filter_by(user_id=user_id)
        .order_by(FounderReadinessProfile.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1

    # Mark all previous profiles as not latest
    if latest:
        (
            FounderReadinessProfile.query
            .filter_by(user_id=user_id, is_latest=True)
            .update({'is_latest': False})
        )

    profile = FounderReadinessProfile(
        user_id=user_id,
        version=next_version,
        is_latest=True,

        # Dimension scores
        financial_readiness_score=result.financial.score,
        financial_readiness_level=result.financial.level,
        time_capacity_score=result.time_capacity.score,
        time_capacity_level=result.time_capacity.level,
        personal_stability_score=result.personal_stability.score,
        personal_stability_level=result.personal_stability.level,
        motivation_quality_score=result.motivation_quality.score,
        motivation_quality_level=result.motivation_quality.level,
        skills_experience_score=result.skills_experience.score,
        skills_experience_level=result.skills_experience.level,
        idea_clarity_score=result.idea_clarity.score,
        idea_clarity_level=result.idea_clarity.level,
        founder_idea_fit_score=result.founder_idea_fit.score,
        founder_idea_fit_level=result.founder_idea_fit.level,
        # legal_employment maps to strategic_position column (pre-migration name)
        strategic_position_score=result.legal_employment.score,
        strategic_position_level=result.legal_employment.level,
        # health_energy maps to evidence_quality column (pre-migration name)
        evidence_quality_score=result.health_energy.score,
        evidence_quality_level=result.health_energy.level,
        founder_market_fit_score=result.founder_market_fit.score,
        founder_market_fit_level=result.founder_market_fit.level,
        market_validity_score=result.market_validity.score,
        market_validity_level=result.market_validity.level,
        business_model_score=result.business_model.score,
        business_model_level=result.business_model.level,
        network_mentorship_score=result.network_mentorship.score,
        network_mentorship_level=result.network_mentorship.level,

        # Composite
        overall_readiness_level=result.overall_level,
        recommended_route=result.recommended_route,
        founder_type=result.founder_type,
        active_blockers=result.active_blockers,
        compensation_rules_applied=result.compensation_rules,
        burnout_signal_detected=result.burnout_signal,
        overload_signal_detected=result.overload_signal,
        detected_scenario=result.detected_scenario,
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def _update_phase_gates(user_id: int, result) -> dict:
    """
    Ensure Phase 1 gate is IN_PROGRESS (or COMPLETED if no blockers),
    and propagate locks to Phase 2-7. Initialises gates if this is the first run.
    """
    # Ensure phase gates exist
    existing_gates = PhaseGate.query.filter_by(user_id=user_id).count()
    if existing_gates == 0:
        initialize_phase_gates(user_id)

    gate1 = PhaseGate.query.filter_by(user_id=user_id, phase_number=1).first()
    if gate1:
        if result.overall_level >= LEVEL_HARD_STOP:
            gate1.status = 'BLOCKED'
            gate1.blocking_reason = (
                'Critical blocker detected. Review the details and resolve before continuing.'
            )
        elif result.overall_level >= LEVEL_HARD_BLOCK:
            gate1.status = 'IN_PROGRESS'
            gate1.blockers = result.active_blockers[:5]
        else:
            gate1.status = 'IN_PROGRESS'
            gate1.blockers = result.active_blockers[:5]

    db.session.commit()

    # Build summary dict for response
    gates = {}
    all_gates = PhaseGate.query.filter_by(user_id=user_id).all()
    for g in all_gates:
        gates[str(g.phase_number)] = g.status

    return gates


def _create_first_action(user_id: int, result, profile: FounderReadinessProfile):
    """
    Sprint 7 — Phase 1 → Action Loop.

    After Phase 1 assessment, immediately create the first proposed action
    so the user is never left on an empty state. The action type depends on
    what the rule engine diagnosed:
      - HARD_BLOCK / STABILIZE route → SEARCH_MENTORS (free action, no capital)
      - ACCELERATE / DEEP_TECH       → DRAFT_DOCUMENT (business plan start)
      - Everything else              → SEARCH_MENTORS (default first step)

    We check for dedup — if the same action was already proposed today,
    don't create another one.
    """
    from src.services.phase1_rule_engine import ROUTE_ACCELERATE, ROUTE_DEEP_TECH  # local import to avoid circular

    # Pick action type based on routing
    if result.recommended_route in (ROUTE_ACCELERATE, ROUTE_DEEP_TECH):
        action_type = 'DRAFT_DOCUMENT'
        rationale = (
            f"Phase 1 complete. Your profile suggests accelerated readiness "
            f"(route: {result.recommended_route}). Start drafting your business concept document."
        )
        action_data = {
            'document_type': 'business_concept',
            'phase': 1,
            'founder_type': result.founder_type,
            'route': result.recommended_route,
        }
    else:
        action_type = 'SEARCH_MENTORS'
        rationale = (
            f"Phase 1 complete. Next step: find a mentor who has navigated "
            f"your specific situation (route: {result.recommended_route}). "
            f"This costs nothing and can unlock Phase 2."
        )
        action_data = {
            'search_context': {
                'route': result.recommended_route,
                'founder_type': result.founder_type,
                'active_blockers': result.active_blockers[:3],
            }
        }

    # Dedup: skip if same action_type already PROPOSED or APPROVED for this user today
    from datetime import date
    existing = (
        UserAction.query
        .filter(
            UserAction.user_id == user_id,
            UserAction.action_type == action_type,
            UserAction.approval_status.in_(['PROPOSED', 'APPROVED', 'QUEUED']),
        )
        .first()
    )
    if existing:
        logger.info("Action loop: dedup — %s already exists for user %s (id=%s)",
                    action_type, user_id, existing.id)
        return existing

    action = UserAction(
        user_id=user_id,
        action_type=action_type,
        action_data=action_data,
        rationale=rationale,
        approval_status='PROPOSED',
    )

    # Auto-approvable actions (search, draft) don't need explicit user sign-off
    if action_type in AUTO_APPROVE:
        action.approval_status = 'APPROVED'
        from datetime import datetime
        action.approved_at = datetime.utcnow()

    db.session.add(action)
    db.session.commit()
    logger.info("Action loop: created %s (status=%s) for user %s",
                action_type, action.approval_status, user_id)
    return action


def _build_response(profile: FounderReadinessProfile, result, narrative: dict,
                    gates: dict, first_action=None) -> dict:
    """Assemble the final API response."""
    return {
        'profile_id': profile.id,
        'version': profile.version,
        'overall_readiness_level': result.overall_level,
        'recommended_route': result.recommended_route,
        'founder_type': result.founder_type,
        'detected_scenario': result.detected_scenario,
        'active_blockers': result.active_blockers,
        'allowed_actions': result.allowed_actions,
        'blocked_actions': result.blocked_actions,
        'compensation_rules': result.compensation_rules,
        'burnout_signal': result.burnout_signal,
        'overload_signal': result.overload_signal,
        'phase_gates': gates,
        'dimensions': {
            'financial': {'score': result.financial.score, 'level': result.financial.level},
            'time_capacity': {'score': result.time_capacity.score, 'level': result.time_capacity.level},
            'personal_stability': {'score': result.personal_stability.score, 'level': result.personal_stability.level},
            'motivation_quality': {'score': result.motivation_quality.score, 'level': result.motivation_quality.level},
            'skills_experience': {'score': result.skills_experience.score, 'level': result.skills_experience.level},
            'idea_clarity': {'score': result.idea_clarity.score, 'level': result.idea_clarity.level},
            'founder_idea_fit': {'score': result.founder_idea_fit.score, 'level': result.founder_idea_fit.level},
            'legal_employment': {'score': result.legal_employment.score, 'level': result.legal_employment.level},
            'health_energy': {'score': result.health_energy.score, 'level': result.health_energy.level},
        },
        'ai_narrative': {
            'narrative': narrative.get('founder_readiness_narrative', ''),
            'primary_strength': narrative.get('primary_strength', ''),
            'primary_risk': narrative.get('primary_risk', ''),
            'next_step_explanation': narrative.get('next_step_explanation', ''),
            'what_not_to_do': narrative.get('what_not_to_do', []),
            'confidence': narrative.get('confidence', 'LOW'),
            'is_template': narrative.get('is_template', False),
        },
        'first_action': {
            'id':              first_action.id,
            'action_type':     first_action.action_type,
            'approval_status': first_action.approval_status,
            'rationale':       first_action.rationale,
            'action_data':     first_action.action_data,
        } if first_action else None,
    }
