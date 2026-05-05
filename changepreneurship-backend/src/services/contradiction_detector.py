"""
ContradictionDetector — Sprint 2 (S2-04)
=========================================
Detects logical contradictions between a user's stated values/constraints
and their stated intentions/goals.

CEO Section 3.4 Example 5:
  "User says very low risk tolerance but wants to quit job, take loans,
  build a high-risk product → contradiction."

Rules:
  - Level 3 contradiction = Soft Block (slow down, explain)
  - Level 4+ contradiction = must be resolved before progress on that dimension
  - NEVER block on a single data point alone — must be multiple corroborating signals
  - Contradiction is NOT a failure; it is information to surface and discuss
"""
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONTRADICTION_LEVEL_NOTE = 1       # Informational, no block
CONTRADICTION_LEVEL_WARNING = 2    # Warning, pace down
CONTRADICTION_LEVEL_SOFT = 3       # Soft block on affected dimension
CONTRADICTION_LEVEL_HARD = 4       # Must resolve before progress


@dataclass
class Contradiction:
    type: str
    level: int
    dimension_a: str
    dimension_b: str
    explanation: str
    recommendation: str
    affected_actions: List[str] = field(default_factory=list)


@dataclass
class ContradictionResult:
    contradictions: List[Contradiction]
    max_level: int
    has_blocking_contradiction: bool  # level >= 4
    summary: str


