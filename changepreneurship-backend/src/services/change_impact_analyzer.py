"""
ChangeImpactAnalyzer — Sprint 2 (S2-05)
========================================
When a user changes an answer, determine the severity and downstream impact
of that change across all outputs (documents, assessments, routes, tasks).

CEO Section 3.5:
  "Users can change direction at any time, but the platform must preserve
  traceability and explain the consequences."

Severity Levels:
  1 = Minor wording       → auto-update
  2 = Detail update       → light recalculation
  3 = Assumption change   → flag affected outputs
  4 = Strategic change    → full impact analysis + user review required
  5 = Blocking change     → pause affected route
  6 = Venture restart     → archive + new workspace

Silent overwrites are strictly forbidden.
"""
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Output types that can be affected
# ---------------------------------------------------------------------------
OUTPUT_FOUNDER_PROFILE = 'FOUNDER_READINESS_PROFILE'
OUTPUT_PHASE_GATE = 'PHASE_GATE'
OUTPUT_ROUTING_DECISION = 'ROUTING_DECISION'
OUTPUT_VENTURE_CONCEPT = 'CLARIFIED_VENTURE_CONCEPT'
OUTPUT_PROBLEM_STATEMENT = 'PROBLEM_STATEMENT'
OUTPUT_TARGET_USER = 'TARGET_USER_HYPOTHESIS'
OUTPUT_VALUE_PROP = 'VALUE_PROPOSITION'
OUTPUT_ASSUMPTIONS = 'ASSUMPTIONS'
OUTPUT_TASK_ROADMAP = 'TASK_ROADMAP'
OUTPUT_PITCH_DECK = 'PITCH_DECK'
OUTPUT_MARKET_RESEARCH = 'MARKET_RESEARCH'
OUTPUT_BUSINESS_PLAN = 'BUSINESS_PLAN'
OUTPUT_COMPETITOR_ANALYSIS = 'COMPETITOR_ANALYSIS'


@dataclass
class AffectedOutput:
    output_type: str
    status: str           # INVALIDATED / NEEDS_REVIEW / AUTO_UPDATED / UNAFFECTED
    action_required: str  # RE_GENERATE / USER_REVIEW / AUTO / NONE
    reason: str


@dataclass
class ChangeImpactResult:
    severity_level: int
    changed_field: str
    old_value: object
    new_value: object
    affected_outputs: List[AffectedOutput]
    upstream_impact: List[str]
    downstream_impact: List[str]
    sidestream_impact: List[str]
    recommendation: str
    requires_user_approval: bool
    is_venture_restart: bool


# ---------------------------------------------------------------------------
# Field → severity mapping
# ---------------------------------------------------------------------------
# Changing these fields at Level 4 requires user approval
_STRATEGIC_FIELDS = {
    'target_user_description',   # Changing customer = all docs affected
    'venture_type',
    'problem_defined',
    'value_prop_clear',
    'motivation_type',
    'funding_model_preference',
    'venture_goal_type',
}

_BLOCKING_FIELDS = {
    'financial_runway_months',   # Can trigger/resolve blockers
    'illegal_venture',
    'immigration_restriction',
    'employer_ip_risk',
    'has_non_compete',
    'income_stable',
}

_DETAIL_FIELDS = {
    'weekly_available_hours',
    'stress_level',
    'energy_level',
    'risk_tolerance',
    'domain_skill_level',
    'relevant_experience_years',
    'mission_clarity',
    'idea_description',
}


