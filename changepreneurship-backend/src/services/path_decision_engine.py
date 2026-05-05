"""Basic rule-based PathDecisionEngine for the MVP infrastructure pass.

This deliberately starts small. It gives the codebase a deterministic decision layer
before external execution is attempted. AI can later write narrative explanations on
top of these typed decisions, but should not be responsible for blocking decisions.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from src.models.mvp_infrastructure import FounderReadinessProfile


@dataclass
class PathDecision:
    route: str
    next_action_type: str
    risk_level: str
    blocker_status: str
    confidence: str
    explanation: str
    unlock_condition: Optional[str] = None
    recommended_action_title: Optional[str] = None
    recommended_action_payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PathDecisionEngine:
    """Safety-first rule engine for deciding the next route.

    Priority order used here:
    1. Survival/stability risk
    2. Critical financial/time/personal blockers
    3. No clear idea
    4. No evidence/validation
    5. Weak support network / mentor need
    6. Continue with next concrete action
    """

    CRITICAL_STATUSES = {"critical", "hard_stop"}
    WEAK_STATUSES = {"weak", "unknown"}

    def decide(self, profile: FounderReadinessProfile) -> PathDecision:
        dimensions = {name: profile.get_dimension(name) for name in profile.DIMENSIONS}

        survival = profile.survival_risk_indicator
        financial = dimensions.get("financial_readiness", {})
        time_capacity = dimensions.get("time_capacity", {})
        personal = dimensions.get("personal_readiness", {})
        idea_fit = dimensions.get("founder_idea_fit", {})
        evidence = dimensions.get("evidence_discipline", {})
        support = dimensions.get("support_network", {})

        if survival in {"high", "critical"}:
            return PathDecision(
                route="stabilize_founder",
                next_action_type="stability_plan",
                risk_level="high",
                blocker_status="hard_blocked",
                confidence="medium",
                explanation="The user appears to have survival or stability pressure. Active venture-building should wait until the foundation is safer.",
                unlock_condition="Create a basic stabilization plan and confirm minimum income/runway/time capacity.",
                recommended_action_title="Create stabilization plan",
                recommended_action_payload={
                    "goal": "Reduce immediate personal/financial instability before venture execution.",
                    "suggested_steps": [
                        "Clarify monthly obligations and available runway",
                        "Identify urgent income or debt pressure",
                        "Define the safest low-risk preparation task",
                    ],
                },
            )

        if self._status(financial) in self.CRITICAL_STATUSES:
            return PathDecision(
                route="stabilize_finances",
                next_action_type="financial_stability_review",
                risk_level="high",
                blocker_status="hard_blocked",
                confidence=self._confidence(financial),
                explanation="Financial readiness is critical. The platform should not recommend costly execution before basic financial safety is clarified.",
                unlock_condition="Clarify runway, obligations, and a safe spending limit before paid or high-commitment actions.",
                recommended_action_title="Review financial runway and safe spending limit",
                recommended_action_payload={"dimension": "financial_readiness"},
            )

        if self._status(time_capacity) in self.CRITICAL_STATUSES:
            return PathDecision(
                route="create_capacity",
                next_action_type="time_capacity_plan",
                risk_level="medium",
                blocker_status="soft_blocked",
                confidence=self._confidence(time_capacity),
                explanation="The user does not appear to have enough recurring time to execute venture tasks reliably.",
                unlock_condition="Define a realistic weekly time block before assigning real-world actions.",
                recommended_action_title="Define weekly execution capacity",
                recommended_action_payload={"dimension": "time_capacity"},
            )

        if self._status(personal) in self.CRITICAL_STATUSES:
            return PathDecision(
                route="stabilize_personal_readiness",
                next_action_type="personal_readiness_review",
                risk_level="high",
                blocker_status="hard_blocked",
                confidence=self._confidence(personal),
                explanation="Personal readiness appears too fragile for active venture execution. The safest next step is preparation, not acceleration.",
                unlock_condition="Resolve or reduce the personal readiness blocker before moving into external commitments.",
                recommended_action_title="Review personal readiness blocker",
                recommended_action_payload={"dimension": "personal_readiness"},
            )

        if self._status(idea_fit) in self.WEAK_STATUSES:
            return PathDecision(
                route="clarify_idea",
                next_action_type="idea_clarification",
                risk_level="low",
                blocker_status="warning",
                confidence=self._confidence(idea_fit),
                explanation="The idea/founder fit is not yet clear enough. The next step should clarify the problem, user, and reason this founder should pursue it.",
                recommended_action_title="Clarify the venture idea",
                recommended_action_payload={
                    "questions": [
                        "What problem are you solving?",
                        "Who has this problem?",
                        "Why are you the right person to explore it?",
                    ]
                },
            )

        if self._status(evidence) in self.WEAK_STATUSES:
            return PathDecision(
                route="validate_market",
                next_action_type="validation_task",
                risk_level="medium",
                blocker_status="warning",
                confidence=self._confidence(evidence),
                explanation="The current idea needs stronger outside evidence before serious building or spending.",
                recommended_action_title="Run a small validation task",
                recommended_action_payload={
                    "goal": "Collect real-world evidence before building.",
                    "suggested_task": "Prepare 3-5 customer or stakeholder interview requests.",
                },
            )

        if self._status(support) in self.WEAK_STATUSES:
            return PathDecision(
                route="seek_mentor",
                next_action_type="mentor_outreach",
                risk_level="low",
                blocker_status="warning",
                confidence=self._confidence(support),
                explanation="The user appears to need external support or a mentor before moving faster.",
                recommended_action_title="Prepare mentor outreach",
                recommended_action_payload={
                    "mentor_type": "founder or domain mentor",
                    "message_goal": "Ask for practical feedback on readiness, validation, and next steps.",
                },
            )

        return PathDecision(
            route="continue",
            next_action_type="next_best_action",
            risk_level=profile.risk_level or "medium",
            blocker_status="open",
            confidence=profile.route_confidence or "medium",
            explanation="No hard blocker was detected in the basic MVP rules. The user can proceed to the next concrete venture-building action.",
            recommended_action_title="Choose next concrete venture-building action",
            recommended_action_payload={"route": "continue"},
        )

    def _status(self, dimension: Dict[str, Any]) -> str:
        return str(dimension.get("status", "unknown")).lower()

    def _confidence(self, dimension: Dict[str, Any]) -> str:
        return str(dimension.get("confidence", "low")).lower()
