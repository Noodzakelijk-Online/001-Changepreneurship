"""
Phase 1 Rule Engine — Layer 1 (Fixed Rules, No AI)
===================================================
Evaluates founder readiness across 6 Maslow-level dimensions and
7 venture-level dimensions. Produces a typed FounderReadinessResult
that the API then saves as a FounderReadinessProfile.

CRITICAL INVARIANTS (CEO Section 4.2, 4.4, 7.1):
  - Hard blockers (Level 4-5) CANNOT be compensated by high scores elsewhere.
  - Composite = MAX of all levels, never average.
  - Level 5 (Hard Stop) propagates immediately regardless of other dims.
  - AI never overrides this layer's output.
"""
from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Level constants
# ---------------------------------------------------------------------------
LEVEL_HEALTHY = 0
LEVEL_OK = 1
LEVEL_WARNING = 2
LEVEL_SOFT_BLOCK = 3
LEVEL_HARD_BLOCK = 4
LEVEL_HARD_STOP = 5

# ---------------------------------------------------------------------------
# Route constants
# ---------------------------------------------------------------------------
ROUTE_CONTINUE = 'CONTINUE'
ROUTE_STABILIZE = 'STABILIZE'
ROUTE_LOW_CAPITAL = 'LOW_CAPITAL'
ROUTE_OPERATIONS_CLEANUP = 'OPERATIONS_CLEANUP'
ROUTE_IMPACT_SOCIAL = 'IMPACT_SOCIAL'
ROUTE_DEEP_TECH = 'DEEP_TECH'
ROUTE_DEBT_CONSCIOUS = 'DEBT_CONSCIOUS'
ROUTE_CORPORATE_TRANSITION = 'CORPORATE_TRANSITION'
ROUTE_ACCELERATE = 'ACCELERATE'
ROUTE_HARD_STOP = 'HARD_STOP'

# Actions used in blocker descriptions
_PAID_ACTIONS = [
    'paid_development',
    'outsourcing',
    'paid_tools_and_subscriptions',
    'hiring',
    'external_service_spend',
    'marketing_spend',
]
_FREE_ACTIONS = [
    'idea_clarification',
    'free_competitor_research',
    'customer_discovery_conversations',
    'free_outreach_drafting',
    'planning_and_roadmapping',
    'mentor_search_free',
]


