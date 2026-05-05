"""
Phase 5 Product Concept Testing Service — Sprint 11
====================================================
CEO Section 5: "Do real people respond positively to this specific concept?"

Responsibilities:
- Interpret collected responses to measure adoption signal
- Generate a Product Concept Test Result (the Phase 5 deliverable)
- Recommend: proceed / revise / retest / pivot / stop

CEO dimensions collected:
  Comprehension  — do people understand the offer quickly?
  Desire         — genuine want vs polite approval
  Trust          — do they believe delivery is possible?
  Objections     — price, timing, complexity, credibility, risk, alternatives
  Conversion     — sign-ups, pre-orders, bookings, agreements, donations
  Feedback quality — specific, vague, actionable, biased
  Usability      — can people imagine using it?
  Adoption barriers — what stops action?

Phase 5 blocks progress if:
  - people do not understand the concept
  - interest is polite but not actionable
  - no one willing to pay, sign up, pilot, support, or commit
  - objections are severe and repeated
  - MVP too expensive or complex
  - test group too biased
  - user ignores negative feedback
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

# Canonical interest level values (from pct-s3-2)
INTEREST_LEVELS = (
    'STRONG',     # multiple asked to buy/sign up
    'MODERATE',   # positive but no action
    'POLITE',     # friendly but vague
    'CONFUSED',   # did not understand
    'NEGATIVE',   # rejected or uninterested
)

INTEREST_SCORE = {
    'STRONG':   80,
    'MODERATE': 55,
    'POLITE':   30,
    'CONFUSED': 10,
    'NEGATIVE': 0,
}

# Canonical evidence strength values (from pct-s4-3)
EVIDENCE_LEVELS = (
    'STRONG',      # multiple concrete commitments
    'MODERATE',    # positive signals but no commitments
    'WEAK',        # mostly polite feedback
    'VERY_WEAK',   # confused or negative
)

EVIDENCE_ADJUSTMENT = {
    'STRONG':    +10,
    'MODERATE':  0,
    'WEAK':      -10,
    'VERY_WEAK': -20,
}

# Adoption signal thresholds (final score 0-100)
ADOPTION_THRESHOLDS = {
    'STRONG':   70,
    'MODERATE': 45,
    'WEAK':     20,
}

VALID_DECISIONS = ('PROCEED', 'REVISE', 'RETEST', 'PIVOT', 'STOP')

# Minimum required questions that must have non-empty answers to submit
REQUIRED_FOR_SUBMIT = (
    'pct-s1-1',  # concept description
    'pct-s1-2',  # target audience
    'pct-s2-2',  # contact count
    'pct-s3-2',  # interest level
)

DECISION_RATIONALE = {
    'PROCEED': (
        'Strong adoption signals detected. Your concept is understood, desired, '
        'and has generated concrete commitment. Proceed to Business Development.'
    ),
    'REVISE': (
        'Moderate interest observed but limited concrete action. Your concept shows '
        'promise but needs refinement in messaging, pricing, or delivery before proceeding.'
    ),
    'RETEST': (
        'Signals are weak or unclear. Reposition or simplify the concept, then '
        'repeat testing with a fresh participant group.'
    ),
    'PIVOT': (
        'Adoption barriers are too significant with the current concept. Consider '
        'a pivot: different audience, different solution, or fundamentally different offer.'
    ),
    'STOP': (
        'No adoption signal detected across multiple dimensions. The concept in its '
        'current form is not viable. Stop and reassess from earlier phases.'
    ),
}


class Phase5ConceptService:
    """Interprets Phase 5 responses and generates the Product Concept Test Result."""

    # ── Adoption signal ─────────────────────────────────────────────────────

    def assess_adoption(self, responses: dict) -> dict:
        """
        Compute adoption signal from collected responses.

        Returns:
          adoption_signal:  STRONG | MODERATE | WEAK | NONE
          adoption_score:   0-100
          conversion_rate:  float (conversions / contacts) or None
          blockers:         list of identified blocker strings
          recommendation:   short recommendation string
        """
        interest_raw = (responses.get('pct-s3-2') or '').upper().strip()
        evidence_raw = (responses.get('pct-s4-3') or '').upper().strip()

        # Base score from interest level
        base = INTEREST_SCORE.get(interest_raw, 25)

        # Conversion bonus (0-20)
        contacts   = self._to_int(responses.get('pct-s2-2'))
        conversions = self._to_int(responses.get('pct-s3-5'))
        conv_rate = None
        conv_bonus = 0
        if contacts and contacts > 0:
            conv_rate = round(conversions / contacts, 3)
            conv_bonus = min(20, int(conv_rate * 20))

        # Evidence adjustment
        evidence_adj = EVIDENCE_ADJUSTMENT.get(evidence_raw, 0)

        score = max(0, min(100, base + conv_bonus + evidence_adj))

        # Map score to signal
        if score >= ADOPTION_THRESHOLDS['STRONG']:
            signal = 'STRONG'
        elif score >= ADOPTION_THRESHOLDS['MODERATE']:
            signal = 'MODERATE'
        elif score >= ADOPTION_THRESHOLDS['WEAK']:
            signal = 'WEAK'
        else:
            signal = 'NONE'

        blockers = self._identify_blockers(responses, signal)

        return {
            'adoption_signal':  signal,
            'adoption_score':   score,
            'total_contacts':   contacts or 0,
            'total_conversions': conversions,
            'conversion_rate':  conv_rate,
            'interest_level':   interest_raw or None,
            'evidence_strength': evidence_raw or None,
            'blockers':         blockers,
            'recommendation':   self._recommendation(signal, blockers),
        }

    # ── Generate deliverable ─────────────────────────────────────────────────

    def generate_result(self, venture, responses: dict) -> dict:
        """
        Generate the full Product Concept Test Result deliverable.
        """
        adoption = self.assess_adoption(responses)
        decision = self._decide(adoption['adoption_signal'], adoption['blockers'])

        return {
            'test_design': {
                'concept':           responses.get('pct-s1-1', ''),
                'target_audience':   responses.get('pct-s1-2', ''),
                'value_proposition': responses.get('pct-s1-3', ''),
                'success_criteria':  responses.get('pct-s1-4', ''),
                'methods_used':      responses.get('pct-s2-1', ''),
                'participants':      self._to_int(responses.get('pct-s2-2')),
                'selection_process': responses.get('pct-s2-3', ''),
                'test_scenario':     responses.get('pct-s2-4', ''),
            },
            'response_summary': {
                'total_contacted':   adoption['total_contacts'],
                'conversions':       adoption['total_conversions'],
                'conversion_rate':   adoption['conversion_rate'],
                'interest_level':    adoption['interest_level'],
                'comprehension':     responses.get('pct-s3-1', ''),
                'conversion_signals': responses.get('pct-s3-4', ''),
            },
            'objection_map':       responses.get('pct-s3-3', ''),
            'positive_findings':   responses.get('pct-s4-1', ''),
            'concerns_blockers':   responses.get('pct-s4-2', ''),
            'evidence_strength':   adoption['evidence_strength'],
            'recommended_changes': responses.get('pct-s4-4', ''),
            'adoption_signal':     adoption['adoption_signal'],
            'adoption_score':      adoption['adoption_score'],
            'blockers':            adoption['blockers'],
            'decision':            decision,
            'decision_rationale':  DECISION_RATIONALE.get(decision, ''),
            'ready_for_business_dev': decision == 'PROCEED',
            'generated_at':        datetime.utcnow().isoformat(),
        }

    # ── Validate ──────────────────────────────────────────────────────────────

    def validate_for_submit(self, responses: dict) -> tuple[bool, str]:
        """Check that required responses are present before generating a result."""
        for qid in REQUIRED_FOR_SUBMIT:
            val = responses.get(qid, '')
            if not val or (isinstance(val, str) and not val.strip()):
                return False, f"Required question not answered: {qid}"
        contact_count = self._to_int(responses.get('pct-s2-2'))
        if contact_count is not None and contact_count < 1:
            return False, "Contact count must be at least 1"
        return True, ''

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _to_int(val) -> int | None:
        try:
            return max(0, int(val))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _identify_blockers(responses: dict, signal: str) -> list:
        blockers = []
        interest = (responses.get('pct-s3-2') or '').upper()
        if interest in ('CONFUSED', 'NEGATIVE'):
            blockers.append('Comprehension or interest problem detected')
        conversions = Phase5ConceptService._to_int(responses.get('pct-s3-5')) or 0
        contacts    = Phase5ConceptService._to_int(responses.get('pct-s2-2')) or 0
        if contacts > 0 and conversions == 0 and interest in ('POLITE', 'CONFUSED', 'NEGATIVE'):
            blockers.append('No concrete action taken by any participant')
        objections = (responses.get('pct-s3-3') or '').lower()
        if any(w in objections for w in ('too expensive', 'price', 'afford', 'cost')):
            blockers.append('Pricing objections identified')
        if any(w in objections for w in ('complex', 'complicated', 'confusing', 'hard to')):
            blockers.append('Complexity objections identified')
        if signal == 'NONE':
            blockers.append('No adoption signal from testing')
        return blockers

    @staticmethod
    def _decide(signal: str, blockers: list) -> str:
        if signal == 'STRONG':
            return 'PROCEED'
        if signal == 'MODERATE':
            return 'REVISE'
        if signal == 'WEAK':
            return 'RETEST'
        # NONE — pivot vs stop depends on severity
        if len(blockers) >= 3:
            return 'STOP'
        return 'PIVOT'

    @staticmethod
    def _recommendation(signal: str, blockers: list) -> str:
        if signal == 'STRONG':
            return 'Concept is validated. Proceed to Business Development.'
        if signal == 'MODERATE':
            return 'Promising concept. Address blockers and refine before proceeding.'
        if signal == 'WEAK':
            return 'Concept needs significant revision. Retest with clearer positioning.'
        return 'No viable adoption signal. Consider pivoting or returning to earlier phases.'
