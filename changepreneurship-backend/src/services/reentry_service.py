"""
ReentryService — Sprint 2 (S2-07)
===================================
Handles returning users. Determines what has become stale,
what should be re-evaluated, and generates a "welcome back" snapshot.

CEO Section 3.6:
  "Never force a full restart. Show where they left off,
   what changed, and what needs review."

Inactivity thresholds:
  < 7 days:     resume normally
  7-27 days:    light re-entry check
  28-89 days:   standard re-entry check
  90-179 days:  deep re-entry check
  180+ days:    major revalidation

Staleness rules (CEO Section 3.6):
  financial_runway:     stale after 28 days
  market_research:      stale after 60-90 days
  competitor_analysis:  stale after 90 days
  pitch_deck:           stale after 30-60 days (before external sharing)
  task_roadmap:         stale after 14 days
  founder_readiness:    stale after 60 days
"""
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Inactivity levels
# ---------------------------------------------------------------------------
INACTIVITY_NONE = 0          # < 7 days
INACTIVITY_LIGHT = 1         # 7-27 days
INACTIVITY_STANDARD = 2      # 28-89 days
INACTIVITY_DEEP = 3          # 90-179 days
INACTIVITY_MAJOR = 4         # 180+ days

# Staleness thresholds (days) per output type
STALENESS_RULES = {
    'FOUNDER_READINESS_PROFILE':  60,
    'FINANCIAL_RUNWAY':           28,
    'MARKET_RESEARCH':            60,
    'COMPETITOR_ANALYSIS':        90,
    'PITCH_DECK':                 30,
    'TASK_ROADMAP':               14,
    'CLARIFIED_VENTURE_CONCEPT':  90,
    'VALUE_PROPOSITION':          90,
    'TARGET_USER_HYPOTHESIS':     90,
    'ASSUMPTIONS':                30,
    'BUSINESS_PLAN':              60,
}

# What gets re-evaluated at each inactivity level
REEVAL_BY_LEVEL = {
    INACTIVITY_LIGHT:    ['TASK_ROADMAP', 'FINANCIAL_RUNWAY'],
    INACTIVITY_STANDARD: ['TASK_ROADMAP', 'FINANCIAL_RUNWAY', 'FOUNDER_READINESS_PROFILE'],
    INACTIVITY_DEEP:     [
        'TASK_ROADMAP', 'FINANCIAL_RUNWAY', 'FOUNDER_READINESS_PROFILE',
        'MARKET_RESEARCH', 'ASSUMPTIONS',
    ],
    INACTIVITY_MAJOR:    list(STALENESS_RULES.keys()),
}


class StaleOutput:
    def __init__(self, output_type: str, last_updated: datetime, days_stale: int, action: str):
        self.output_type = output_type
        self.last_updated = last_updated
        self.days_stale = days_stale
        self.action = action  # REFRESH / REVIEW / REBUILD

    def to_dict(self):
        return {
            'output_type': self.output_type,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'days_stale': self.days_stale,
            'action': self.action,
            'label': self._label(),
        }

    def _label(self):
        if self.action == 'REBUILD':
            return 'Outdated'
        if self.action == 'REFRESH':
            return 'Needs Refresh'
        return 'Needs Review'


class ReentrySnapshot:
    def __init__(
        self,
        inactivity_level: int,
        days_away: int,
        where_left_off: dict,
        still_valid: List[str],
        needs_review: List[StaleOutput],
        stale_outputs: List[StaleOutput],
        updated_blockers: List[dict],
        recommended_next_action: dict,
        what_not_to_do_yet: List[str],
        welcome_message: str,
    ):
        self.inactivity_level = inactivity_level
        self.days_away = days_away
        self.where_left_off = where_left_off
        self.still_valid = still_valid
        self.needs_review = needs_review
        self.stale_outputs = stale_outputs
        self.updated_blockers = updated_blockers
        self.recommended_next_action = recommended_next_action
        self.what_not_to_do_yet = what_not_to_do_yet
        self.welcome_message = welcome_message

    def to_dict(self):
        return {
            'inactivity_level': self.inactivity_level,
            'days_away': self.days_away,
            'where_left_off': self.where_left_off,
            'still_valid': self.still_valid,
            'needs_review': [o.to_dict() for o in self.needs_review],
            'stale_outputs': [o.to_dict() for o in self.stale_outputs],
            'updated_blockers': self.updated_blockers,
            'recommended_next_action': self.recommended_next_action,
            'what_not_to_do_yet': self.what_not_to_do_yet,
            'welcome_message': self.welcome_message,
        }


