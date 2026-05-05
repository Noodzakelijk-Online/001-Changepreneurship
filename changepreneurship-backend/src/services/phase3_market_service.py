"""
Phase 3 Market Research Service — Sprint 9
==========================================
CEO Section 3.3 Phase 3: "Does the world care?"

Responsibilities:
- Evaluate evidence quality (strength hierarchy from VentureRecord)
- Generate Market Validity Report (MVR)
- Generate interview/outreach scripts
- Build competitor map
- Test assumptions from Phase 2 CVC
- Recommend proceed / revise / pivot / stop

Evidence strength (from venture_record.py, CEO Section 2.5):
  BELIEF < OPINION < DESK_RESEARCH < AI_RESEARCH < INDIRECT < DIRECT < BEHAVIORAL
  (0)      (1)       (2)             (3)            (4)        (5)      (6)
"""
import logging
from datetime import datetime
from typing import Optional

from src.models.venture_record import (
    VentureRecord, EvidenceItem,
    VENTURE_STATUS_VALIDATED,
    EVIDENCE_STRENGTH_ORDER, EVIDENCE_TYPE_CHOICES,
)

logger = logging.getLogger(__name__)

# ── Evidence threshold for each recommendation ─────────────────────────────
# CEO: minimum DIRECT or BEHAVIORAL evidence to proceed safely
MIN_PROCEED_SCORE      = 30   # out of 100
MIN_CONFIDENT_SCORE    = 55
STRONG_EVIDENCE_SCORE  = 75

# Minimum number of distinct evidence items to generate a full MVR
MIN_EVIDENCE_FOR_REPORT = 2

# ── Competitors ─────────────────────────────────────────────────────────────
MAX_COMPETITORS = 10


