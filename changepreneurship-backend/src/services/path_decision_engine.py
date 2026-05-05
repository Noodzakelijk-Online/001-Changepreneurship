"""
PathDecisionEngine — Sprint 2 (S2-01)
=======================================
Layer 1 — Central non-linear routing engine.

CEO Section 3.4:
  "The platform should NOT always route users to the next question.
   The next step should be determined by the user's actual situation,
   risk level, evidence level, and readiness."

Priority order (CEO Section 3.4) — ENFORCED, never violated:
  1. Safety and legality
  2. Personal and financial stability
  3. Contradictions and data quality
  4. Idea clarity
  5. Market evidence
  6. Business model coherence
  7. Operational capacity
  8. Acceleration opportunities
  9. Next normal question (DEFAULT)

Reroute message template (CEO Section 3.4):
  "I am not sending you to [next normal step] yet.
   Based on [detected signal], the more responsible next step is [action].
   This matters because [reason].
   For now, [blocked action] is paused, but [allowed action] can continue.
   To unlock the next stage, complete [specific task/condition]."
"""
from dataclasses import dataclass, field
from typing import List, Optional
import logging

from src.services.contradiction_detector import (
    ContradictionDetector,
    CONTRADICTION_LEVEL_SOFT, CONTRADICTION_LEVEL_HARD,
)
from src.services.phase1_rule_engine import (
    LEVEL_HEALTHY, LEVEL_OK, LEVEL_WARNING,
    LEVEL_SOFT_BLOCK, LEVEL_HARD_BLOCK, LEVEL_HARD_STOP,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routing categories (CEO Section 3.4 — 21 categories)
# ---------------------------------------------------------------------------
ROUTE_CONTINUE = 'CONTINUE'
ROUTE_CLARIFY = 'CLARIFY'
ROUTE_DEEPEN = 'DEEPEN'
ROUTE_VALIDATE = 'VALIDATE'
ROUTE_PAUSE = 'PAUSE'
ROUTE_STABILIZE = 'STABILIZE'
ROUTE_REFER = 'REFER'
ROUTE_FIND_MENTOR = 'FIND_MENTOR'
ROUTE_PIVOT = 'PIVOT'
ROUTE_STOP = 'STOP'
ROUTE_ACCELERATE = 'ACCELERATE'
ROUTE_REASSESS = 'REASSESS'
ROUTE_FINANCIAL_STABILIZATION = 'FINANCIAL_STABILIZATION'
ROUTE_RUNWAY_PLAN = 'RUNWAY_PLAN'
ROUTE_CUSTOMER_DISCOVERY = 'CUSTOMER_DISCOVERY'
ROUTE_REAL_WORLD_TASK = 'REAL_WORLD_TASK'
ROUTE_STUDY = 'STUDY'
ROUTE_FOUNDER_IDEA_MISMATCH = 'FOUNDER_IDEA_MISMATCH'
ROUTE_BURNOUT_PREVENTION = 'BURNOUT_PREVENTION'
ROUTE_FAST_TRACK = 'FAST_TRACK'
ROUTE_OPERATIONS_CLEANUP = 'OPERATIONS_CLEANUP'
ROUTE_IMPACT_NON_PROFIT = 'IMPACT_NON_PROFIT'
ROUTE_DEEP_TECH = 'DEEP_TECH'
ROUTE_HARD_ETHICAL_STOP = 'HARD_ETHICAL_STOP'
ROUTE_RECOMMEND_PIVOT = 'RECOMMEND_PIVOT'
ROUTE_RECALCULATE = 'RECALCULATE'

# Overperformance signal types
OVERPERFORMANCE_GENUINE = 'GENUINE_READINESS'
OVERPERFORMANCE_POLISHED = 'POLISHED_UNREALITY'
OVERPERFORMANCE_BURNOUT = 'BURNOUT_PERFORMANCE'
OVERPERFORMANCE_AI_INFLATE = 'AI_INFLATION'

# Priority levels for routing (CEO Section 3.4)
PRIORITY_SAFETY_LEGAL = 1
PRIORITY_STABILITY = 2
PRIORITY_CONTRADICTIONS = 3
PRIORITY_IDEA_CLARITY = 4
PRIORITY_MARKET_EVIDENCE = 5
PRIORITY_BUSINESS_MODEL = 6
PRIORITY_OPERATIONAL_CAPACITY = 7
PRIORITY_ACCELERATION = 8
PRIORITY_DEFAULT = 9


@dataclass
class NextAction:
    type: str
    description: str
    success_criteria: str
    template: Optional[str] = None
    estimated_time: Optional[str] = None


@dataclass
class RerouteMessage:
    detected: str           # What signal was detected
    why: str                # Why this matters
    blocked_action: str     # What is currently paused
    allowed_action: str     # What can continue
    unlock_condition: str   # How to unlock the blocked path


@dataclass
class RoutingDecision:
    category: str                       # One of the 21 route constants
    priority_level: int                 # 1-9 (which CEO priority triggered this)
    allowed_actions: List[str]
    blocked_actions: List[dict]         # [{action, reason, unlock}]
    next_action: NextAction
    is_reroute: bool
    reroute_message: Optional[RerouteMessage]
    overperformance_signal: Optional[str] = None
    verification_tasks: List[str] = field(default_factory=list)
    contradictions_summary: Optional[str] = None


@dataclass
class OverperformanceSignal:
    signal_type: str
    confidence: str         # LOW / MEDIUM / HIGH
    reasoning: str
    verification_tasks: List[str]


class PathDecisionEngine:
    """
    Layer 1 routing engine. Stateless — accepts profile + responses, returns decision.

    Usage:
        engine = PathDecisionEngine()
        decision = engine.evaluate_routing(founder_profile_dict, responses, current_phase)
    """

    def __init__(self):
        self._contradiction_detector = ContradictionDetector()

    # ------------------------------------------------------------------
    # MAIN ENTRYPOINT
    # ------------------------------------------------------------------
    def evaluate_routing(
        self,
        founder_profile: dict,
        responses: dict,
        current_phase: int = 1,
        historical_answers: dict = None,
        session_data: dict = None,
    ) -> RoutingDecision:
        """
        Evaluate routing for the user. Returns a RoutingDecision.

        CEO Priority Order strictly enforced:
          Priority 1 wins over everything.
        """
        overall_level = int(founder_profile.get('overall_readiness_level', 0))
        active_blockers = list(founder_profile.get('active_blockers', []))
        r = responses
        historical = historical_answers or {}

        # -----------------------------------------------------------
        # PRIORITY 1: Safety and Legality
        # -----------------------------------------------------------
        # Merge pre-computed profile level with raw response signals (fallback)
        legal_level = int(founder_profile.get('legal_employment_level', 0))
        if legal_level == LEVEL_HEALTHY:
            # Escalate from raw responses when profile has not been computed yet
            if responses.get('illegal_venture') or responses.get('immigration_restriction'):
                legal_level = LEVEL_HARD_STOP
            elif responses.get('employer_ip_risk') or responses.get('has_non_compete'):
                legal_level = LEVEL_HARD_BLOCK
        if legal_level == LEVEL_HARD_STOP:
            return self._make_decision(
                category=ROUTE_HARD_ETHICAL_STOP,
                priority_level=PRIORITY_SAFETY_LEGAL,
                blocked_actions=active_blockers,
                allowed_actions=[],
                next_action=NextAction(
                    type='LEGAL_RESOLUTION',
                    description=(
                        'This platform cannot assist with the current venture as described. '
                        'Please consult a qualified legal professional.'
                    ),
                    success_criteria='N/A — this block cannot be unlocked through the platform.',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Legal or ethical restriction',
                    why='The platform cannot responsibly guide ventures that are illegal or unethical.',
                    blocked_action='all platform activities',
                    allowed_action='consulting a legal professional',
                    unlock_condition='This block cannot be unlocked. Consider a fundamentally different venture.',
                ),
            )

        if legal_level == LEVEL_HARD_BLOCK:
            return self._make_decision(
                category=ROUTE_REFER,
                priority_level=PRIORITY_SAFETY_LEGAL,
                blocked_actions=active_blockers,
                allowed_actions=['planning', 'market_research', 'legal_research'],
                next_action=NextAction(
                    type='LEGAL_CONSULTATION',
                    description='Consult an employment or IP lawyer before proceeding.',
                    success_criteria='Documented legal clearance or modified venture scope.',
                    estimated_time='1-2 weeks',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Potential legal restriction (IP, employment, or immigration)',
                    why='Proceeding without legal clarity risks the entire venture.',
                    blocked_action='product development and IP creation',
                    allowed_action='planning, research, and legal consultation',
                    unlock_condition='Written legal clearance or venture scope adjusted to avoid the risk.',
                ),
            )

        # -----------------------------------------------------------
        # PRIORITY 2: Personal and Financial Stability
        # -----------------------------------------------------------
        financial_level = int(founder_profile.get('financial_level', 0))
        stability_level = int(founder_profile.get('personal_stability_level', 0))

        # Fallback: derive from raw responses when profile not yet computed
        if financial_level == LEVEL_HEALTHY:
            runway = responses.get('financial_runway_months')
            if runway is not None:
                runway = int(runway)
                if runway == 0:
                    financial_level = LEVEL_HARD_BLOCK
                elif runway < 3:
                    financial_level = LEVEL_SOFT_BLOCK

        if stability_level == LEVEL_HARD_STOP:
            return self._make_decision(
                category=ROUTE_REFER,
                priority_level=PRIORITY_STABILITY,
                blocked_actions=active_blockers,
                allowed_actions=['support_resources'],
                next_action=NextAction(
                    type='PERSONAL_SUPPORT',
                    description=(
                        'Your personal wellbeing comes first. '
                        'Please connect with appropriate support resources.'
                    ),
                    success_criteria='Stable and ready to build.',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Signs of acute personal crisis or severe burnout',
                    why='Building a venture from a place of crisis tends to compound problems.',
                    blocked_action='all venture-building activities',
                    allowed_action='accessing mental health and support resources',
                    unlock_condition='Return when you feel stable — this platform will be here.',
                ),
            )

        if financial_level == LEVEL_HARD_BLOCK:
            return self._make_decision(
                category=ROUTE_FINANCIAL_STABILIZATION,
                priority_level=PRIORITY_STABILITY,
                blocked_actions=active_blockers,
                allowed_actions=[
                    'idea_clarification', 'free_research',
                    'customer_conversations', 'planning',
                ],
                next_action=NextAction(
                    type='RUNWAY_BUILDING',
                    description=(
                        'Build financial runway to at least 3 months before '
                        'committing to this venture.'
                    ),
                    success_criteria='3+ months runway documented.',
                    estimated_time='4-12 weeks depending on your income situation',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Financial runway below safe threshold',
                    why='Ventures built under severe financial pressure have much lower survival rates.',
                    blocked_action='any paid actions (development, tools, marketing, hiring)',
                    allowed_action='free research, planning, customer conversations',
                    unlock_condition='Establish at least 3 months of documented financial runway.',
                ),
            )

        if financial_level == LEVEL_SOFT_BLOCK or stability_level == LEVEL_SOFT_BLOCK:
            return self._make_decision(
                category=ROUTE_STABILIZE,
                priority_level=PRIORITY_STABILITY,
                blocked_actions=[b for b in active_blockers if b.get('severity', 0) >= 3],
                allowed_actions=['free_research', 'customer_conversations', 'planning'],
                next_action=NextAction(
                    type='STABILIZE_THEN_CONTINUE',
                    description=(
                        'Low-capital path is recommended. '
                        'Focus on conversations and learning — no spending.'
                    ),
                    success_criteria='Runway improved to 3+ months OR stability consistent for 2 weeks.',
                    estimated_time='2-4 weeks',
                ),
                is_reroute=True,
                reroute_message=self._build_stability_reroute(financial_level, stability_level),
            )

        # -----------------------------------------------------------
        # PRIORITY 3: Contradictions and Data Quality
        # -----------------------------------------------------------
        contradiction_result = self._contradiction_detector.evaluate(responses)
        if contradiction_result.has_blocking_contradiction:
            blocking = [c for c in contradiction_result.contradictions if c.level >= CONTRADICTION_LEVEL_HARD]
            return self._make_decision(
                category=ROUTE_REASSESS,
                priority_level=PRIORITY_CONTRADICTIONS,
                blocked_actions=[{
                    'action': a,
                    'reason': c.explanation,
                    'unlock': c.recommendation,
                } for c in blocking for a in c.affected_actions],
                allowed_actions=['reflection', 'conversation_with_mentor', 'free_research'],
                next_action=NextAction(
                    type='RESOLVE_CONTRADICTION',
                    description=blocking[0].recommendation if blocking else 'Resolve contradictions before continuing.',
                    success_criteria='Contradictions resolved and answers updated consistently.',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected=f'Contradiction: {blocking[0].type if blocking else "data inconsistency"}',
                    why=blocking[0].explanation if blocking else 'Your answers contain an important inconsistency.',
                    blocked_action=', '.join(blocking[0].affected_actions[:2]) if blocking else 'affected actions',
                    allowed_action='reflection and updating your answers',
                    unlock_condition=blocking[0].recommendation if blocking else 'Resolve contradictions.',
                ),
                contradictions_summary=contradiction_result.summary,
            )

        # -----------------------------------------------------------
        # PRIORITY 4: Idea Clarity
        # -----------------------------------------------------------
        idea_level = int(founder_profile.get('idea_clarity_level', 0))
        if idea_level == LEVEL_HARD_BLOCK:
            return self._make_decision(
                category=ROUTE_CLARIFY,
                priority_level=PRIORITY_IDEA_CLARITY,
                blocked_actions=[b for b in active_blockers if b.get('dimension') == 'idea_clarity'],
                allowed_actions=['idea_journaling', 'problem_discovery', 'customer_conversations'],
                next_action=NextAction(
                    type='IDEA_CLARIFICATION',
                    description=(
                        'Define one specific person with one specific problem before anything else.'
                    ),
                    success_criteria=(
                        'You can describe your target user in one sentence without using '
                        '"everyone" or "anyone".'
                    ),
                    estimated_time='1-3 days of focused conversations',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Idea or target user not yet clearly defined',
                    why='All downstream work (market research, business model, messaging) depends on a clear target.',
                    blocked_action='market research, business plan, investor pitch',
                    allowed_action='problem discovery, customer conversations, idea journaling',
                    unlock_condition='Define a specific target user with a specific problem.',
                ),
            )

        # -----------------------------------------------------------
        # PRIORITY 5: Market Evidence
        # -----------------------------------------------------------
        market_level = int(founder_profile.get('market_validity_level', 0))
        if market_level >= LEVEL_HARD_BLOCK and current_phase >= 2:
            return self._make_decision(
                category=ROUTE_CUSTOMER_DISCOVERY,
                priority_level=PRIORITY_MARKET_EVIDENCE,
                blocked_actions=[{
                    'action': 'business_plan_generation',
                    'reason': 'Business plan without market evidence is speculation.',
                    'unlock': 'Complete 5+ customer discovery conversations.',
                }],
                allowed_actions=['customer_conversations', 'market_research', 'assumption_testing'],
                next_action=NextAction(
                    type='CUSTOMER_DISCOVERY',
                    description='Complete 5 customer discovery conversations before building further.',
                    success_criteria='5 conversations documented with key insights.',
                    estimated_time='1-2 weeks',
                    template='discovery_conversation_guide',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='No direct market evidence',
                    why='Every assumption needs to be tested with real people before you invest more.',
                    blocked_action='business plan, pitch deck, investor outreach',
                    allowed_action='customer discovery conversations, desk research',
                    unlock_condition='5+ documented customer conversations with recorded insights.',
                ),
            )

        # -----------------------------------------------------------
        # PRIORITY 7: Operational Capacity (overload detection)
        # -----------------------------------------------------------
        time_level = int(founder_profile.get('time_capacity_level', 0))
        overload = bool(founder_profile.get('overload_signal', False))

        # Fallback: derive from raw responses when profile not yet computed
        if not overload and time_level == LEVEL_HEALTHY:
            hours = int(responses.get('weekly_available_hours', 0))
            burnout_signals = responses.get('burnout_signals', [])
            has_customers = (
                responses.get('has_paying_customers')
                or responses.get('paying_customers_exist')
            )
            if hours >= 80:
                overload = True
            elif hours >= 60 and burnout_signals and has_customers:
                overload = True

        if overload or time_level == LEVEL_HARD_BLOCK:
            return self._make_decision(
                category=ROUTE_OPERATIONS_CLEANUP,
                priority_level=PRIORITY_OPERATIONAL_CAPACITY,
                blocked_actions=[{
                    'action': 'new_market_expansion',
                    'reason': 'Adding scope while overloaded increases failure risk.',
                    'unlock': 'Document 3 core processes and reduce weekly hours to under 50.',
                }],
                allowed_actions=['process_documentation', 'delegation_planning', 'stabilisation'],
                next_action=NextAction(
                    type='OPERATIONS_CLEANUP',
                    description=(
                        'Document your 3 most critical processes. '
                        'This is the fastest path to sustainable growth.'
                    ),
                    success_criteria='3 processes documented, workload reduced to < 50h/week.',
                    estimated_time='2-4 weeks',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Operational overload (60+ hours/week with existing customers)',
                    why='Adding more scope to an overloaded operation accelerates failure, not growth.',
                    blocked_action='new product features, new market expansion, new hiring',
                    allowed_action='process documentation, delegation planning, systems design',
                    unlock_condition='Weekly hours below 50 AND 3 core processes documented.',
                ),
            )

        # -----------------------------------------------------------
        # PRIORITY 8: Overperformance detection
        # -----------------------------------------------------------
        overperformance = self._detect_overperformance(session_data or {}, founder_profile)
        if overperformance and overperformance.signal_type == OVERPERFORMANCE_BURNOUT:
            return self._make_decision(
                category=ROUTE_BURNOUT_PREVENTION,
                priority_level=PRIORITY_ACCELERATION,
                blocked_actions=[{
                    'action': 'intensive_building',
                    'reason': 'Burnout performance pattern detected — pace is unsustainable.',
                    'unlock': 'Maintain consistent lower pace for 2 weeks.',
                }],
                allowed_actions=['light_tasks', 'planning', 'reflection'],
                next_action=NextAction(
                    type='PACE_REDUCTION',
                    description='Reduce intensity. Sustainable building beats sprint-crash cycles.',
                    success_criteria='Consistent 10-15h/week for 2 weeks.',
                ),
                is_reroute=True,
                reroute_message=RerouteMessage(
                    detected='Burnout performance pattern',
                    why='Very high short-term output followed by crashes is a common founder failure mode.',
                    blocked_action='intensive multi-task sprints',
                    allowed_action='focused single tasks, planning, reflection',
                    unlock_condition='Consistent moderate pace for 2 weeks.',
                ),
                overperformance_signal=overperformance.signal_type,
                verification_tasks=overperformance.verification_tasks,
            )

        # -----------------------------------------------------------
        # PRIORITY 9: Default routing (no blockers)
        # -----------------------------------------------------------
        return self._default_routing(founder_profile, responses, current_phase, overperformance)

    # ------------------------------------------------------------------
    # HELPER: Default routing when all priorities clear
    # ------------------------------------------------------------------
    def _default_routing(
        self, founder_profile: dict, responses: dict, current_phase: int, overperformance=None
    ) -> RoutingDecision:
        overall_level = int(founder_profile.get('overall_readiness_level', 0))

        # Strong profile + current phase done → Accelerate
        if overall_level <= LEVEL_OK and current_phase >= 2 and responses.get('paying_customers_exist'):
            category = ROUTE_ACCELERATE
            next_action = NextAction(
                type='ACCELERATE',
                description='Your foundation is solid and you have traction. Accelerate validation.',
                success_criteria='Revenue-generating pilot running.',
            )
        elif current_phase == 1:
            category = ROUTE_CONTINUE
            next_action = NextAction(
                type='NEXT_QUESTION',
                description='Continue Phase 1 — complete your readiness assessment.',
                success_criteria='All Phase 1 dimensions assessed.',
            )
        elif current_phase == 2:
            if not responses.get('target_user_specific', True):
                category = ROUTE_CLARIFY
                next_action = NextAction(
                    type='DEEPEN_TARGET_USER',
                    description='Clarify who your target user is before proceeding.',
                    success_criteria='Specific target user defined.',
                )
            else:
                category = ROUTE_VALIDATE
                next_action = NextAction(
                    type='START_CUSTOMER_DISCOVERY',
                    description='Your idea is clear enough — time to test it with real people.',
                    success_criteria='First 3 discovery conversations completed.',
                    estimated_time='1-2 weeks',
                )
        else:
            category = ROUTE_CONTINUE
            next_action = NextAction(
                type='CONTINUE_PHASE',
                description=f'Continue Phase {current_phase}.',
                success_criteria='Complete current phase milestones.',
            )

        return self._make_decision(
            category=category,
            priority_level=PRIORITY_DEFAULT,
            blocked_actions=[],
            allowed_actions=['all_actions'],
            next_action=next_action,
            is_reroute=False,
            reroute_message=None,
            overperformance_signal=overperformance.signal_type if overperformance else None,
            verification_tasks=overperformance.verification_tasks if overperformance else [],
        )

    # ------------------------------------------------------------------
    # Overperformance detection (CEO Section 4.6)
    # ------------------------------------------------------------------
    def detect_overperformance(self, session_data: dict, founder_profile: dict) -> Optional[OverperformanceSignal]:
        return self._detect_overperformance(session_data, founder_profile)

    def _detect_overperformance(self, session_data: dict, founder_profile: dict) -> Optional[OverperformanceSignal]:
        """
        CEO Section 4.6: High scores fast can be:
          GENUINE_READINESS — accelerate
          POLISHED_UNREALITY — verify first
          BURNOUT_PERFORMANCE — slow down
          AI_INFLATION — ask follow-up questions
        """
        overall = int(founder_profile.get('overall_readiness_level', 3))
        burnout_signal = bool(founder_profile.get('burnout_signal', False))
        overload_signal = bool(founder_profile.get('overload_signal', False))
        time_to_complete_sec = int(session_data.get('completion_time_seconds', 999))
        stress_level = int(founder_profile.get('personal_stability_level', 0))
        hours = float(session_data.get('weekly_hours_reported', 20))

        # Fast completion + perfect score → polished or AI-inflated
        if time_to_complete_sec < 180 and overall == 0:
            if session_data.get('answers_look_optimised'):
                return OverperformanceSignal(
                    signal_type=OVERPERFORMANCE_AI_INFLATE,
                    confidence='MEDIUM',
                    reasoning='Unusually fast completion with very optimistic answers.',
                    verification_tasks=[
                        'Complete one "reality check" follow-up question for each dimension',
                        'Describe a specific setback you experienced in the past year',
                    ],
                )

        # High stress + burnout signal + still high scores → burnout performance
        if burnout_signal and stress_level >= 3 and overall <= 1:
            return OverperformanceSignal(
                signal_type=OVERPERFORMANCE_BURNOUT,
                confidence='MEDIUM',
                reasoning='Burnout/stress signals combined with high performance scores suggests unsustainable pace.',
                verification_tasks=[
                    'Track your actual hours for 1 week (not estimated)',
                    'Rate your energy honestly at 3 different times today',
                ],
            )

        # Genuinely good profile
        if overall == 0 and not burnout_signal and not overload_signal:
            return OverperformanceSignal(
                signal_type=OVERPERFORMANCE_GENUINE,
                confidence='MEDIUM',
                reasoning='Solid profile across all dimensions.',
                verification_tasks=[],
            )

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_stability_reroute(self, financial_level: int, stability_level: int) -> RerouteMessage:
        if financial_level >= LEVEL_SOFT_BLOCK:
            return RerouteMessage(
                detected='Short financial runway',
                why='Building without financial safety net creates decisions driven by desperation, not good judgement.',
                blocked_action='paid tools, outsourcing, marketing spend',
                allowed_action='free research, planning, customer conversations',
                unlock_condition='Build runway to 3+ months.',
            )
        return RerouteMessage(
            detected='Personal stability concerns',
            why='Sustained building requires sustained energy. Protecting your capacity now protects the venture.',
            blocked_action='high-pressure tasks, investor pitching, hiring',
            allowed_action='light planning, research, conversations',
            unlock_condition='2 weeks of consistent, lower-intensity activity.',
        )

    @staticmethod
    def _make_decision(
        category: str,
        priority_level: int,
        blocked_actions: list,
        allowed_actions: list,
        next_action: NextAction,
        is_reroute: bool,
        reroute_message: Optional[RerouteMessage],
        overperformance_signal: Optional[str] = None,
        verification_tasks: List[str] = None,
        contradictions_summary: Optional[str] = None,
    ) -> RoutingDecision:
        return RoutingDecision(
            category=category,
            priority_level=priority_level,
            allowed_actions=allowed_actions,
            blocked_actions=blocked_actions,
            next_action=next_action,
            is_reroute=is_reroute,
            reroute_message=reroute_message,
            overperformance_signal=overperformance_signal,
            verification_tasks=verification_tasks or [],
            contradictions_summary=contradictions_summary,
        )

    def compute_reroute_message_text(self, decision: RoutingDecision) -> str:
        """
        Generate the full 5-element reroute message as a human-readable string.
        CEO Section 3.4 template.
        """
        if not decision.reroute_message:
            return ''
        m = decision.reroute_message
        na = decision.next_action
        return (
            f"I am not sending you to your next normal step yet.\n\n"
            f"Based on {m.detected}, the more responsible next step is: "
            f"{na.description}\n\n"
            f"This matters because: {m.why}\n\n"
            f"For now, {m.blocked_action} is paused — but {m.allowed_action} can continue.\n\n"
            f"To unlock the next stage: {m.unlock_condition}"
        )

    def get_routing_priority_order(self) -> list:
        """Returns the CEO-defined priority order as a human-readable list."""
        return [
            (PRIORITY_SAFETY_LEGAL,        'Safety and legality'),
            (PRIORITY_STABILITY,           'Personal and financial stability'),
            (PRIORITY_CONTRADICTIONS,      'Contradictions and data quality'),
            (PRIORITY_IDEA_CLARITY,        'Idea clarity'),
            (PRIORITY_MARKET_EVIDENCE,     'Market evidence'),
            (PRIORITY_BUSINESS_MODEL,      'Business model coherence'),
            (PRIORITY_OPERATIONAL_CAPACITY,'Operational capacity'),
            (PRIORITY_ACCELERATION,        'Acceleration opportunities'),
            (PRIORITY_DEFAULT,             'Next normal question (default)'),
        ]