class ReentryService:
    """
    Stateless service. Accepts user state data, returns a ReentrySnapshot.

    Usage:
        service = ReentryService()
        snapshot = service.generate_reentry_snapshot(
            last_seen=datetime(...),
            current_outputs={...},  # dict of output_type → last_updated datetime
            current_phase=1,
            last_action=dict(...),
            active_blockers=[...],
        )
    """

    def check_inactivity_level(self, last_seen: datetime) -> tuple[int, int]:
        """Returns (inactivity_level, days_away)."""
        if last_seen is None:
            return INACTIVITY_MAJOR, 999
        days = (datetime.utcnow() - last_seen).days
        if days < 7:
            return INACTIVITY_NONE, days
        if days < 28:
            return INACTIVITY_LIGHT, days
        if days < 90:
            return INACTIVITY_STANDARD, days
        if days < 180:
            return INACTIVITY_DEEP, days
        return INACTIVITY_MAJOR, days

    def evaluate_stale_outputs(
        self,
        current_outputs: dict,  # {output_type: last_updated datetime}
        inactivity_level: int,
        days_away: int,
    ) -> tuple[List[StaleOutput], List[str]]:
        """
        Returns (stale_outputs, still_valid_types).
        """
        stale = []
        still_valid = []
        now = datetime.utcnow()

        for output_type, threshold_days in STALENESS_RULES.items():
            last_updated = current_outputs.get(output_type)
            if last_updated is None:
                continue  # Output doesn't exist yet — not stale

            age_days = (now - last_updated).days

            if age_days >= threshold_days:
                action = 'REBUILD' if age_days >= threshold_days * 2 else 'REFRESH'
                stale.append(StaleOutput(
                    output_type=output_type,
                    last_updated=last_updated,
                    days_stale=age_days - threshold_days,
                    action=action,
                ))
            else:
                still_valid.append(output_type)

        return stale, still_valid

    def generate_reentry_snapshot(
        self,
        last_seen: Optional[datetime],
        current_outputs: dict,  # {output_type: last_updated datetime}
        current_phase: int = 1,
        last_action: Optional[dict] = None,
        active_blockers: Optional[List[dict]] = None,
    ) -> ReentrySnapshot:
        """
        Generate the full re-entry snapshot for a returning user.
        """
        inactivity_level, days_away = self.check_inactivity_level(last_seen)
        stale_outputs, still_valid = self.evaluate_stale_outputs(
            current_outputs, inactivity_level, days_away
        )

        needs_review = [o for o in stale_outputs if o.action == 'REVIEW']
        truly_stale = [o for o in stale_outputs if o.action in ('REFRESH', 'REBUILD')]

        # Build recommended next action
        if inactivity_level == INACTIVITY_NONE:
            next_action = {
                'type': 'CONTINUE',
                'description': 'Continue where you left off.',
                'cta': 'Continue',
            }
        elif inactivity_level == INACTIVITY_LIGHT:
            next_action = {
                'type': 'QUICK_CHECK',
                'description': 'Quick check on your financial situation and last task.',
                'cta': 'Run quick check',
            }
        elif inactivity_level == INACTIVITY_STANDARD:
            next_action = {
                'type': 'REENTRY_ASSESSMENT',
                'description': 'Answer 3 quick questions to re-calibrate your situation.',
                'cta': 'Update my situation',
            }
        elif inactivity_level == INACTIVITY_DEEP:
            next_action = {
                'type': 'DEEP_REENTRY',
                'description': (
                    'Quite a bit may have changed. '
                    'Let us re-assess your current situation in about 10 minutes.'
                ),
                'cta': 'Re-assess my situation',
            }
        else:
            next_action = {
                'type': 'MAJOR_REVALIDATION',
                'description': (
                    'Welcome back after a long break. '
                    'Your profile needs a full update — this will take about 15 minutes.'
                ),
                'cta': 'Start re-assessment',
            }

        # What not to do yet
        what_not_to_do = []
        if truly_stale:
            stale_types = [o.output_type.replace('_', ' ').title() for o in truly_stale[:3]]
            what_not_to_do.append(
                f"Do not share {', '.join(stale_types)} with anyone external — they may be outdated."
            )
        if active_blockers:
            what_not_to_do.append(
                'Do not commit to paid actions until active blockers are reviewed.'
            )

        # Welcome message (CEO tone: welcoming, not shaming)
        welcome_message = self._build_welcome_message(days_away, inactivity_level, current_phase)

        where_left_off = {
            'phase': current_phase,
            'last_action': last_action or {},
            'phase_label': f'Phase {current_phase}',
        }

        return ReentrySnapshot(
            inactivity_level=inactivity_level,
            days_away=days_away,
            where_left_off=where_left_off,
            still_valid=still_valid,
            needs_review=needs_review,
            stale_outputs=truly_stale,
            updated_blockers=active_blockers or [],
            recommended_next_action=next_action,
            what_not_to_do_yet=what_not_to_do,
            welcome_message=welcome_message,
        )

    def _build_welcome_message(self, days_away: int, level: int, phase: int) -> str:
        """CEO tone: welcoming, not shaming. Never mentions deadlines."""
        if level == INACTIVITY_NONE:
            return f"Welcome back. You are in Phase {phase} — continue from where you stopped."
        if level == INACTIVITY_LIGHT:
            return (
                f"Good to see you back after {days_away} days. "
                f"Your progress in Phase {phase} is still here. "
                f"One quick check and you are ready to continue."
            )
        if level == INACTIVITY_STANDARD:
            return (
                f"Welcome back after {days_away} days. "
                f"Some of your financial and readiness data may need a quick update. "
                f"This will only take a few minutes."
            )
        if level == INACTIVITY_DEEP:
            return (
                f"Welcome back — it has been about {days_away // 30} months. "
                f"A lot can change in that time, and your situation likely has too. "
                f"Let us take 10 minutes to re-calibrate before you continue."
            )
        return (
            f"Welcome back. It has been a while — {days_away // 30} months. "
            f"Your work is all here, exactly as you left it. "
            f"Let us start by understanding where you are now, and take it from there."
        )