@dataclass
class DimensionResult:
    score: int          # 0-100 (higher = better)
    level: int          # 0-5
    blockers: List[dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase1Result:
    # Individual dimensions
    financial: DimensionResult
    time_capacity: DimensionResult
    personal_stability: DimensionResult
    motivation_quality: DimensionResult
    skills_experience: DimensionResult
    idea_clarity: DimensionResult
    founder_idea_fit: DimensionResult
    legal_employment: DimensionResult
    health_energy: DimensionResult

    # Derived / placeholder dims (not fully computed in Phase 1)
    founder_market_fit: DimensionResult
    market_validity: DimensionResult
    business_model: DimensionResult
    network_mentorship: DimensionResult

    # Composite result
    overall_level: int
    recommended_route: str
    active_blockers: List[dict]
    allowed_actions: List[str]
    blocked_actions: List[dict]
    compensation_rules: List[dict]

    # Signals
    burnout_signal: bool = False
    overload_signal: bool = False
    detected_scenario: Optional[str] = None
    founder_type: Optional[str] = None


class Phase1RuleEngine:
    """
    Layer 1 Rule Engine for Phase 1 (Self-Discovery).

    Usage:
        engine = Phase1RuleEngine()
        result = engine.evaluate_all(responses_dict)
    """

    # ------------------------------------------------------------------
    # DIMENSION 1: Financial Readiness
    # ------------------------------------------------------------------
    def evaluate_financial_readiness(
        self,
        runway_months: float,
        income_stable: bool,
        debt_pressure_level: int,   # 0-5
        has_dependants: bool = False,
        high_debt: bool = False,
    ) -> DimensionResult:
        """
        Thresholds (CEO Section 4.2 / MASLOW_SCORING_DESIGN.md):
          Level 5: high_debt + no_income + has_dependants
          Level 4: runway < 1 month  OR  (high_debt AND no_income)
          Level 3: runway 1-2 months
          Level 2: runway 3-5 months
          Level 1: runway 6-11 months  OR  income_stable + 6+ months
          Level 0: runway >= 12 AND income_stable
        """
        blockers = []
        warnings = []

        no_income = not income_stable

        # --- Level 5: Crisis ---
        if high_debt and no_income and has_dependants:
            return DimensionResult(
                score=0,
                level=LEVEL_HARD_STOP,
                blockers=[{
                    'type': 'FINANCIAL_CRISIS',
                    'dimension': 'financial_readiness',
                    'severity': LEVEL_HARD_STOP,
                    'reason': 'High debt, no stable income, and dependants detected. '
                              'This combination represents a financial crisis that requires '
                              'immediate professional support.',
                    'what_is_blocked': ['all_platform_activities'],
                    'what_is_allowed': ['financial_counseling_resources', 'support_links'],
                    'unlock_condition':
                        'Stabilise your financial situation with professional support. '
                        'The platform will be here when you are ready.',
                }],
            )

        # --- Level 4: Hard Block ---
        if runway_months < 1 or (high_debt and no_income):
            reason = (
                'Less than 1 month of financial runway detected.'
                if runway_months < 1
                else 'High debt combined with no stable income.'
            )
            blockers.append({
                'type': 'FINANCIAL_HARD_BLOCK',
                'dimension': 'financial_readiness',
                'severity': LEVEL_HARD_BLOCK,
                'reason': reason,
                'what_is_blocked': _PAID_ACTIONS,
                'what_is_allowed': _FREE_ACTIONS,
                'unlock_condition':
                    'Establish at least 3 months of financial runway (savings, employment, '
                    'or confirmed pre-revenue investment with documentation).',
            })
            return DimensionResult(score=15, level=LEVEL_HARD_BLOCK, blockers=blockers)

        # --- Debt elevation (bumps level up) ---
        debt_elevation = 0
        if debt_pressure_level >= 4 and not income_stable:
            debt_elevation = 1  # Elevate by one level
        elif debt_pressure_level >= 3 and runway_months < 3:
            debt_elevation = 1

        # --- Level 3: Soft Block ---
        if runway_months < 3:
            level = min(LEVEL_SOFT_BLOCK + debt_elevation, LEVEL_HARD_BLOCK)
            score = max(10, int(runway_months / 3 * 40))
            blockers.append({
                'type': 'FINANCIAL_SOFT_BLOCK',
                'dimension': 'financial_readiness',
                'severity': level,
                'reason': f'Financial runway is under 3 months ({runway_months:.1f} months). '
                           'Low-capital route recommended.',
                'what_is_blocked': _PAID_ACTIONS,
                'what_is_allowed': _FREE_ACTIONS,
                'unlock_condition':
                    'Build your runway to 3+ months before spending on the venture.',
            })
            if debt_pressure_level >= 3:
                warnings.append(
                    'Debt pressure combined with short runway. Consider debt-conscious path.'
                )
            return DimensionResult(score=score, level=level, blockers=blockers, warnings=warnings)

        # --- Level 2: Warning ---
        if runway_months < 6:
            score = int(40 + (runway_months - 3) / 3 * 25)
            warnings.append(
                f'Runway of {runway_months:.1f} months is short. '
                'Keep expenses low and track spend carefully.'
            )
            return DimensionResult(
                score=score,
                level=max(LEVEL_WARNING, debt_elevation),
                warnings=warnings,
            )

        # --- Level 1: OK ---
        if runway_months < 12 or not income_stable:
            score = int(65 + (runway_months - 6) / 6 * 15)
            return DimensionResult(score=min(score, 80), level=LEVEL_OK)

        # --- Level 0: Healthy ---
        score = min(100, int(80 + (runway_months - 12) / 12 * 20))
        return DimensionResult(score=score, level=LEVEL_HEALTHY)

    # ------------------------------------------------------------------
    # DIMENSION 2: Time Capacity
    # ------------------------------------------------------------------
    def evaluate_time_capacity(
        self,
        weekly_available_hours: float,
        schedule_flexibility: int = 3,  # 0-5
        paying_customers_exist: bool = False,
    ) -> DimensionResult:
        """
        Special: >= 60h/week AND paying_customers → OPERATIONS_CLEANUP (overload signal).
        """
        blockers = []
        warnings = []
        overload = False
        burnout_risk = False

        # --- Overload signal (Scenario F) ---
        if weekly_available_hours >= 60:
            overload = True
            if paying_customers_exist:
                # Scenario F: Accidental Entrepreneur
                blockers.append({
                    'type': 'OPERATIONS_OVERLOAD',
                    'dimension': 'time_capacity',
                    'severity': LEVEL_HARD_BLOCK,
                    'reason': 'You are working 60+ hours per week with existing customers. '
                               'Expanding further right now risks burnout and operational failure.',
                    'what_is_blocked': [
                        'new_market_expansion', 'fundraising', 'new_product_features',
                        'additional_customer_acquisition',
                    ],
                    'what_is_allowed': [
                        'operations_documentation',
                        'process_design',
                        'delegation_planning',
                        'stabilisation_tasks',
                    ],
                    'unlock_condition':
                        'Complete Operations Cleanup track: document 3 core processes and '
                        'reduce weekly hours to under 50.',
                })
                result = DimensionResult(
                    score=20, level=LEVEL_HARD_BLOCK, blockers=blockers
                )
                result.overload = True
                return result
            else:
                burnout_risk = True
                warnings.append(
                    'Working 60+ hours per week is a burnout risk. '
                    'Sustainable building requires protecting your energy.'
                )
                result = DimensionResult(score=30, level=LEVEL_SOFT_BLOCK, warnings=warnings)
                result.burnout_risk = True
                return result

        # --- Level 4: Hard Block (< 2h/week) ---
        if weekly_available_hours < 2:
            blockers.append({
                'type': 'TIME_HARD_BLOCK',
                'dimension': 'time_capacity',
                'severity': LEVEL_HARD_BLOCK,
                'reason': f'Only {weekly_available_hours:.0f} hours per week available. '
                           'Active building is not feasible at this level.',
                'what_is_blocked': ['all_active_building_tasks'],
                'what_is_allowed': ['passive_reading', 'light_ideation'],
                'unlock_condition':
                    'Free up at least 5 consistent hours per week for venture work.',
            })
            return DimensionResult(score=10, level=LEVEL_HARD_BLOCK, blockers=blockers)

        # --- Level 3: Soft Block (3-5h/week) ---
        if weekly_available_hours < 6:
            score = int(20 + weekly_available_hours * 3)
            if schedule_flexibility >= 4:
                # Micro-sprint track possible
                warnings.append(
                    'Limited hours but high flexibility — micro-sprint track recommended.'
                )
                return DimensionResult(
                    score=score, level=LEVEL_SOFT_BLOCK, warnings=warnings
                )
            blockers.append({
                'type': 'TIME_SOFT_BLOCK',
                'dimension': 'time_capacity',
                'severity': LEVEL_SOFT_BLOCK,
                'reason': f'{weekly_available_hours:.0f} hours/week is very limited. '
                           'Only micro-commitment tasks are recommended.',
                'what_is_blocked': ['complex_multi_step_tasks', 'intensive_research'],
                'what_is_allowed': [
                    'single_question_tasks',
                    'idea_journaling',
                    'short_conversations',
                ],
                'unlock_condition': 'Increase available time to 6+ hours per week.',
            })
            return DimensionResult(score=score, level=LEVEL_SOFT_BLOCK, blockers=blockers)

        # --- Level 2: Warning (6-9h/week) ---
        if weekly_available_hours < 10:
            warnings.append(
                f'{weekly_available_hours:.0f} hours/week — limited but workable. '
                'Milestones will take longer.'
            )
            return DimensionResult(score=50, level=LEVEL_WARNING, warnings=warnings)

        # --- Level 1: OK (10-19h/week) ---
        if weekly_available_hours < 20:
            score = int(60 + (weekly_available_hours - 10) * 2)
            return DimensionResult(score=score, level=LEVEL_OK)

        # --- Level 0: Healthy (20+h/week) ---
        score = min(100, int(80 + (weekly_available_hours - 20) * 0.5))
        return DimensionResult(score=score, level=LEVEL_HEALTHY)

    # ------------------------------------------------------------------
    # DIMENSION 3: Personal Stability
    # ------------------------------------------------------------------
    def evaluate_personal_stability(
        self,
        stress_level: int,                  # 0-5
        burnout_signals: List[str],
        life_chaos_signals: List[str],
        acute_personal_crisis: bool = False,
    ) -> DimensionResult:
        blockers = []
        warnings = []

        burnout_count = len(burnout_signals)
        chaos_count = len(life_chaos_signals)

        # --- Level 5: Hard Stop ---
        if acute_personal_crisis or burnout_count >= 7:
            return DimensionResult(
                score=0,
                level=LEVEL_HARD_STOP,
                blockers=[{
                    'type': 'PERSONAL_CRISIS',
                    'dimension': 'personal_stability',
                    'severity': LEVEL_HARD_STOP,
                    'reason': 'Signs of acute personal crisis or severe burnout detected. '
                               'The platform cannot responsibly guide venture-building right now.',
                    'what_is_blocked': ['all_platform_activities'],
                    'what_is_allowed': ['support_resources', 'mental_health_links'],
                    'unlock_condition':
                        'Seek support from a mental health professional or crisis service. '
                        'Return when you feel stable — this platform will be here.',
                }],
            )

        # --- Level 4: Hard Block ---
        if stress_level >= 5 or (burnout_count >= 5 and stress_level >= 4) or chaos_count >= 2:
            reason_parts = []
            if stress_level >= 5:
                reason_parts.append('maximum stress level reported')
            if burnout_count >= 5:
                reason_parts.append(f'{burnout_count} burnout signals detected')
            if chaos_count >= 2:
                reason_parts.append(f'{chaos_count} major life disruptions reported')
            blockers.append({
                'type': 'STABILITY_HARD_BLOCK',
                'dimension': 'personal_stability',
                'severity': LEVEL_HARD_BLOCK,
                'reason': 'High personal instability: ' + ', '.join(reason_parts) + '.',
                'what_is_blocked': [
                    'high_pressure_tasks',
                    'investor_pitching',
                    'hiring_processes',
                    'major_financial_commitments',
                ],
                'what_is_allowed': _FREE_ACTIONS[:3],
                'unlock_condition':
                    'Complete at least 3 small platform tasks over 2+ weeks to demonstrate '
                    'consistent capacity. Consider speaking to a counsellor.',
            })
            score = max(5, 25 - burnout_count * 3)
            return DimensionResult(score=score, level=LEVEL_HARD_BLOCK, blockers=blockers)

        # --- Level 3: Soft Block ---
        if stress_level >= 4 and burnout_count >= 3:
            warnings.append(
                'High stress combined with multiple burnout signals. '
                'High-pressure activities should be avoided.'
            )
            blockers.append({
                'type': 'STABILITY_SOFT_BLOCK',
                'dimension': 'personal_stability',
                'severity': LEVEL_SOFT_BLOCK,
                'reason': 'Elevated stress and burnout risk detected.',
                'what_is_blocked': ['fundraising', 'high_pressure_deadlines', 'pitching'],
                'what_is_allowed': _FREE_ACTIONS,
                'unlock_condition': 'Reduce stress signals and maintain consistency for 2 weeks.',
            })
            return DimensionResult(score=35, level=LEVEL_SOFT_BLOCK, blockers=blockers, warnings=warnings)

        # --- Level 2: Warning ---
        if stress_level >= 4 or burnout_count >= 3 or chaos_count >= 1:
            warnings.append(
                'Elevated stress detected. Monitor your capacity and pace yourself.'
            )
            score = max(40, 65 - stress_level * 5 - burnout_count * 3)
            return DimensionResult(score=score, level=LEVEL_WARNING, warnings=warnings)

        # --- Level 1: OK ---
        if stress_level >= 3 or burnout_count >= 1:
            warnings.append('Moderate stress noted — proceed with self-care.')
            score = max(60, 80 - stress_level * 5)
            return DimensionResult(score=score, level=LEVEL_OK, warnings=warnings)

        # --- Level 0: Healthy ---
        score = min(100, 90 + (3 - stress_level) * 3)
        return DimensionResult(score=score, level=LEVEL_HEALTHY)

    # ------------------------------------------------------------------
    # DIMENSION 4: Motivation Quality
    # ------------------------------------------------------------------
    def evaluate_motivation_quality(
        self,
        motivation_type: str,   # ESCAPIST|FINANCIAL_ONLY|MISSION|PASSION|IMPACT|MIXED
        mission_clarity: int,   # 0-5
        urgency_type: str = 'NORMAL',  # PANIC|HIGH|NORMAL|STRATEGIC
    ) -> DimensionResult:
        """
        Motivation quality is a WARNING dimension, never a standalone blocker.
        """
        warnings = []
        level = LEVEL_HEALTHY

        if motivation_type in ('ESCAPIST', 'FINANCIAL_ONLY'):
            level = LEVEL_WARNING
            warnings.append(
                'Primary motivation appears to be escape or purely financial. '
                'Ventures driven only by these motives tend to struggle under pressure. '
                'Reflect on what sustainable meaning this venture would provide.'
            )

        if urgency_type == 'PANIC':
            level = max(level, LEVEL_WARNING)
            warnings.append(
                'Panic-driven urgency detected (e.g., just lost job, financial pressure). '
                'Rushed ventures launched under panic tend to overlook critical risks.'
            )

        if mission_clarity < 2:
            level = max(level, LEVEL_WARNING)
            warnings.append(
                'Mission is not yet clear. Clarifying the "why" behind this venture '
                'will improve decision-making through tough moments.'
            )

        base_score = 50 + mission_clarity * 8
        if motivation_type == 'MISSION':
            base_score += 15
        elif motivation_type == 'IMPACT':
            base_score += 20
        elif motivation_type == 'PASSION':
            base_score += 10
        elif motivation_type in ('ESCAPIST', 'FINANCIAL_ONLY'):
            base_score -= 20

        return DimensionResult(score=max(10, min(100, base_score)), level=level, warnings=warnings)

    # ------------------------------------------------------------------
    # DIMENSION 5: Skills & Experience
    # ------------------------------------------------------------------
    def evaluate_skills_experience(
        self,
        domain_skill_level: int,        # 0-5
        relevant_experience_years: int,
        execution_history: bool,        # Has completed a project before
        has_technical_cofounder: bool = False,
        using_nocode_tools: bool = False,
    ) -> DimensionResult:
        warnings = []
        blockers = []

        # Compute base score
        base_score = (
            domain_skill_level * 10
            + min(relevant_experience_years, 10) * 3
            + (20 if execution_history else 0)
        )

        # Low skill + no mitigation = Soft Block for specific actions
        if domain_skill_level <= 1 and not has_technical_cofounder and not using_nocode_tools:
            blockers.append({
                'type': 'SKILLS_SOFT_BLOCK',
                'dimension': 'skills_experience',
                'severity': LEVEL_SOFT_BLOCK,
                'reason': 'Low domain skill with no identified skill-gap mitigation.',
                'what_is_blocked': ['technical_product_build', 'solo_execution_tasks'],
                'what_is_allowed': ['idea_clarification', 'customer_research', 'co_founder_search'],
                'unlock_condition':
                    'Identify a technical co-founder, find a mentor, or commit to using '
                    'no-code tools to bridge the skill gap.',
            })
            return DimensionResult(
                score=max(15, base_score),
                level=LEVEL_SOFT_BLOCK,
                blockers=blockers,
            )

        if domain_skill_level <= 2:
            warnings.append(
                'Skill level is moderate. Consider a mentor or technical partner '
                'for areas outside your expertise.'
            )
            level = LEVEL_WARNING
        elif domain_skill_level >= 4 and relevant_experience_years >= 5:
            level = LEVEL_HEALTHY
        else:
            level = LEVEL_OK

        return DimensionResult(
            score=max(20, min(100, base_score)),
            level=level,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # DIMENSION 6: Idea Clarity
    # ------------------------------------------------------------------
    def evaluate_idea_clarity(
        self,
        problem_defined: bool,
        target_user_specific: bool,
        value_prop_clear: bool,
        idea_is_just_features: bool = False,
        user_customer_payer_same: bool = True,
    ) -> DimensionResult:
        """
        "Everyone is my customer" → Level 4 Block (blocks market research).
        """
        blockers = []
        warnings = []

        # --- Level 4: Hard Block ---
        if not target_user_specific:
            blockers.append({
                'type': 'IDEA_CLARITY_HARD_BLOCK',
                'dimension': 'idea_clarity',
                'severity': LEVEL_HARD_BLOCK,
                'reason': 'Target user is too broad ("everyone" or undefined). '
                           'Without a specific target, market research cannot be done reliably.',
                'what_is_blocked': ['market_research', 'business_plan_generation', 'investor_pitch'],
                'what_is_allowed': ['idea_clarification', 'target_user_narrowing_exercises'],
                'unlock_condition':
                    'Define a specific target user: who they are, what problem they have, '
                    'and why this problem matters to them specifically.',
            })
            score = 10 if not problem_defined else 25
            return DimensionResult(score=score, level=LEVEL_HARD_BLOCK, blockers=blockers)

        if not problem_defined:
            blockers.append({
                'type': 'IDEA_CLARITY_HARD_BLOCK',
                'dimension': 'idea_clarity',
                'severity': LEVEL_HARD_BLOCK,
                'reason': 'Problem to be solved is not yet defined.',
                'what_is_blocked': ['market_research', 'business_plan_generation'],
                'what_is_allowed': ['problem_discovery_exercises', 'idea_journaling'],
                'unlock_condition': 'Articulate a specific problem that a specific person experiences.',
            })
            return DimensionResult(score=10, level=LEVEL_HARD_BLOCK, blockers=blockers)

        # --- Level 3: Soft Block ---
        if idea_is_just_features or not value_prop_clear:
            level = LEVEL_SOFT_BLOCK
            if idea_is_just_features:
                warnings.append(
                    'The idea is described as a set of features, not a solution to a problem. '
                    'Reframe around the problem first.'
                )
            if not value_prop_clear:
                warnings.append('Value proposition (why this, why you) is not yet clear.')
            score = 40 if value_prop_clear else 30
            return DimensionResult(score=score, level=level, warnings=warnings)

        if not user_customer_payer_same:
            warnings.append(
                'The user, customer, and payer may be different people. '
                'Clarify who pays and who benefits — this affects your business model significantly.'
            )
            return DimensionResult(score=55, level=LEVEL_WARNING, warnings=warnings)

        # --- Level 0-1: Clear idea ---
        score = 70 + (10 if problem_defined else 0) + (10 if value_prop_clear else 0)
        return DimensionResult(score=min(100, score), level=LEVEL_OK)

    # ------------------------------------------------------------------
    # DIMENSION 7: Founder-Idea Fit
    # ------------------------------------------------------------------
    def evaluate_founder_idea_fit(
        self,
        risk_tolerance: int,     # 0-5 (0=very low, 5=very high)
        venture_risk_level: int, # 0-5 (how risky is the venture type)
        lifestyle_fit: int,      # 0-5
        values_alignment: int,   # 0-5
    ) -> DimensionResult:
        warnings = []
        blockers = []

        risk_mismatch = abs(risk_tolerance - venture_risk_level)
        base_score = (
            (5 - risk_mismatch) * 8
            + lifestyle_fit * 8
            + values_alignment * 8
        )

        if risk_mismatch >= 3:
            blockers.append({
                'type': 'FOUNDER_IDEA_MISMATCH',
                'dimension': 'founder_idea_fit',
                'severity': LEVEL_SOFT_BLOCK,
                'reason': f'Large risk mismatch: your tolerance is {risk_tolerance}/5 '
                           f'but venture requires {venture_risk_level}/5 risk.',
                'what_is_blocked': ['high_commitment_pivots', 'major_resource_allocation'],
                'what_is_allowed': ['idea_adaptation_exploration', 'co_founder_search'],
                'unlock_condition':
                    'Consider adapting the venture to match your risk tolerance, '
                    'or finding a co-founder with complementary risk appetite.',
            })
            return DimensionResult(
                score=max(20, base_score),
                level=LEVEL_SOFT_BLOCK,
                blockers=blockers,
            )

        if risk_mismatch >= 2 or lifestyle_fit <= 1:
            warnings.append('Moderate mismatch between founder profile and venture type.')
            return DimensionResult(score=max(40, base_score), level=LEVEL_WARNING, warnings=warnings)

        return DimensionResult(score=max(50, min(100, base_score)), level=LEVEL_OK)

    # ------------------------------------------------------------------
    # DIMENSION 8: Legal / Employment Restrictions
    # ------------------------------------------------------------------
    def evaluate_legal_employment(
        self,
        has_non_compete: bool = False,
        non_compete_in_same_area: bool = False,
        employer_ip_risk: bool = False,
        immigration_restriction: bool = False,
        illegal_venture: bool = False,
    ) -> DimensionResult:
        """
        Legal/Ethical is HIGHEST PRIORITY (Priority 1 in routing order).
        """
        blockers = []

        # Non-negotiable stops
        if illegal_venture:
            return DimensionResult(
                score=0,
                level=LEVEL_HARD_STOP,
                blockers=[{
                    'type': 'ILLEGAL_VENTURE_STOP',
                    'dimension': 'legal_employment',
                    'severity': LEVEL_HARD_STOP,
                    'reason': 'The venture as described involves illegal or unethical activity.',
                    'what_is_blocked': ['all_platform_activities'],
                    'what_is_allowed': [],
                    'unlock_condition':
                        'This block cannot be unlocked. Consider a fundamentally different venture.',
                }],
            )

        if immigration_restriction:
            return DimensionResult(
                score=0,
                level=LEVEL_HARD_STOP,
                blockers=[{
                    'type': 'IMMIGRATION_LEGAL_STOP',
                    'dimension': 'legal_employment',
                    'severity': LEVEL_HARD_STOP,
                    'reason': 'Immigration or visa restrictions prevent self-employment.',
                    'what_is_blocked': ['all_active_activities'],
                    'what_is_allowed': ['planning', 'legal_research'],
                    'unlock_condition':
                        'Consult an immigration lawyer to explore legal paths to entrepreneurship.',
                }],
            )

        if employer_ip_risk:
            blockers.append({
                'type': 'EMPLOYER_IP_HARD_BLOCK',
                'dimension': 'legal_employment',
                'severity': LEVEL_HARD_BLOCK,
                'reason': 'Risk of employer IP claim detected '
                           '(building on employer time, using employer tools or data).',
                'what_is_blocked': ['product_development', 'technical_build', 'ip_creation'],
                'what_is_allowed': ['planning', 'market_research', 'customer_conversations'],
                'unlock_condition':
                    'Get written confirmation from your employer or consult an employment '
                    'lawyer to clarify IP ownership.',
            })
            return DimensionResult(score=20, level=LEVEL_HARD_BLOCK, blockers=blockers)

        if has_non_compete and non_compete_in_same_area:
            blockers.append({
                'type': 'NON_COMPETE_SOFT_BLOCK',
                'dimension': 'legal_employment',
                'severity': LEVEL_SOFT_BLOCK,
                'reason': 'Non-compete agreement may restrict building in this area.',
                'what_is_blocked': ['direct_competitor_build'],
                'what_is_allowed': ['adjacent_market_exploration', 'different_venture_type'],
                'unlock_condition':
                    'Consult an employment lawyer to understand the exact scope of your non-compete.',
            })
            return DimensionResult(score=40, level=LEVEL_SOFT_BLOCK, blockers=blockers)

        if has_non_compete:
            return DimensionResult(
                score=70,
                level=LEVEL_WARNING,
                warnings=['Non-compete exists — scope unclear. Verify before building in your industry.'],
            )

        return DimensionResult(score=95, level=LEVEL_HEALTHY)

    # ------------------------------------------------------------------
    # DIMENSION 9: Health & Energy
    # ------------------------------------------------------------------
    def evaluate_health_energy(
        self,
        energy_level: int,              # 0-5
        affects_work_capacity: bool = False,
        active_intensive_treatment: bool = False,
    ) -> DimensionResult:
        warnings = []
        blockers = []

        if active_intensive_treatment and energy_level <= 1:
            blockers.append({
                'type': 'HEALTH_HARD_BLOCK',
                'dimension': 'health_energy',
                'severity': LEVEL_HARD_BLOCK,
                'reason': 'Active intensive treatment combined with very low energy.',
                'what_is_blocked': ['intensive_tasks', 'high_output_phases'],
                'what_is_allowed': ['light_ideation', 'passive_research'],
                'unlock_condition': 'Resume when energy stabilises above 3/5.',
            })
            return DimensionResult(score=10, level=LEVEL_HARD_BLOCK, blockers=blockers)

        if energy_level <= 2 and affects_work_capacity:
            warnings.append(
                'Low energy that affects work capacity detected. '
                'Micro-commitment track recommended.'
            )
            return DimensionResult(score=25, level=LEVEL_SOFT_BLOCK, warnings=warnings)

        if energy_level <= 2:
            warnings.append('Low energy reported — pace yourself and protect recovery time.')
            return DimensionResult(score=40, level=LEVEL_WARNING, warnings=warnings)

        if energy_level <= 3:
            return DimensionResult(score=60, level=LEVEL_OK)

        return DimensionResult(score=80 + energy_level * 4, level=LEVEL_HEALTHY)

    # ------------------------------------------------------------------
    # COMPOSITE: Worst-case wins, NEVER average
    # ------------------------------------------------------------------
    def compute_overall_readiness(self, dim_results: dict) -> tuple:
        """
        Returns: (overall_level, recommended_route)

        KEY INVARIANT: overall_level = MAX of all individual levels.
        Level 5 propagates immediately. Level 4 blocks everything below.
        """
        # Collect levels
        all_levels = {name: r.level for name, r in dim_results.items()}

        # Hard Stop propagates immediately
        if any(v == LEVEL_HARD_STOP for v in all_levels.values()):
            return LEVEL_HARD_STOP, ROUTE_HARD_STOP

        # Determine overall level
        overall = max(all_levels.values(), default=LEVEL_HEALTHY)

        # Determine route based on which dimensions are blocking
        fin = dim_results.get('financial', DimensionResult(score=100, level=0))
        time = dim_results.get('time_capacity', DimensionResult(score=100, level=0))
        legal = dim_results.get('legal_employment', DimensionResult(score=100, level=0))
        stability = dim_results.get('personal_stability', DimensionResult(score=100, level=0))

        # Detect overload signal (Scenario F)
        if getattr(time, 'overload', False):
            return LEVEL_HARD_BLOCK, ROUTE_OPERATIONS_CLEANUP

        # Legal/ethical always first (CEO Priority 1)
        if legal.level >= LEVEL_SOFT_BLOCK:
            return overall, ROUTE_STABILIZE

        if overall == LEVEL_HARD_BLOCK:
            if fin.level >= LEVEL_HARD_BLOCK:
                return overall, ROUTE_STABILIZE
            if stability.level >= LEVEL_HARD_BLOCK:
                return overall, ROUTE_STABILIZE
            return overall, ROUTE_STABILIZE

        if overall == LEVEL_SOFT_BLOCK:
            if fin.level >= LEVEL_SOFT_BLOCK:
                return overall, ROUTE_LOW_CAPITAL
            if time.level >= LEVEL_SOFT_BLOCK:
                return overall, ROUTE_LOW_CAPITAL
            return overall, ROUTE_LOW_CAPITAL

        if overall == LEVEL_WARNING:
            return overall, ROUTE_CONTINUE

        return overall, ROUTE_CONTINUE

    # ------------------------------------------------------------------
    # COMPENSATION RULES (Level 2-3 only)
    # ------------------------------------------------------------------
    def get_compensation_rules(self, results: dict, raw_responses: dict) -> list:
        """
        Identify compensations that CAN reduce level 2-3 risks.
        HARD RULE: Level 4-5 are NEVER compensable.

        Returns list of applied compensation objects.
        """
        applied = []
        financial = results.get('financial')
        skills = results.get('skills_experience')

        # Low financial runway + income stable = slight mitigation
        if financial and financial.level == LEVEL_SOFT_BLOCK:
            if raw_responses.get('income_stable') and raw_responses.get('employed_part_time'):
                applied.append({
                    'risk_compensated': 'short_runway',
                    'compensator': 'stable_part_time_income',
                    'evidence_required': False,
                    'note': 'Part-time income partially compensates short runway. '
                            'Low-capital track still required.',
                    'level_reduced_by': 0,  # Does not reduce level, only reduces severity of warning
                })

        # Low skills + technical co-founder
        if skills and skills.level == LEVEL_SOFT_BLOCK:
            if raw_responses.get('has_technical_cofounder'):
                applied.append({
                    'risk_compensated': 'low_technical_skill',
                    'compensator': 'technical_cofounder',
                    'evidence_required': True,
                    'note': 'Technical co-founder compensates skill gap. '
                            'Evidence of co-founder commitment is required to fully clear block.',
                    'level_reduced_by': 1,
                })

        return applied

    # ------------------------------------------------------------------
    # SCENARIO DETECTION (CEO Section 4.5)
    # ------------------------------------------------------------------
    def detect_scenario(self, raw: dict, results: dict) -> Optional[str]:
        """
        Detect which of CEO's 6 prototype scenarios best matches the user.
        Returns scenario tag or None.
        """
        fin = results.get('financial')
        time = results.get('time_capacity')
        skills = results.get('skills_experience')

        # Scenario A: Overexcited Beginner
        # Zero runway + quit job + high passion/urgency
        if (fin and fin.level >= LEVEL_HARD_BLOCK and
                raw.get('just_quit_job') and
                raw.get('motivation_type') in ('PASSION', 'ESCAPIST', 'FINANCIAL_ONLY')):
            return 'OVEREXCITED_BEGINNER'

        # Scenario F: Accidental Entrepreneur (overload + paying customers)
        if (time and getattr(time, 'overload', False) and
                raw.get('paying_customers_exist')):
            return 'ACCIDENTAL_ENTREPRENEUR'

        # Scenario D: Deep-Tech
        if (skills and skills.score >= 70 and
                raw.get('venture_type') == 'DEEP_TECH' and
                not raw.get('has_commercial_experience')):
            return 'DEEP_TECH_INNOVATOR'

        # Scenario H: Impact Visionary
        if (raw.get('motivation_type') == 'IMPACT' and
                raw.get('venture_type') in ('SOCIAL', 'NON_PROFIT') and
                raw.get('funding_model_clear') is False):
            return 'IMPACT_VISIONARY'

        # Scenario C: Failed Founder
        if raw.get('had_previous_failed_venture') and raw.get('has_debt'):
            return 'FAILED_FOUNDER_RESTART'

        # Scenario B: Experienced Professional
        if (skills and skills.score >= 65 and
                skills.level <= LEVEL_WARNING and
                raw.get('corporate_background') and
                not raw.get('has_validated_with_real_customers')):
            return 'EXPERIENCED_PROFESSIONAL'

        return None

    # ------------------------------------------------------------------
    # FOUNDER TYPE CLASSIFICATION (CEO Section 2.2 — 16 types A-P)
    # ------------------------------------------------------------------
    def classify_founder_type(self, raw: dict, overall_level: int) -> Optional[str]:
        """
        Classify user into one of 16 founder types (A-P).
        Returns single letter or None.
        """
        venture_type = raw.get('venture_type', '')
        motivation = raw.get('motivation_type', '')
        experience = raw.get('relevant_experience_years', 0)
        failed_before = raw.get('had_previous_failed_venture', False)
        has_customers = raw.get('paying_customers_exist', False)
        corporate = raw.get('corporate_background', False)
        no_idea_yet = raw.get('no_idea_yet', False)

        if no_idea_yet:
            return 'P'  # No-Idea Explorer

        if venture_type == 'DEEP_TECH':
            return 'G'  # Deep-Tech / Research Founder

        if motivation == 'IMPACT' or venture_type in ('SOCIAL', 'NON_PROFIT'):
            return 'H'  # Impact-Driven / Social Founder

        if failed_before:
            return 'F'  # Failed or Struggling Founder

        if has_customers and overall_level >= LEVEL_SOFT_BLOCK:
            return 'J'  # Overloaded / Operational Founder

        if has_customers:
            return 'C'  # Side-Hustler With Traction

        if corporate and experience >= 5:
            return 'E'  # Experienced Industry Professional

        if corporate and experience >= 2:
            return 'B'  # Career Switcher / Professional Founder

        if venture_type == 'LOCAL':
            return 'K'  # Local / Community Business Founder

        if venture_type in ('SAAS', 'DIGITAL'):
            return 'L'  # Digital Product / SaaS Founder

        if experience == 0:
            return 'A'  # Aspiring First-Time Founder

        return 'A'

    # ------------------------------------------------------------------
    # MASTER EVALUATION
    # ------------------------------------------------------------------
    def evaluate_all(self, responses: dict) -> Phase1Result:
        """
        Run all dimensions. Return typed Phase1Result.

        Expected keys in `responses` (all optional, defaults to safe values):
          financial_runway_months, income_stable, debt_pressure_level,
          has_dependants, high_debt, weekly_available_hours, schedule_flexibility,
          paying_customers_exist, stress_level, burnout_signals, life_chaos_signals,
          acute_personal_crisis, motivation_type, mission_clarity, urgency_type,
          domain_skill_level, relevant_experience_years, execution_history,
          has_technical_cofounder, using_nocode_tools, problem_defined,
          target_user_specific, value_prop_clear, idea_is_just_features,
          user_customer_payer_same, risk_tolerance, venture_risk_level,
          lifestyle_fit, values_alignment, has_non_compete,
          non_compete_in_same_area, employer_ip_risk, immigration_restriction,
          illegal_venture, energy_level, affects_work_capacity,
          active_intensive_treatment
        """
        r = responses  # shorthand

        # --- Run each dimension ---
        fin = self.evaluate_financial_readiness(
            runway_months=float(r.get('financial_runway_months', 6)),
            income_stable=bool(r.get('income_stable', True)),
            debt_pressure_level=int(r.get('debt_pressure_level', 0)),
            has_dependants=bool(r.get('has_dependants', False)),
            high_debt=bool(r.get('high_debt', False)),
        )

        time = self.evaluate_time_capacity(
            weekly_available_hours=float(r.get('weekly_available_hours', 10)),
            schedule_flexibility=int(r.get('schedule_flexibility', 3)),
            paying_customers_exist=bool(r.get('paying_customers_exist', False)),
        )

        stability = self.evaluate_personal_stability(
            stress_level=int(r.get('stress_level', 2)),
            burnout_signals=list(r.get('burnout_signals', [])),
            life_chaos_signals=list(r.get('life_chaos_signals', [])),
            acute_personal_crisis=bool(r.get('acute_personal_crisis', False)),
        )

        motivation = self.evaluate_motivation_quality(
            motivation_type=str(r.get('motivation_type', 'MIXED')),
            mission_clarity=int(r.get('mission_clarity', 2)),
            urgency_type=str(r.get('urgency_type', 'NORMAL')),
        )

        skills = self.evaluate_skills_experience(
            domain_skill_level=int(r.get('domain_skill_level', 3)),
            relevant_experience_years=int(r.get('relevant_experience_years', 0)),
            execution_history=bool(r.get('execution_history', False)),
            has_technical_cofounder=bool(r.get('has_technical_cofounder', False)),
            using_nocode_tools=bool(r.get('using_nocode_tools', False)),
        )

        idea = self.evaluate_idea_clarity(
            problem_defined=bool(r.get('problem_defined', True)),
            target_user_specific=bool(r.get('target_user_specific', True)),
            value_prop_clear=bool(r.get('value_prop_clear', False)),
            idea_is_just_features=bool(r.get('idea_is_just_features', False)),
            user_customer_payer_same=bool(r.get('user_customer_payer_same', True)),
        )

        fit = self.evaluate_founder_idea_fit(
            risk_tolerance=int(r.get('risk_tolerance', 2)),
            venture_risk_level=int(r.get('venture_risk_level', 2)),
            lifestyle_fit=int(r.get('lifestyle_fit', 3)),
            values_alignment=int(r.get('values_alignment', 3)),
        )

        legal = self.evaluate_legal_employment(
            has_non_compete=bool(r.get('has_non_compete', False)),
            non_compete_in_same_area=bool(r.get('non_compete_in_same_area', False)),
            employer_ip_risk=bool(r.get('employer_ip_risk', False)),
            immigration_restriction=bool(r.get('immigration_restriction', False)),
            illegal_venture=bool(r.get('illegal_venture', False)),
        )

        health = self.evaluate_health_energy(
            energy_level=int(r.get('energy_level', 4)),
            affects_work_capacity=bool(r.get('affects_work_capacity', False)),
            active_intensive_treatment=bool(r.get('active_intensive_treatment', False)),
        )

        # Placeholder dims (not fully assessable in Phase 1)
        founder_market_fit = DimensionResult(score=50, level=LEVEL_OK)
        market_validity = DimensionResult(score=50, level=LEVEL_OK)
        business_model = DimensionResult(score=50, level=LEVEL_OK)
        network = DimensionResult(score=50, level=LEVEL_OK)

        all_dims = {
            'financial': fin,
            'time_capacity': time,
            'personal_stability': stability,
            'motivation_quality': motivation,
            'skills_experience': skills,
            'idea_clarity': idea,
            'founder_idea_fit': fit,
            'legal_employment': legal,
            'health_energy': health,
        }

        overall_level, recommended_route = self.compute_overall_readiness(all_dims)

        # Collect all active blockers
        active_blockers = []
        for dim_result in all_dims.values():
            active_blockers.extend(dim_result.blockers)

        # Build allowed / blocked action lists from blockers
        blocked_action_set = {}
        for bl in active_blockers:
            for action in bl.get('what_is_blocked', []):
                blocked_action_set[action] = {
                    'action': action,
                    'reason': bl['reason'],
                    'unlock_condition': bl.get('unlock_condition', ''),
                }
        allowed_actions = list({
            a
            for bl in active_blockers
            for a in bl.get('what_is_allowed', [])
        })
        if not active_blockers:
            allowed_actions = ['all_actions']

        compensation_rules = self.get_compensation_rules(all_dims, r)

        # Detect scenario and founder type
        scenario = self.detect_scenario(r, all_dims)
        founder_type = self.classify_founder_type(r, overall_level)

        # Route override for specific scenarios
        if scenario == 'ACCIDENTAL_ENTREPRENEUR':
            recommended_route = ROUTE_OPERATIONS_CLEANUP
        elif scenario == 'DEEP_TECH_INNOVATOR':
            recommended_route = ROUTE_DEEP_TECH
        elif scenario == 'IMPACT_VISIONARY':
            recommended_route = ROUTE_IMPACT_SOCIAL
        elif scenario == 'FAILED_FOUNDER_RESTART':
            recommended_route = ROUTE_DEBT_CONSCIOUS
        elif scenario == 'EXPERIENCED_PROFESSIONAL':
            recommended_route = ROUTE_CORPORATE_TRANSITION if overall_level <= LEVEL_WARNING else recommended_route

        return Phase1Result(
            financial=fin,
            time_capacity=time,
            personal_stability=stability,
            motivation_quality=motivation,
            skills_experience=skills,
            idea_clarity=idea,
            founder_idea_fit=fit,
            legal_employment=legal,
            health_energy=health,
            founder_market_fit=founder_market_fit,
            market_validity=market_validity,
            business_model=business_model,
            network_mentorship=network,
            overall_level=overall_level,
            recommended_route=recommended_route,
            active_blockers=active_blockers,
            allowed_actions=allowed_actions,
            blocked_actions=list(blocked_action_set.values()),
            compensation_rules=compensation_rules,
            burnout_signal=getattr(stability, 'burnout_risk', False),
            overload_signal=getattr(time, 'overload', False),
            detected_scenario=scenario,
            founder_type=founder_type,
        )
