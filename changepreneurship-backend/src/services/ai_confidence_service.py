"""
AI Confidence Service — Sprint 5 (S5-03)
============================================
CEO (Section 7.3): "Every AI output has a confidence label.
The user always knows how reliable the AI's output is."

Confidence tiers (ascending):
  SPECULATIVE — AI made it up, no grounding
  LOW         — AI reasoning with weak inputs
  MEDIUM      — AI reasoning with structured inputs + some context
  HIGH        — AI reasoning with rich context + validated inputs
  VERIFIED    — Human or behavioral validation applied (NOT AI alone)

CEO invariant: AI alone cannot produce VERIFIED outputs.
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Tier constants (ordered)
CONFIDENCE_SPECULATIVE = 'SPECULATIVE'
CONFIDENCE_LOW = 'LOW'
CONFIDENCE_MEDIUM = 'MEDIUM'
CONFIDENCE_HIGH = 'HIGH'
CONFIDENCE_VERIFIED = 'VERIFIED'  # Only humans / behavioral evidence can reach this

CONFIDENCE_ORDER = [
    CONFIDENCE_SPECULATIVE,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_HIGH,
    CONFIDENCE_VERIFIED,
]


@dataclass
class ConfidenceAssessment:
    label: str
    score: float  # 0.0-1.0
    rationale: str
    can_act_on: bool
    caveats: List[str]

    def to_dict(self):
        return {
            'label': self.label,
            'score': self.score,
            'rationale': self.rationale,
            'can_act_on': self.can_act_on,
            'caveats': self.caveats,
        }


class AIConfidenceService:
    """
    Evaluates and labels AI output confidence.
    Rules are based on input quality + task type + context richness.
    """

    # Tasks with higher baseline uncertainty
    _HIGH_UNCERTAINTY_TASKS = {
        'GENERATE_CVC',
        'GENERATE_ASSUMPTIONS',
        'REROUTE_MESSAGE',
    }

    # Tasks with lower uncertainty (more rule-based inputs)
    _LOWER_UNCERTAINTY_TASKS = {
        'CONTRADICTION_CHECK',
        'NARRATIVE_PHASE1',
    }

    def assess_confidence(
        self,
        task_type: str,
        inputs: dict,
        output: str,
        context_richness: int = 0,  # 0-10
    ) -> ConfidenceAssessment:
        """
        Assess confidence of an AI output.
        context_richness = count of non-empty structured inputs provided.
        """
        score = self._compute_score(task_type, inputs, context_richness)
        label = self._score_to_label(score)
        caveats = self._build_caveats(task_type, label, inputs)

        can_act_on = label in (CONFIDENCE_MEDIUM, CONFIDENCE_HIGH, CONFIDENCE_VERIFIED)

        return ConfidenceAssessment(
            label=label,
            score=score,
            rationale=self._rationale(task_type, score, context_richness),
            can_act_on=can_act_on,
            caveats=caveats,
        )

    def label_assumption(self, source: str, evidence_count: int = 0) -> str:
        """Label an assumption based on its source and evidence backing."""
        if source == 'ai' and evidence_count == 0:
            return CONFIDENCE_SPECULATIVE
        if source == 'ai':
            return CONFIDENCE_LOW
        if source == 'user' and evidence_count == 0:
            return CONFIDENCE_LOW
        if evidence_count >= 3:
            return CONFIDENCE_HIGH
        if evidence_count >= 1:
            return CONFIDENCE_MEDIUM
        return CONFIDENCE_LOW

    def can_upgrade_to_verified(self, source: str) -> bool:
        """CEO invariant: AI alone can never produce VERIFIED outputs."""
        return source != 'ai'

    # ------------------------------------------------------------------
    def _compute_score(self, task_type: str, inputs: dict, context_richness: int) -> float:
        base = 0.4

        # Input quality
        non_empty = sum(1 for v in inputs.values() if v and len(str(v)) > 10)
        input_quality = min(non_empty / max(len(inputs), 1), 1.0)
        base += input_quality * 0.3

        # Context richness bonus
        base += min(context_richness / 10, 0.2)

        # Task-type adjustment
        if task_type in self._HIGH_UNCERTAINTY_TASKS:
            base *= 0.85
        elif task_type in self._LOWER_UNCERTAINTY_TASKS:
            base *= 1.1

        return round(min(max(base, 0.0), 0.89), 3)  # max 0.89 for AI (never VERIFIED)

    def _score_to_label(self, score: float) -> str:
        if score >= 0.80:
            return CONFIDENCE_HIGH
        if score >= 0.60:
            return CONFIDENCE_MEDIUM
        if score >= 0.40:
            return CONFIDENCE_LOW
        return CONFIDENCE_SPECULATIVE

    def _rationale(self, task_type: str, score: float, context_richness: int) -> str:
        if score >= 0.80:
            return f'Rich context ({context_richness}/10 inputs) provided strong grounding for {task_type}.'
        if score >= 0.60:
            return f'Moderate context provided for {task_type}. Validate before acting.'
        if score >= 0.40:
            return f'Limited context for {task_type}. Treat as hypothesis only.'
        return f'Minimal grounding for {task_type}. Highly speculative — do not act without research.'

    def _build_caveats(self, task_type: str, label: str, inputs: dict) -> List[str]:
        caveats = []
        if label in (CONFIDENCE_SPECULATIVE, CONFIDENCE_LOW):
            caveats.append('This output is AI-generated with limited input data. Treat as a starting point, not a conclusion.')
        if task_type == 'GENERATE_ASSUMPTIONS':
            caveats.append('AI-generated assumptions are never verified facts. Test each one independently.')
        if task_type == 'GENERATE_CVC':
            caveats.append('Clarified Venture Concept is a draft until you approve it.')
        if not inputs.get('problem_description') and not inputs.get('problem'):
            caveats.append('No problem statement provided — outputs are highly speculative.')
        return caveats