class ChangeImpactAnalyzer:
    """
    Stateless analyzer. Call analyze(field, old_value, new_value, current_profile)
    to get a ChangeImpactResult.
    """

    def analyze(
        self,
        changed_field: str,
        old_value,
        new_value,
        current_outputs: List[str] = None,
        responses: dict = None,
    ) -> ChangeImpactResult:
        """
        Analyze the impact of changing a single field.

        Args:
            changed_field: Name of the response field that changed.
            old_value: Previous value.
            new_value: New value.
            current_outputs: List of output types that currently exist for user.
            responses: Full current response dict (for context).
        """
        current_outputs = current_outputs or []
        responses = responses or {}

        severity = self._compute_severity(changed_field, old_value, new_value, responses)
        affected = self._compute_affected_outputs(changed_field, severity, current_outputs)
        upstream, downstream, sidestream = self._compute_impact_streams(changed_field, severity)

        recommendation = self._build_recommendation(changed_field, severity, affected)
        requires_approval = severity >= 4
        is_restart = severity >= 6

        return ChangeImpactResult(
            severity_level=severity,
            changed_field=changed_field,
            old_value=old_value,
            new_value=new_value,
            affected_outputs=affected,
            upstream_impact=upstream,
            downstream_impact=downstream,
            sidestream_impact=sidestream,
            recommendation=recommendation,
            requires_user_approval=requires_approval,
            is_venture_restart=is_restart,
        )

    def _compute_severity(self, field: str, old_val, new_val, responses: dict) -> int:
        """Determine change severity level 1-6."""
        if field in _STRATEGIC_FIELDS:
            # Changing target customer is almost always Level 4+
            if field == 'target_user_description':
                return 4
            if field == 'venture_type':
                return 4
            if field == 'problem_defined' and not new_val:
                return 5  # Removing problem definition is blocking
            return 4

        if field in _BLOCKING_FIELDS:
            if field == 'illegal_venture' or field == 'immigration_restriction':
                return 5  # Immediate blocker
            # Financial runway: big change (from >6mo to <1mo) = level 4
            if field == 'financial_runway_months':
                try:
                    old_f = float(old_val or 0)
                    new_f = float(new_val or 0)
                    if new_f < 1 and old_f >= 3:
                        return 5
                    if abs(new_f - old_f) > 6:
                        return 4
                    if abs(new_f - old_f) > 2:
                        return 3
                    return 2
                except (TypeError, ValueError):
                    return 3
            return 3

        if field in _DETAIL_FIELDS:
            # Significant numeric changes
            try:
                old_f = float(old_val or 0)
                new_f = float(new_val or 0)
                if abs(new_f - old_f) / max(old_f, 1) > 0.5:
                    return 3
                return 2
            except (TypeError, ValueError):
                return 2

        # Default: minor wording
        return 1

    def _compute_affected_outputs(
        self, field: str, severity: int, current_outputs: List[str]
    ) -> List[AffectedOutput]:
        affected = []

        # Helper
        def add(output_type, status, action, reason):
            if output_type in current_outputs:
                affected.append(AffectedOutput(
                    output_type=output_type,
                    status=status,
                    action_required=action,
                    reason=reason,
                ))

        if severity >= 5:
            # Blocking changes invalidate almost everything
            for ot in current_outputs:
                add(ot, 'INVALIDATED', 'USER_REVIEW',
                    f'Change to {field} at severity {severity} requires review of all outputs.')

        elif severity == 4:
            # Strategic change — all venture docs need review
            add(OUTPUT_FOUNDER_PROFILE, 'NEEDS_REVIEW', 'RE_GENERATE',
                f'{field} is a strategic field — re-evaluate readiness profile.')
            add(OUTPUT_ROUTING_DECISION, 'INVALIDATED', 'RE_GENERATE',
                'Routing must be recalculated.')
            add(OUTPUT_VENTURE_CONCEPT, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Clarified venture concept may no longer be accurate.')
            add(OUTPUT_PROBLEM_STATEMENT, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Problem statement should be reviewed.')
            add(OUTPUT_TARGET_USER, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Target user hypothesis may have changed.')
            add(OUTPUT_VALUE_PROP, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Value proposition depends on target user and venture type.')
            add(OUTPUT_ASSUMPTIONS, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Some assumptions may no longer apply.')
            add(OUTPUT_BUSINESS_PLAN, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Business plan is built on the changed parameters.')
            add(OUTPUT_PITCH_DECK, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Pitch deck targets may need updating.')

        elif severity == 3:
            # Assumption change — flag related outputs
            add(OUTPUT_FOUNDER_PROFILE, 'NEEDS_REVIEW', 'RE_GENERATE',
                f'{field} affects readiness scoring.')
            add(OUTPUT_ROUTING_DECISION, 'NEEDS_REVIEW', 'RE_GENERATE',
                'Routing should be recalculated.')
            add(OUTPUT_ASSUMPTIONS, 'NEEDS_REVIEW', 'USER_REVIEW',
                'Verify affected assumptions.')

        elif severity == 2:
            # Light recalculation
            add(OUTPUT_FOUNDER_PROFILE, 'AUTO_UPDATED', 'AUTO',
                f'{field} change triggers profile recalculation.')
            add(OUTPUT_ROUTING_DECISION, 'AUTO_UPDATED', 'AUTO',
                'Routing updated automatically.')

        elif severity == 1:
            # Auto-update, no user action
            for ot in current_outputs:
                if ot == OUTPUT_FOUNDER_PROFILE:
                    add(ot, 'AUTO_UPDATED', 'AUTO', 'Minor update applied.')

        return [a for a in affected]  # filter already done in add()

    def _compute_impact_streams(self, field: str, severity: int):
        """
        upstream = what feeds into this field
        downstream = what this field feeds into
        sidestream = adjacent/related outputs not in direct chain
        """
        upstream, downstream, sidestream = [], [], []

        DOWNSTREAM_MAP = {
            'target_user_description': [
                OUTPUT_VENTURE_CONCEPT, OUTPUT_VALUE_PROP, OUTPUT_MARKET_RESEARCH,
                OUTPUT_BUSINESS_PLAN, OUTPUT_PITCH_DECK,
            ],
            'venture_type': [
                OUTPUT_ROUTING_DECISION, OUTPUT_VENTURE_CONCEPT, OUTPUT_BUSINESS_PLAN,
            ],
            'financial_runway_months': [
                OUTPUT_FOUNDER_PROFILE, OUTPUT_ROUTING_DECISION, OUTPUT_PHASE_GATE,
            ],
            'problem_defined': [
                OUTPUT_VENTURE_CONCEPT, OUTPUT_PROBLEM_STATEMENT, OUTPUT_ASSUMPTIONS,
                OUTPUT_MARKET_RESEARCH,
            ],
        }

        downstream = DOWNSTREAM_MAP.get(field, [OUTPUT_FOUNDER_PROFILE, OUTPUT_ROUTING_DECISION])

        if severity >= 4:
            sidestream = [OUTPUT_TASK_ROADMAP, OUTPUT_COMPETITOR_ANALYSIS]

        return upstream, downstream, sidestream

    def _build_recommendation(
        self, field: str, severity: int, affected: List[AffectedOutput]
    ) -> str:
        if severity >= 6:
            return (
                'This change is significant enough to warrant starting a new venture workspace. '
                'Your current work will be archived and accessible.'
            )
        if severity == 5:
            return (
                f'Changing {field} has triggered an active blocker. '
                f'Review the {len(affected)} affected output(s) before continuing.'
            )
        if severity == 4:
            needs_review = [a for a in affected if a.action_required == 'USER_REVIEW']
            return (
                f'This is a strategic change. '
                f'{len(needs_review)} document(s) now have "Needs Review" status. '
                f'Review them before presenting to any external party.'
            )
        if severity == 3:
            return (
                f'{field} change affects assumptions and scoring. '
                f'Recalculation will run automatically, but verify the results.'
            )
        if severity == 2:
            return 'Minor change — outputs have been automatically updated.'
        return 'Wording update applied. No outputs affected.'
