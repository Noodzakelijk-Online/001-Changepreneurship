"""
Phase2IdeaService — Sprint 3 (S3-02)
======================================
Phase 2: Idea Discovery — turns a rough idea into a Clarified Venture Concept.

CEO (Section 3.3, Phase 2):
  "Turn the user's rough idea into a clear venture concept.
   This phase does not yet prove the idea is good — it makes it clear
   enough to be tested."

Layer 1 rules (S3-02, CEO Section 4.3):
  - Target = "everyone" → Level 4 Block (market research blocked)
  - Problem undefined    → Level 4 Block
  - Only features, no value → Level 3 Soft Block
  - User/customer/payer confused → Level 3
  - First use case undefined → Level 3

Layer 3 AI: generates CVC only if Layer 1 has no Level 4 blocks.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import logging

from src.services.phase1_rule_engine import (
    LEVEL_HEALTHY, LEVEL_OK, LEVEL_WARNING,
    LEVEL_SOFT_BLOCK, LEVEL_HARD_BLOCK,
)

logger = logging.getLogger(__name__)

# Idea clarity block levels
IDEA_BLOCK_NONE = 0
IDEA_BLOCK_SOFT = LEVEL_SOFT_BLOCK       # 3
IDEA_BLOCK_HARD = LEVEL_HARD_BLOCK       # 4

# Everyone-targeting keywords
_EVERYONE_KEYWORDS = {
    'everyone', 'anybody', 'everyone who', 'all people',
    'all businesses', 'any business', 'anyone with',
    'every person', 'all users', 'universal', 'whole world',
}

# Feature-only indicators (no value prop)
_FEATURE_PHRASES = [
    'dashboard', 'app that', 'platform that', 'tool that',
    'system that tracks', 'software that', 'website where',
]


@dataclass
class IdeaBlocker:
    type: str
    level: int
    what_is_blocked: List[str]
    what_is_allowed: List[str]
    unlock_condition: str
    explanation: str


@dataclass
class Phase2Result:
    idea_block_level: int
    blockers: List[IdeaBlocker]
    can_generate_cvc: bool
    clarity_score: int          # 0-100
    venture_type_hint: Optional[str]
    missing_elements: List[str]
    # Set by AI after generation:
    cvc_generated: bool = False
    problem_statement: Optional[str] = None
    target_user_hypothesis: Optional[str] = None
    value_proposition: Optional[str] = None
    assumptions: List[dict] = field(default_factory=list)
    open_questions: List[dict] = field(default_factory=list)


class Phase2IdeaService:
    """
    Layer 1: evaluates idea clarity and blocks if needed.
    Layer 3: generates CVC if Layer 1 is clear.
    Stateless — accepts responses dict.
    """

    def evaluate_idea_clarity(self, responses: dict) -> Phase2Result:
        """
        Run Layer 1 checks on idea responses.
        Returns Phase2Result with blockers and clarity score.
        """
        blockers = []
        missing = []
        r = responses

        idea_desc = str(r.get('idea_description', '') or '').lower()
        target_user = str(r.get('target_user_description', '') or '').lower()
        problem = str(r.get('problem_description', '') or r.get('problem_defined', '') or '')
        value_prop = str(r.get('value_prop', '') or r.get('value_proposition', '') or '')
        use_case = str(r.get('first_use_case', '') or '')
        user_payer_diff = r.get('user_customer_payer_different')

        # --- Check: Problem defined ---
        problem_ok = bool(problem and len(str(problem).strip()) > 10)
        if not problem_ok:
            missing.append('problem_statement')
            blockers.append(IdeaBlocker(
                type='PROBLEM_UNDEFINED',
                level=IDEA_BLOCK_HARD,
                what_is_blocked=['market_research', 'business_plan', 'investor_outreach'],
                what_is_allowed=['idea_journaling', 'problem_interviews', 'observation_tasks'],
                unlock_condition=(
                    'Define a specific problem: who experiences it, when, how often, and why it matters.'
                ),
                explanation=(
                    'A venture without a clear problem is a solution looking for a purpose. '
                    'Define the problem before anything else.'
                ),
            ))

        # --- Check: Target = "everyone" ---
        targeting_everyone = any(kw in target_user for kw in _EVERYONE_KEYWORDS)
        if targeting_everyone or (not target_user and not r.get('target_user_specific')):
            if targeting_everyone:
                missing.append('specific_target_user')
                blockers.append(IdeaBlocker(
                    type='TARGET_TOO_BROAD',
                    level=IDEA_BLOCK_HARD,
                    what_is_blocked=['market_research', 'messaging', 'business_plan'],
                    what_is_allowed=['persona_building', 'customer_interviews', 'niche_research'],
                    unlock_condition=(
                        'Describe your target user in one sentence without using "everyone" '
                        'or "any business". Include: who they are, what they do, what they struggle with.'
                    ),
                    explanation=(
                        '"Everyone" is not a customer. '
                        'Every downstream output — messaging, pricing, channels — depends on a specific target.'
                    ),
                ))
            else:
                missing.append('target_user_description')

        # --- Check: Only features, no value ---
        only_features = (
            value_prop
            and any(phrase in value_prop.lower() for phrase in _FEATURE_PHRASES)
            and 'save' not in value_prop.lower()
            and 'help' not in value_prop.lower()
            and 'allow' not in value_prop.lower()
            and 'enable' not in value_prop.lower()
        )
        if only_features or (idea_desc and not value_prop):
            missing.append('value_proposition')
            blockers.append(IdeaBlocker(
                type='FEATURES_NO_VALUE',
                level=IDEA_BLOCK_SOFT,
                what_is_blocked=['go_to_market', 'pricing_definition'],
                what_is_allowed=[
                    'customer_discovery', 'pain_point_mapping',
                    'problem_statement_refinement',
                ],
                unlock_condition=(
                    'Describe the value delivered to the user: time saved, money saved, '
                    'pain eliminated, or goal enabled.'
                ),
                explanation=(
                    'A list of features is not a value proposition. '
                    'Customers buy outcomes, not features.'
                ),
            ))

        # --- Check: User/customer/payer confused ---
        if user_payer_diff is None and r.get('has_b2b_element'):
            missing.append('user_customer_payer_clarity')
            blockers.append(IdeaBlocker(
                type='USER_PAYER_UNCLEAR',
                level=IDEA_BLOCK_SOFT,
                what_is_blocked=['pricing_strategy', 'sales_strategy'],
                what_is_allowed=['stakeholder_mapping', 'customer_interviews'],
                unlock_condition=(
                    'Clarify: who uses the product, who decides to buy it, and who pays for it. '
                    'These can be three different people in B2B.'
                ),
                explanation=(
                    'In B2B ventures, the user, buyer, and payer are often different people. '
                    'Confusing them leads to wrong pricing and sales strategy.'
                ),
            ))

        # --- Check: First use case ---
        if not use_case and r.get('current_phase', 1) >= 2:
            missing.append('first_use_case')
            blockers.append(IdeaBlocker(
                type='NO_FIRST_USE_CASE',
                level=IDEA_BLOCK_SOFT,
                what_is_blocked=['prototype', 'mvp_scope'],
                what_is_allowed=['use_case_mapping', 'customer_journey_draft'],
                unlock_condition=(
                    'Describe the single first scenario where someone uses your product '
                    'and gets value from it.'
                ),
                explanation=(
                    'Without a first use case, MVP scope is undefined. '
                    'Define one scenario where the product solves one problem for one person.'
                ),
            ))

        # --- Clarity score (0-100) ---
        max_score = 100
        deductions = 0
        if not problem_ok:
            deductions += 35
        if targeting_everyone:
            deductions += 30
        if only_features or not value_prop:
            deductions += 20
        if not use_case:
            deductions += 15
        clarity_score = max(0, max_score - deductions)

        # --- Venture type hint ---
        venture_type_hint = self._infer_venture_type(idea_desc, r)

        # --- Max block level ---
        max_level = max((b.level for b in blockers), default=IDEA_BLOCK_NONE)
        can_generate_cvc = max_level < IDEA_BLOCK_HARD

        return Phase2Result(
            idea_block_level=max_level,
            blockers=blockers,
            can_generate_cvc=can_generate_cvc,
            clarity_score=clarity_score,
            venture_type_hint=venture_type_hint,
            missing_elements=missing,
        )

    def generate_cvc_from_responses(self, responses: dict, result: Phase2Result) -> Phase2Result:
        """
        Generates a Clarified Venture Concept using templates when AI unavailable.
        Called after evaluate_idea_clarity() confirms can_generate_cvc=True.
        In production, this triggers Phase1NarrativeService equivalent for Phase 2.
        """
        if not result.can_generate_cvc:
            return result

        r = responses
        idea = r.get('idea_description', '')
        target = r.get('target_user_description', r.get('target_user', ''))
        problem = r.get('problem_description', r.get('problem_defined', ''))
        value = r.get('value_prop', r.get('value_proposition', ''))
        use_case = r.get('first_use_case', '')

        # Problem statement template
        problem_statement = (
            problem
            if len(str(problem)) > 20
            else f'[Target users] struggle with [problem]. Current solutions fail because [gap].'
        )

        # Target user hypothesis template
        target_user_hypothesis = (
            f'{target} who needs to {use_case or "solve the defined problem"}.'
            if target
            else 'Target user not yet defined — interview 5 people who match your hypothesis.'
        )

        # Value proposition template
        value_proposition = (
            value
            if len(str(value)) > 20
            else f'Unlike existing solutions, this helps {target} achieve [outcome] by [approach].'
        )

        # Generate initial assumptions (Layer 3 placeholder)
        assumptions = [
            {
                'id': 'a1',
                'claim': f'The target user ({target or "undefined"}) experiences this problem regularly.',
                'type': 'AI_RESEARCH',
                'tested': False,
                'strength': 'BELIEF',
            },
            {
                'id': 'a2',
                'claim': 'Current solutions are insufficient for this use case.',
                'type': 'AI_RESEARCH',
                'tested': False,
                'strength': 'BELIEF',
            },
            {
                'id': 'a3',
                'claim': 'The target user is willing to pay for a better solution.',
                'type': 'AI_RESEARCH',
                'tested': False,
                'strength': 'BELIEF',
            },
        ]

        open_questions = [
            {'id': 'q1', 'question': 'How often does the target user experience this problem?'},
            {'id': 'q2', 'question': 'What do they currently do to solve it?'},
            {'id': 'q3', 'question': 'What would they pay for a better solution?'},
        ]

        result.cvc_generated = True
        result.problem_statement = problem_statement
        result.target_user_hypothesis = target_user_hypothesis
        result.value_proposition = value_proposition
        result.assumptions = assumptions
        result.open_questions = open_questions

        return result

    def _infer_venture_type(self, idea_desc: str, responses: dict) -> Optional[str]:
        """Infer venture type from keywords and responses."""
        mission = str(responses.get('mission_clarity', '') or '').lower()
        combined = (idea_desc + ' ' + mission).lower()

        if any(w in combined for w in ['nonprofit', 'ngo', 'charity', 'donate', 'grant']):
            return 'NONPROFIT'
        if any(w in combined for w in ['social impact', 'community', 'underserved', 'access gap']):
            return 'SOCIAL'
        if any(w in combined for w in ['deep tech', 'research', 'patent', 'phd', 'biotech', 'quantum']):
            return 'DEEPTECH'
        if any(w in combined for w in ['local', 'neighbourhood', 'city', 'municipality']):
            return 'LOCAL'
        return 'FORPROFIT'
