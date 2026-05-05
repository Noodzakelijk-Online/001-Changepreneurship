"""
AssumptionTracker — Sprint 3 (S3-03)
======================================
CEO (Section 2.5): every assumption must be tracked and labelled.
Distinguishes: assumption / weak signal / partial validation / strong validation /
behavioral evidence / professional opinion / verified fact / user belief /
projection / speculation

Rules:
  - AI-generated assumptions always typed AI_RESEARCH (not VERIFIED_FACT)
  - User must explicitly mark assumption as Tested after validation
  - Dashboard shows: % tested vs assumed
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Assumption types (confidence tier)
ASSUMPTION_TYPE_USER_BELIEF = 'USER_BELIEF'
ASSUMPTION_TYPE_AI_RESEARCH = 'AI_RESEARCH'
ASSUMPTION_TYPE_DESK_RESEARCH = 'DESK_RESEARCH'
ASSUMPTION_TYPE_PROFESSIONAL_OPINION = 'PROFESSIONAL_OPINION'
ASSUMPTION_TYPE_WEAK_SIGNAL = 'WEAK_SIGNAL'
ASSUMPTION_TYPE_PARTIAL_VALIDATION = 'PARTIAL_VALIDATION'
ASSUMPTION_TYPE_STRONG_VALIDATION = 'STRONG_VALIDATION'
ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE = 'BEHAVIORAL_EVIDENCE'
ASSUMPTION_TYPE_VERIFIED_FACT = 'VERIFIED_FACT'

# Confidence tier order (higher index = stronger)
ASSUMPTION_CONFIDENCE_ORDER = [
    ASSUMPTION_TYPE_USER_BELIEF,        # 0
    ASSUMPTION_TYPE_AI_RESEARCH,        # 1 — CEO: AI outputs are never VERIFIED
    ASSUMPTION_TYPE_DESK_RESEARCH,      # 2
    ASSUMPTION_TYPE_WEAK_SIGNAL,        # 3
    ASSUMPTION_TYPE_PROFESSIONAL_OPINION,  # 4
    ASSUMPTION_TYPE_PARTIAL_VALIDATION, # 5
    ASSUMPTION_TYPE_STRONG_VALIDATION,  # 6
    ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE,# 7
    ASSUMPTION_TYPE_VERIFIED_FACT,      # 8
]

# AI outputs max at this tier (CEO invariant)
AI_ASSUMPTION_MAX_TIER = ASSUMPTION_TYPE_AI_RESEARCH


@dataclass
class Assumption:
    id: str
    venture_id: Optional[int]
    claim: str
    assumption_type: str
    source: str
    tested: bool = False
    test_result: Optional[str] = None
    supporting_evidence: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tested_at: Optional[str] = None

    @property
    def confidence_tier(self):
        try:
            return ASSUMPTION_CONFIDENCE_ORDER.index(self.assumption_type)
        except ValueError:
            return 0

    def to_dict(self):
        return {
            'id': self.id,
            'venture_id': self.venture_id,
            'claim': self.claim,
            'assumption_type': self.assumption_type,
            'confidence_tier': self.confidence_tier,
            'confidence_label': self._confidence_label(),
            'source': self.source,
            'tested': self.tested,
            'test_result': self.test_result,
            'supporting_evidence': self.supporting_evidence,
            'created_at': self.created_at,
            'tested_at': self.tested_at,
        }

    def _confidence_label(self):
        labels = {
            ASSUMPTION_TYPE_USER_BELIEF: 'User Belief — no external validation',
            ASSUMPTION_TYPE_AI_RESEARCH: 'AI Research — not independently verified',
            ASSUMPTION_TYPE_DESK_RESEARCH: 'Desk Research — secondary sources only',
            ASSUMPTION_TYPE_WEAK_SIGNAL: 'Weak Signal — limited direct evidence',
            ASSUMPTION_TYPE_PROFESSIONAL_OPINION: 'Professional Opinion — expert but not user validation',
            ASSUMPTION_TYPE_PARTIAL_VALIDATION: 'Partial Validation — some evidence, not conclusive',
            ASSUMPTION_TYPE_STRONG_VALIDATION: 'Strong Validation — multiple corroborating sources',
            ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE: 'Behavioral Evidence — actions speak louder than words',
            ASSUMPTION_TYPE_VERIFIED_FACT: 'Verified Fact — independently confirmed',
        }
        return labels.get(self.assumption_type, 'Unknown')


@dataclass
class AssumptionSummary:
    venture_id: Optional[int]
    total: int
    tested: int
    untested: int
    tested_pct: float
    by_type: dict
    pending: List[dict]
    high_risk_untested: List[dict]


class AssumptionTracker:
    """
    Stateless tracker. Works on lists of Assumption dicts (from VentureRecord.assumptions).
    Production: reads/writes VentureRecord.assumptions JSON column.
    """

    def create_assumption(
        self,
        venture_id: Optional[int],
        claim: str,
        assumption_type: str,
        source: str = 'user',
    ) -> Assumption:
        """
        Create a new assumption.
        AI-generated assumptions are capped at AI_RESEARCH tier (CEO invariant).
        """
        # CEO invariant: AI cannot produce VERIFIED_FACT
        if source == 'ai' and ASSUMPTION_CONFIDENCE_ORDER.index(assumption_type) > ASSUMPTION_CONFIDENCE_ORDER.index(AI_ASSUMPTION_MAX_TIER):
            assumption_type = AI_ASSUMPTION_MAX_TIER
            logger.warning(
                "AI assumption type capped to %s (CEO invariant: AI cannot produce verified facts)",
                AI_ASSUMPTION_MAX_TIER,
            )

        assumption_id = f"a_{venture_id or 0}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        return Assumption(
            id=assumption_id,
            venture_id=venture_id,
            claim=claim,
            assumption_type=assumption_type,
            source=source,
        )

    def mark_tested(
        self,
        assumption: Assumption,
        test_result: str,
        evidence_ids: Optional[List[str]] = None,
        new_type: Optional[str] = None,
    ) -> Assumption:
        """
        User explicitly marks assumption as tested.
        Optionally upgrades assumption_type based on evidence.
        """
        assumption.tested = True
        assumption.test_result = test_result
        assumption.tested_at = datetime.utcnow().isoformat()
        if evidence_ids:
            assumption.supporting_evidence = evidence_ids
        if new_type and new_type in ASSUMPTION_CONFIDENCE_ORDER:
            assumption.assumption_type = new_type
        return assumption

    def get_assumption_confidence(self, assumption: Assumption) -> dict:
        return {
            'tier': assumption.confidence_tier,
            'label': assumption._confidence_label(),
            'can_use_externally': assumption.assumption_type not in (
                ASSUMPTION_TYPE_USER_BELIEF,
                ASSUMPTION_TYPE_AI_RESEARCH,
            ),
        }

    def get_pending_validation(self, assumptions: List[dict]) -> List[dict]:
        """Returns list of untested assumptions from a raw dict list."""
        return [a for a in assumptions if not a.get('tested', False)]

    def compute_summary(self, assumptions: List[dict], venture_id=None) -> AssumptionSummary:
        """Compute summary statistics for an assumption list."""
        total = len(assumptions)
        tested = sum(1 for a in assumptions if a.get('tested', False))
        untested = total - tested
        tested_pct = round(tested / total * 100, 1) if total else 0.0

        by_type = {}
        for a in assumptions:
            t = a.get('assumption_type', 'UNKNOWN')
            by_type[t] = by_type.get(t, 0) + 1

        pending = [a for a in assumptions if not a.get('tested', False)]

        # High-risk: AI/belief assumptions that are untested
        high_risk = [
            a for a in pending
            if a.get('assumption_type') in (
                ASSUMPTION_TYPE_USER_BELIEF,
                ASSUMPTION_TYPE_AI_RESEARCH,
            )
        ]

        return AssumptionSummary(
            venture_id=venture_id,
            total=total,
            tested=tested,
            untested=untested,
            tested_pct=tested_pct,
            by_type=by_type,
            pending=[a for a in pending[:10]],
            high_risk_untested=high_risk[:5],
        )

    def update_with_evidence(
        self,
        assumption: Assumption,
        evidence_type: str,
        evidence_strength: str,
        description: str,
    ) -> Assumption:
        """
        Updates assumption confidence based on submitted evidence.
        Maps evidence strength to assumption type upgrade.
        """
        strength_to_type = {
            'BEHAVIORAL': ASSUMPTION_TYPE_BEHAVIORAL_EVIDENCE,
            'DIRECT': ASSUMPTION_TYPE_STRONG_VALIDATION,
            'INDIRECT': ASSUMPTION_TYPE_PARTIAL_VALIDATION,
            'DESK_RESEARCH': ASSUMPTION_TYPE_DESK_RESEARCH,
            'AI_RESEARCH': ASSUMPTION_TYPE_AI_RESEARCH,
            'OPINION': ASSUMPTION_TYPE_PROFESSIONAL_OPINION,
            'BELIEF': ASSUMPTION_TYPE_USER_BELIEF,
        }
        new_type = strength_to_type.get(evidence_strength, assumption.assumption_type)

        # Only upgrade, never downgrade
        current_tier = assumption.confidence_tier
        new_tier = ASSUMPTION_CONFIDENCE_ORDER.index(new_type) if new_type in ASSUMPTION_CONFIDENCE_ORDER else 0
        if new_tier > current_tier:
            assumption.assumption_type = new_type

        assumption.supporting_evidence.append(f"{evidence_type}: {description[:100]}")
        return assumption