class ContradictionDetector:
    """
    Stateless detector — call evaluate(responses) with the current answer set.
    """

    def evaluate(self, responses: dict) -> ContradictionResult:
        """
        Evaluate all contradiction rules against the given response dict.
        Returns ContradictionResult.
        """
        found: List[Contradiction] = []
        r = responses

        # -- Rule 1: Low risk tolerance + high-risk actions ---------------
        risk_tol = int(r.get('risk_tolerance', 3))
        actions = r.get('intended_actions', [])

        if risk_tol <= 1:
            if r.get('intend_to_quit_job'):
                found.append(Contradiction(
                    type='RISK_ACTION_MISMATCH',
                    level=CONTRADICTION_LEVEL_HARD,
                    dimension_a='risk_tolerance',
                    dimension_b='intended_actions',
                    explanation=(
                        'You indicated a very low risk tolerance, but also plan to '
                        'quit your job to pursue this. Quitting employment is a high-risk action.'
                    ),
                    recommendation=(
                        'Consider building this as a side project until it generates income '
                        'that replaces your salary, or revisit your risk tolerance assessment.'
                    ),
                    affected_actions=['quit_job'],
                ))

            if r.get('intend_to_take_loan'):
                found.append(Contradiction(
                    type='RISK_ACTION_MISMATCH',
                    level=CONTRADICTION_LEVEL_HARD,
                    dimension_a='risk_tolerance',
                    dimension_b='intended_actions',
                    explanation=(
                        'You indicated a very low risk tolerance, but plan to take on debt '
                        'to fund this venture. Debt increases your personal financial risk significantly.'
                    ),
                    recommendation=(
                        'Consider starting without debt and only adding financing once you have '
                        'evidence that the venture works.'
                    ),
                    affected_actions=['take_loan', 'debt_financing'],
                ))

            venture_risk = int(r.get('venture_risk_level', 2))
            if venture_risk >= 4:
                found.append(Contradiction(
                    type='RISK_VENTURE_MISMATCH',
                    level=CONTRADICTION_LEVEL_SOFT,
                    dimension_a='risk_tolerance',
                    dimension_b='venture_risk_level',
                    explanation=(
                        f'Your risk tolerance ({risk_tol}/5) is much lower than the '
                        f'venture type requires ({venture_risk}/5).'
                    ),
                    recommendation=(
                        'Consider a lower-risk venture variant, a co-founder with higher '
                        'risk tolerance, or a lifestyle-business model that reduces exposure.'
                    ),
                    affected_actions=['high_commitment_pivots', 'major_financial_bets'],
                ))

        # -- Rule 2: Zero runway + paid development intent ----------------
        runway = float(r.get('financial_runway_months', 6))
        if runway < 1 and r.get('intend_paid_development'):
            found.append(Contradiction(
                type='RUNWAY_ACTION_MISMATCH',
                level=CONTRADICTION_LEVEL_HARD,
                dimension_a='financial_runway',
                dimension_b='intended_actions',
                explanation=(
                    'You have less than 1 month of financial runway, but plan to spend '
                    'on development. This combination is high-risk and unsustainable.'
                ),
                recommendation=(
                    'Secure financial stability first. Use the free path '
                    '(conversations, research, planning) until you have 3+ months of runway.'
                ),
                affected_actions=['paid_development', 'outsourcing', 'hiring'],
            ))

        # -- Rule 3: Mission = social impact + model = aggressive VC ------
        motivation = r.get('motivation_type', '')
        funding_model = r.get('funding_model_preference', '')
        venture_type = r.get('venture_type', '')

        if motivation == 'IMPACT' and venture_type in ('SOCIAL', 'NON_PROFIT'):
            if funding_model in ('AGGRESSIVE_VC', 'QUICK_EXIT', 'HIGH_GROWTH'):
                found.append(Contradiction(
                    type='MISSION_MODEL_MISMATCH',
                    level=CONTRADICTION_LEVEL_WARNING,
                    dimension_a='motivation_type',
                    dimension_b='funding_model_preference',
                    explanation=(
                        'Your stated mission is social impact, but your preferred funding model '
                        'is oriented toward rapid growth and exit. These can conflict — VC investors '
                        'typically prioritise returns over mission.'
                    ),
                    recommendation=(
                        'Consider grant funding, impact investment, revenue-based financing, '
                        'or mission-aligned investors who accept patient capital.'
                    ),
                    affected_actions=[],
                ))

        # -- Rule 4: Escape motivation + zero evidence --------------------
        if motivation in ('ESCAPIST',) and not r.get('has_spoken_to_users') and not r.get('has_validated'):
            found.append(Contradiction(
                type='MOTIVATION_EVIDENCE_GAP',
                level=CONTRADICTION_LEVEL_WARNING,
                dimension_a='motivation_type',
                dimension_b='evidence_level',
                explanation=(
                    'Your primary motivation appears to be escaping your current situation. '
                    'Without any market evidence, ventures built primarily around escape '
                    'tend to have higher failure rates.'
                ),
                recommendation=(
                    'Before going further, speak to at least 3 potential customers. '
                    'This costs nothing and will give you much better signal.'
                ),
                affected_actions=[],
            ))

        # -- Rule 5: Time available < 5h + goal = full-time business ------
        hours = float(r.get('weekly_available_hours', 10))
        goal_type = r.get('venture_goal_type', '')

        if hours < 5 and goal_type in ('FULL_TIME_REPLACEMENT', 'SCALE_FAST', 'FULL_TIME'):
            found.append(Contradiction(
                type='CAPACITY_GOAL_MISMATCH',
                level=CONTRADICTION_LEVEL_WARNING,
                dimension_a='time_capacity',
                dimension_b='venture_goal_type',
                explanation=(
                    f'You have {hours:.0f} hours/week available, but your goal is to build '
                    f'a full-time business. Most ventures require 15-20+ hours/week to '
                    f'reach income-replacement level.'
                ),
                recommendation=(
                    'Either adjust the timeline expectations (this will take 2-3x longer), '
                    'or identify which commitments could be reduced to free up more time.'
                ),
                affected_actions=[],
            ))

        # -- Rule 6: Strong domain skills + "no-one has this problem" -----
        skill = int(r.get('domain_skill_level', 0))
        problem_validated = r.get('problem_real_for_others', True)

        if skill >= 4 and not problem_validated and r.get('idea_based_on_own_frustration'):
            found.append(Contradiction(
                type='EXPERT_BLIND_SPOT',
                level=CONTRADICTION_LEVEL_WARNING,
                dimension_a='skills_experience',
                dimension_b='market_validity',
                explanation=(
                    'Your domain expertise is high, which is great — but experts sometimes '
                    'build solutions that only they need. Your frustration is a valid signal, '
                    'but it needs to be validated with people outside your level of expertise.'
                ),
                recommendation=(
                    'Interview 5-10 potential customers who are NOT experts in your domain. '
                    'Pay special attention to how they describe the problem.'
                ),
                affected_actions=[],
            ))

        # -- Rule 7: Paying customers + planning major pivot ---------------
        if r.get('paying_customers_exist') and r.get('planning_major_pivot'):
            found.append(Contradiction(
                type='TRACTION_PIVOT_TENSION',
                level=CONTRADICTION_LEVEL_WARNING,
                dimension_a='market_validity',
                dimension_b='intended_actions',
                explanation=(
                    'You already have paying customers, but plan a major pivot. '
                    'Pivoting away from what already works is a high-risk move that '
                    'deserves careful analysis first.'
                ),
                recommendation=(
                    'Before pivoting, document exactly why current customers pay you. '
                    'Interview at least 3 of them about the proposed change direction.'
                ),
                affected_actions=['major_pivot'],
            ))

        max_level = max((c.level for c in found), default=0)
        has_blocking = any(c.level >= CONTRADICTION_LEVEL_HARD for c in found)

        if not found:
            summary = 'No significant contradictions detected.'
        elif has_blocking:
            summary = (
                f'{len(found)} contradiction(s) detected, including {sum(1 for c in found if c.level >= 4)} '
                f'that require resolution before you can continue.'
            )
        else:
            summary = (
                f'{len(found)} potential inconsistency(ies) noted. '
                f'These are worth reflecting on — they do not block your progress.'
            )

        return ContradictionResult(
            contradictions=found,
            max_level=max_level,
            has_blocking_contradiction=has_blocking,
            summary=summary,
        )