class Phase3MarketService:
    """Core Phase 3 logic — stateless, all data via arguments."""

    # ───────────────────────────────────────────────────────────────────────
    # 1. Evidence scoring
    # ───────────────────────────────────────────────────────────────────────

    def score_evidence(self, evidence_items: list) -> dict:
        """
        Returns {score: 0–100, breakdown, recommendation, evidence_count}.
        Score is weighted: higher-strength items count more.
        CEO: BEHAVIORAL > DIRECT > INDIRECT (must be the dominant type).
        """
        if not evidence_items:
            return {
                'score': 0,
                'recommendation': 'NO_EVIDENCE',
                'breakdown': {},
                'evidence_count': 0,
                'has_behavioral': False,
                'has_direct': False,
            }

        breakdown: dict[str, int] = {s: 0 for s in EVIDENCE_STRENGTH_ORDER}
        total_weight = 0
        max_possible = len(evidence_items) * 6  # max strength index = 6 (BEHAVIORAL)

        for item in evidence_items:
            strength = item.get('strength') if isinstance(item, dict) else item.strength
            idx = EVIDENCE_STRENGTH_ORDER.index(strength) if strength in EVIDENCE_STRENGTH_ORDER else 0
            breakdown[strength] = breakdown.get(strength, 0) + 1
            total_weight += idx

        raw_score = int((total_weight / max_possible) * 100) if max_possible else 0

        # Boost for BEHAVIORAL evidence (strongest CEO signal)
        behavioral_count = breakdown.get('BEHAVIORAL', 0)
        direct_count = breakdown.get('DIRECT', 0)
        if behavioral_count >= 2:
            raw_score = min(100, raw_score + 15)
        elif direct_count >= 3:
            raw_score = min(100, raw_score + 8)

        # Penalty for evidence that's all BELIEF / OPINION
        belief_count = breakdown.get('BELIEF', 0) + breakdown.get('OPINION', 0)
        if belief_count == len(evidence_items):
            raw_score = min(raw_score, 15)

        # Recommendation
        if raw_score >= STRONG_EVIDENCE_SCORE:
            recommendation = 'PROCEED'
        elif raw_score >= MIN_CONFIDENT_SCORE:
            recommendation = 'PROCEED_WITH_CAUTION'
        elif raw_score >= MIN_PROCEED_SCORE:
            recommendation = 'MORE_VALIDATION_NEEDED'
        else:
            recommendation = 'INSUFFICIENT_EVIDENCE'

        return {
            'score': raw_score,
            'recommendation': recommendation,
            'breakdown': breakdown,
            'evidence_count': len(evidence_items),
            'has_behavioral': behavioral_count > 0,
            'has_direct': direct_count > 0,
        }

    # ───────────────────────────────────────────────────────────────────────
    # 2. Assumption testing
    # ───────────────────────────────────────────────────────────────────────

    def evaluate_assumptions(self, assumptions: list, evidence_items: list) -> dict:
        """
        For each assumption from Phase 2 CVC, determine if it's:
          CONFIRMED / REJECTED / PARTIALLY / UNTESTED
        based on the submitted evidence items.
        """
        results = []
        evidence_descriptions = [
            (e.get('description', '') if isinstance(e, dict) else e.description).lower()
            for e in evidence_items
        ]

        for assumption in assumptions:
            # Handle both plain strings and dicts with 'text' or 'assumption' keys
            if isinstance(assumption, str):
                text = assumption.lower()
                tested = False
                test_result = None
            else:
                text = (assumption.get('text') or assumption.get('assumption') or '').lower()
                tested = assumption.get('tested', False)
                test_result = assumption.get('test_result')

            if not text:
                continue

            # Simple keyword match — a proper NLP approach would be ideal
            # but for MVP this is sufficient
            matched_evidence = [d for d in evidence_descriptions if any(
                word in d for word in text.split() if len(word) > 4
            )]

            if tested:
                outcome = test_result or 'PARTIALLY'
            elif matched_evidence:
                outcome = 'PARTIALLY'
            else:
                outcome = 'UNTESTED'

            results.append({
                'assumption': text,
                'status': outcome,
                'evidence_count': len(matched_evidence),
            })

        confirmed = sum(1 for r in results if r['status'] == 'CONFIRMED')
        rejected  = sum(1 for r in results if r['status'] == 'REJECTED')
        untested  = sum(1 for r in results if r['status'] == 'UNTESTED')

        return {
            'results': results,
            'confirmed': confirmed,
            'rejected': rejected,
            'untested': untested,
            'total': len(results),
        }

    # ───────────────────────────────────────────────────────────────────────
    # 3. Market Validity Report (MVR) generation
    # ───────────────────────────────────────────────────────────────────────

    def generate_market_validity_report(
        self,
        venture_record: VentureRecord,
        evidence_items: list,
        competitors: list,
        market_data: dict,
    ) -> dict:
        """
        CEO Section 3.3: "At the end of Phase 3, the user receives a Market Validity Report."

        market_data keys expected:
          - target_segment: str
          - pain_intensity: LOW | MEDIUM | HIGH | CRITICAL
          - willingness_to_pay: bool
          - estimated_price_range: str (optional)
          - market_timing: str (optional)
          - market_size_note: str (optional)
        """
        evidence_score = self.score_evidence(evidence_items)
        assumption_eval = self.evaluate_assumptions(
            venture_record.assumptions or [], evidence_items
        )

        pain = market_data.get('pain_intensity', 'MEDIUM')
        wtp  = market_data.get('willingness_to_pay', False)

        # Overall market validity
        validity_factors = [
            evidence_score['score'] >= MIN_PROCEED_SCORE,
            evidence_score['has_direct'] or evidence_score['has_behavioral'],
            pain in ('HIGH', 'CRITICAL'),
            wtp,
            assumption_eval['rejected'] < assumption_eval['total'] * 0.5 if assumption_eval['total'] else True,
            len(competitors) > 0,  # competitor awareness = good
        ]
        validity_score = int(sum(validity_factors) / len(validity_factors) * 100)

        # Final recommendation
        if validity_score >= 70:
            final_rec = 'PROCEED_TO_PHASE4'
        elif validity_score >= 45:
            final_rec = 'MORE_VALIDATION_NEEDED'
        elif validity_score >= 25:
            final_rec = 'REVISE_IDEA'
        else:
            final_rec = 'PIVOT_OR_STOP'

        # Gaps — what the user still needs to fill
        gaps = []
        if evidence_score['evidence_count'] < 3:
            gaps.append('More evidence needed — target at least 3 distinct sources')
        if not evidence_score['has_direct']:
            gaps.append('No direct evidence yet — speak to real potential customers/beneficiaries')
        if pain not in ('HIGH', 'CRITICAL'):
            gaps.append('Pain intensity is low — the problem may not be urgent enough')
        if not wtp and venture_record.venture_type == 'FORPROFIT':
            gaps.append('Willingness to pay not confirmed — test pricing assumptions')
        if assumption_eval['untested'] > 0:
            gaps.append(f"{assumption_eval['untested']} assumption(s) still untested")

        return {
            'generated_at': datetime.utcnow().isoformat(),
            'venture_id': venture_record.id,
            'evidence_score': evidence_score,
            'assumption_evaluation': assumption_eval,
            'competitor_count': len(competitors),
            'market_data': market_data,
            'validity_score': validity_score,
            'final_recommendation': final_rec,
            'validation_gaps': gaps,
            'pain_assessment': pain,
            'willingness_to_pay': wtp,
            'ready_for_business_pillars': final_rec == 'PROCEED_TO_PHASE4',
        }

    # ───────────────────────────────────────────────────────────────────────
    # 4. Interview script generation
    # ───────────────────────────────────────────────────────────────────────

    def generate_interview_script(self, venture: VentureRecord) -> dict:
        """
        CEO: "The platform may prepare outreach messages, interview scripts,
        research plans, survey questions, and evidence templates."
        """
        problem = venture.problem_statement or 'your problem area'
        target  = venture.target_user_hypothesis or 'potential users'
        vp      = venture.value_proposition or 'your solution'

        return {
            'intro': (
                f"Hi [Name], I'm exploring an idea around {problem}. "
                f"I'd love 15 minutes to understand how you currently deal with this. "
                f"Not selling anything — purely looking to learn."
            ),
            'questions': [
                f"Tell me about the last time you experienced {problem}.",
                "How did you handle it? What did you try?",
                "What was most frustrating about that experience?",
                "What does a good solution look like to you?",
                f"If {vp} existed, what would make you trust it enough to use it?",
                "What would you expect to pay for a solution like that, per month?",
                "Who else in your organisation/network deals with this?",
                "Is there anything I haven't asked that I should understand?",
            ],
            'closing': (
                "Thank you — this is extremely helpful. May I follow up if I have more questions? "
                "I'll share what I build if it ever comes to life."
            ),
            'target_profile': target,
            'note': (
                "Aim for 5–10 conversations before drawing conclusions. "
                "Look for patterns, not just individual opinions. "
                "CEO rule: curiosity ≠ demand. Payment or repeat behaviour = demand."
            ),
        }

    # ───────────────────────────────────────────────────────────────────────
    # 5. Validate competitor submission
    # ───────────────────────────────────────────────────────────────────────

    def validate_competitor(self, data: dict) -> tuple[bool, str]:
        name = (data.get('name') or '').strip()
        if not name:
            return False, 'Competitor name is required'
        if len(name) > 200:
            return False, 'Name too long'
        return True, ''
