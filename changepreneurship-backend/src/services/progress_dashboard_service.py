"""
ProgressDashboardService — Sprint 6 (S6-01)
=============================================
CEO MVP Feature 3 (Section 13.1):
"Progress, outcome, and benchmark tracking"

Dashboard contract:
  - Current stage / current goal
  - Recommended next step (always concrete)
  - Actions taken / waiting items
  - Results / outcomes
  - Next follow-up date (if applicable)
  - Main blocker + unlock condition

Phase order (CEO Section 3.3):
  1. self_discovery       — Self Discovery Assessment
  2. idea_discovery       — Idea Discovery Assessment
  3. market_research      — Market Research
  4. business_pillars     — Business Pillars Planning
  5. product_concept_testing  — Product Concept Testing
  6. business_development — Business Development
  7. business_prototype_testing  — Business Prototype Testing

Phase status:
  LOCKED       — prerequisite not met
  IN_PROGRESS  — started, not complete
  COMPLETED    — progress_percentage == 100 and is_completed
  NOT_STARTED  — unlocked but never started
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.models.assessment import db, Assessment, AssessmentResponse
from src.models.user_action import UserAction, BlockerEvent
from src.models.venture_record import VentureRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase definitions (ordered)
# ---------------------------------------------------------------------------
PHASES = [
    {'id': 'self_discovery',            'name': 'Self Discovery Assessment',    'order': 1},
    {'id': 'idea_discovery',            'name': 'Idea Discovery Assessment',    'order': 2},
    {'id': 'market_research',           'name': 'Market Research',              'order': 3},
    {'id': 'business_pillars',          'name': 'Business Pillars Planning',    'order': 4},
    {'id': 'product_concept_testing',   'name': 'Product Concept Testing',      'order': 5},
    {'id': 'business_development',      'name': 'Business Development',         'order': 6},
    {'id': 'business_prototype_testing','name': 'Business Prototype Testing',   'order': 7},
]

PHASE_IDS = [p['id'] for p in PHASES]

# Mapping from DB phase_id → canonical order index
PHASE_ORDER = {p['id']: p['order'] for p in PHASES}
PHASE_NAME  = {p['id']: p['name']  for p in PHASES}

# Phase goal descriptions (what the user achieves in each phase)
PHASE_GOALS = {
    'self_discovery':       'Understand your founder archetype, motivations, and readiness',
    'idea_discovery':       'Clarify your venture idea into a testable concept',
    'market_research':      'Validate that the market cares about your idea',
    'business_pillars':     'Design your business model, funding logic, and legal structure',
    'product_concept_testing':    'Test your product concept with real potential users',
    'business_development':        'Build the core foundations of your business',
    'business_prototype_testing':  'Prototype, test, and iterate toward your MVP',
}

# What to do next in each phase (concrete action)
PHASE_NEXT_STEP = {
    'self_discovery':       'Complete the Self Discovery Assessment to unlock your founder profile',
    'idea_discovery':       'Submit your idea description to get a Clarified Venture Concept',
    'market_research':      'Conduct your first 5 customer discovery interviews',
    'business_pillars':     'Review your AI-generated Business Pillars Blueprint and approve each pillar',
    'product_concept_testing':    'Define your product concept and test it with at least 3 real users',
    'business_development':        'Complete your business development plan and identify 3 key partners',
    'business_prototype_testing':  'Build a prototype and collect structured feedback from 10 users',
}


class ProgressDashboardService:
    """
    Aggregates all user progress data into a structured dashboard.
    Reads from: Assessment, UserAction, BlockerEvent, VentureRecord,
                FounderReadinessProfile (if available).
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Full dashboard aggregation.
        Returns:
          {
            current_phase: {id, name, goal, status, progress_percentage},
            phases: [{id, name, order, status, progress_percentage, response_count}],
            recommended_next_action: {phase_id, action, reason},
            pending_items: [{action_id, type, status, proposed_at}],
            recent_outcomes: [{action_id, type, outcome, recorded_at}],
            active_blockers: [{type, reason, unlock_condition, level}],
            venture_summary: {name, type, status} | null,
            stats: {completed_phases, total_phases, overall_progress_pct},
          }
        """
        phase_statuses = self._get_phase_statuses(user_id)
        current_phase  = self._get_current_phase(phase_statuses)
        blockers       = self._get_active_blockers(user_id)
        pending        = self.get_pending_items(user_id)
        outcomes       = self.get_recent_outcomes(user_id)
        venture        = self._get_venture_summary(user_id)
        next_action    = self.get_next_recommended_action(user_id, phase_statuses, blockers)
        stats          = self._compute_stats(phase_statuses)

        return {
            'current_phase':           current_phase,
            'phases':                  phase_statuses,
            'recommended_next_action': next_action,
            'pending_items':           pending,
            'recent_outcomes':         outcomes,
            'active_blockers':         blockers,
            'venture_summary':         venture,
            'stats':                   stats,
            'generated_at':            datetime.utcnow().isoformat(),
        }

    def get_current_stage_summary(self, user_id: int) -> Dict[str, Any]:
        """Current stage with goal and progress."""
        phase_statuses = self._get_phase_statuses(user_id)
        return self._get_current_phase(phase_statuses)

    def get_next_recommended_action(
        self,
        user_id: int,
        phase_statuses: Optional[List] = None,
        blockers: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Returns the single most important next step.
        Priority: blockers > current in-progress phase > next locked phase.
        """
        if phase_statuses is None:
            phase_statuses = self._get_phase_statuses(user_id)
        if blockers is None:
            blockers = self._get_active_blockers(user_id)

        # If there is a hard blocker, that is the highest priority
        hard_blockers = [b for b in blockers if b.get('level', 0) >= 4]
        if hard_blockers:
            top = hard_blockers[0]
            return {
                'phase_id':   top.get('phase_id', 'unknown'),
                'action':     top.get('unlock_condition', 'Resolve the active blocker'),
                'reason':     f"Hard blocker: {top.get('type', 'UNKNOWN')} — {top.get('reason', '')}",
                'priority':   'CRITICAL',
                'blocker_id': top.get('id'),
            }

        # In-progress phase
        for ps in phase_statuses:
            if ps['status'] == 'IN_PROGRESS':
                return {
                    'phase_id': ps['id'],
                    'action':   PHASE_NEXT_STEP.get(ps['id'], 'Continue this phase'),
                    'reason':   f"Continue your current phase: {ps['name']}",
                    'priority': 'HIGH',
                }

        # Next not-started (unlocked) phase
        for ps in phase_statuses:
            if ps['status'] == 'NOT_STARTED':
                return {
                    'phase_id': ps['id'],
                    'action':   PHASE_NEXT_STEP.get(ps['id'], 'Start this phase'),
                    'reason':   f"You're ready to begin: {ps['name']}",
                    'priority': 'NORMAL',
                }

        # All complete or all locked
        completed_count = sum(1 for ps in phase_statuses if ps['status'] == 'COMPLETED')
        if completed_count == len(PHASES):
            return {
                'phase_id': None,
                'action':   'All phases completed — review your AI Insights Report',
                'reason':   'You have completed the full Changepreneurship journey',
                'priority': 'INFO',
            }

        # Soft blockers
        soft_blockers = [b for b in blockers if b.get('level', 0) == 3]
        if soft_blockers:
            top = soft_blockers[0]
            return {
                'phase_id':   top.get('phase_id', 'unknown'),
                'action':     top.get('unlock_condition', 'Address the soft blocker'),
                'reason':     f"Soft blocker: {top.get('type', 'UNKNOWN')} — {top.get('reason', '')}",
                'priority':   'MEDIUM',
                'blocker_id': top.get('id'),
            }

        return {
            'phase_id': None,
            'action':   'Review your progress and identify the next phase to begin',
            'reason':   'No active phases — check for locked phases',
            'priority': 'LOW',
        }

    def get_pending_items(self, user_id: int) -> List[Dict[str, Any]]:
        """UserActions awaiting user approval or external response."""
        pending_statuses = ('PROPOSED', 'REVIEWED')
        actions = (
            UserAction.query
            .filter_by(user_id=user_id)
            .filter(UserAction.approval_status.in_(pending_statuses))
            .order_by(UserAction.proposed_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                'action_id':   a.id,
                'type':        a.action_type,
                'status':      a.approval_status,
                'rationale':   a.rationale,
                'proposed_at': a.proposed_at.isoformat() if a.proposed_at else None,
                'expires_at':  a.expires_at.isoformat() if getattr(a, 'expires_at', None) else None,
            }
            for a in actions
        ]

    def get_recent_outcomes(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Recently completed/failed/recorded actions."""
        terminal_statuses = ('OUTCOME_RECORDED', 'REJECTED', 'FAILED', 'CANCELLED', 'EXECUTED')
        actions = (
            UserAction.query
            .filter_by(user_id=user_id)
            .filter(UserAction.approval_status.in_(terminal_statuses))
            .order_by(UserAction.proposed_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'action_id':   a.id,
                'type':        a.action_type,
                'outcome':     a.approval_status,
                'outcome_data': getattr(a, 'outcome_data', None),
                'proposed_at': a.proposed_at.isoformat() if a.proposed_at else None,
                'executed_at': a.executed_at.isoformat() if a.executed_at else None,
            }
            for a in actions
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_phase_statuses(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns ordered list of phase status dicts.
        A phase is LOCKED if the previous phase is not completed.
        Phase 1 is always unlocked.
        """
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        assessment_map = {a.phase_id: a for a in assessments}

        statuses = []
        prev_completed = True  # Phase 1 always unlocked

        for phase in PHASES:
            pid = phase['id']
            assessment = assessment_map.get(pid)

            if not prev_completed:
                status = 'LOCKED'
                progress = 0.0
                response_count = 0
                completed_at = None
            elif assessment is None:
                status = 'NOT_STARTED'
                progress = 0.0
                response_count = 0
                completed_at = None
            elif assessment.is_completed or assessment.progress_percentage >= 100:
                status = 'COMPLETED'
                progress = 100.0
                response_count = AssessmentResponse.query.filter_by(
                    assessment_id=assessment.id
                ).count()
                completed_at = assessment.completed_at.isoformat() if assessment.completed_at else None
            else:
                status = 'IN_PROGRESS'
                progress = assessment.progress_percentage or 0.0
                response_count = AssessmentResponse.query.filter_by(
                    assessment_id=assessment.id
                ).count()
                completed_at = None

            statuses.append({
                'id':                 pid,
                'name':               phase['name'],
                'order':              phase['order'],
                'goal':               PHASE_GOALS.get(pid, ''),
                'status':             status,
                'progress_percentage': progress,
                'response_count':     response_count,
                'completed_at':       completed_at,
                'assessment_id':      assessment.id if assessment else None,
            })

            # Next phase is locked unless this one is completed
            prev_completed = (status == 'COMPLETED')

        return statuses

    def _get_current_phase(self, phase_statuses: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Returns the current active phase.
        Priority: IN_PROGRESS > first NOT_STARTED > last COMPLETED.
        """
        for ps in phase_statuses:
            if ps['status'] == 'IN_PROGRESS':
                return ps
        for ps in phase_statuses:
            if ps['status'] == 'NOT_STARTED':
                return ps
        # All completed or all locked
        completed = [ps for ps in phase_statuses if ps['status'] == 'COMPLETED']
        return completed[-1] if completed else phase_statuses[0]

    def _get_active_blockers(self, user_id: int) -> List[Dict[str, Any]]:
        """Unresolved BlockerEvents for this user (resolved_at is None)."""
        blockers = (
            BlockerEvent.query
            .filter_by(user_id=user_id)
            .filter(BlockerEvent.resolved_at.is_(None))
            .order_by(BlockerEvent.triggered_at.desc())
            .limit(10)
            .all()
        )
        result = []
        for b in blockers:
            d = {
                'id':               b.id,
                'type':             b.blocker_type,
                'level':            b.severity_level,
                'reason':           b.dimension or b.blocker_type,
                'unlock_condition': b.unlock_condition,
                'triggered_at':     b.triggered_at.isoformat() if b.triggered_at else None,
                'phase_id':         getattr(b, 'phase_id', None),
            }
            result.append(d)
        return result

    def _get_venture_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Active VentureRecord summary, or None."""
        venture = (
            VentureRecord.query
            .filter_by(user_id=user_id, is_active=True)
            .order_by(VentureRecord.version.desc())
            .first()
        )
        if not venture:
            return None
        return {
            'id':            venture.id,
            'name':          getattr(venture, 'idea_clarified', None) or getattr(venture, 'idea_raw', None) or 'Unnamed Venture',
            'venture_type':  getattr(venture, 'venture_type', None),
            'status':        venture.status,
            'version':       venture.version,
        }

    def _compute_stats(self, phase_statuses: List[Dict]) -> Dict[str, Any]:
        """Summary statistics for the progress bar."""
        total = len(phase_statuses)
        completed = sum(1 for ps in phase_statuses if ps['status'] == 'COMPLETED')
        in_progress = sum(1 for ps in phase_statuses if ps['status'] == 'IN_PROGRESS')
        locked = sum(1 for ps in phase_statuses if ps['status'] == 'LOCKED')

        # Overall % = average of per-phase progress
        overall_pct = (
            sum(ps['progress_percentage'] for ps in phase_statuses) / total
            if total else 0.0
        )

        return {
            'total_phases':        total,
            'completed_phases':    completed,
            'in_progress_phases':  in_progress,
            'locked_phases':       locked,
            'overall_progress_pct': round(overall_pct, 1),
        }
