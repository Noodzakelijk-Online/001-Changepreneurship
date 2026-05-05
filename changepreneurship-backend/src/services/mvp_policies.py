"""Policy services for codable Changepreneurship MVP requirements.

These services are intentionally deterministic and lightweight. They provide the
rails for AI-generated content and future integrations.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.assessment import db
from src.models.mvp_infrastructure import FounderReadinessProfile, UserAction
from src.models.mvp_logic import (
    ActionOutcome,
    ActionPermissionPolicy,
    AssumptionRecord,
    BenchmarkEvent,
    CostEstimate,
    EvidenceRecord,
    ProfessionalReviewRequirement,
    SpendingCap,
    UserFitAssessment,
    VentureConnectionMode,
)


BLOCKER_PRIORITY_ORDER = [
    "legal_ethical_safety_regulatory",
    "personal_crisis_or_immediate_harm",
    "financial_survival_or_debt_pressure",
    "data_contradictions_or_unreliable_answers",
    "idea_clarity",
    "market_demand_or_evidence_quality",
    "business_model_or_financial_logic",
    "feasibility_or_operational_readiness",
    "mentor_or_support_gap",
    "communication_or_positioning_readiness",
    "acceleration_or_normal_progression",
]


@dataclass
class BlockingMessage:
    blocked_action: str
    reason: str
    risk_explanation: str
    allowed_actions: List[str]
    unlock_condition: str
    blocker_category: str
    severity: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def user_facing_message(self) -> str:
        allowed = "; ".join(self.allowed_actions) if self.allowed_actions else "low-risk preparation only"
        return (
            f"Blocked action: {self.blocked_action}. Reason: {self.reason}. "
            f"Risk: {self.risk_explanation}. Still allowed: {allowed}. "
            f"Unlock condition: {self.unlock_condition}."
        )


class BlockerPolicy:
    """Creates structured blocker messages in the required priority order."""

    PRIORITY = {category: index for index, category in enumerate(BLOCKER_PRIORITY_ORDER)}

    def highest_priority(self, blockers: List[BlockingMessage]) -> Optional[BlockingMessage]:
        if not blockers:
            return None
        return sorted(blockers, key=lambda item: self.PRIORITY.get(item.blocker_category, 999))[0]

    def message(
        self,
        *,
        blocked_action: str,
        reason: str,
        risk_explanation: str,
        unlock_condition: str,
        blocker_category: str,
        severity: str = "warning",
        allowed_actions: Optional[List[str]] = None,
    ) -> BlockingMessage:
        return BlockingMessage(
            blocked_action=blocked_action,
            reason=reason,
            risk_explanation=risk_explanation,
            allowed_actions=allowed_actions or ["manual preparation", "clarification", "evidence collection"],
            unlock_condition=unlock_condition,
            blocker_category=blocker_category,
            severity=severity,
        )


class EvidencePolicy:
    STRENGTH_ORDER = {
        "assumption": 0,
        "weak_signal": 1,
        "partial_validation": 2,
        "strong_validation": 3,
        "verified_fact": 4,
    }

    def create_evidence(
        self,
        *,
        user_id: int,
        venture_id: Optional[int],
        claim: str,
        evidence_type: str = "general",
        source: Optional[str] = None,
        evidence_strength: str = "assumption",
        confidence: str = "low",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRecord:
        if evidence_strength not in EvidenceRecord.VALID_STRENGTHS:
            evidence_strength = "assumption"
        record = EvidenceRecord(
            user_id=user_id,
            venture_id=venture_id,
            claim=claim,
            evidence_type=evidence_type,
            source=source,
            evidence_strength=evidence_strength,
            confidence=confidence,
        )
        record.set_metadata(metadata or {})
        db.session.add(record)
        db.session.commit()
        return record

    def has_minimum_strength(self, *, venture_id: Optional[int], minimum: str = "partial_validation") -> bool:
        if not venture_id:
            return False
        threshold = self.STRENGTH_ORDER.get(minimum, 2)
        records = EvidenceRecord.query.filter_by(venture_id=venture_id).all()
        return any(self.STRENGTH_ORDER.get(record.evidence_strength, 0) >= threshold for record in records)

    def guard_claim(self, *, venture_id: Optional[int], claim_text: str, required_strength: str = "partial_validation") -> Dict[str, Any]:
        allowed = self.has_minimum_strength(venture_id=venture_id, minimum=required_strength)
        return {
            "allowed": allowed,
            "claim_text": claim_text,
            "required_strength": required_strength,
            "language": "validated" if allowed else "assumption",
            "message": "Claim may be presented as validated." if allowed else "Claim must be presented as an assumption until supporting evidence exists.",
        }


class AssumptionPolicy:
    def create_assumption(
        self,
        *,
        user_id: int,
        venture_id: Optional[int],
        assumption_text: str,
        category: str = "general",
        risk_level: str = "medium",
    ) -> AssumptionRecord:
        assumption = AssumptionRecord(
            user_id=user_id,
            venture_id=venture_id,
            assumption_text=assumption_text,
            category=category,
            risk_level=risk_level,
            status="untested",
        )
        db.session.add(assumption)
        db.session.commit()
        return assumption

    def validation_action_payload(self, assumption: AssumptionRecord) -> Dict[str, Any]:
        return {
            "assumption_id": assumption.id,
            "assumption_text": assumption.assumption_text,
            "category": assumption.category,
            "risk_level": assumption.risk_level,
            "goal": "Collect real-world evidence for this assumption before high-commitment action.",
            "suggested_task": "Interview 3-5 relevant customers, beneficiaries, mentors, or domain experts.",
        }


class FounderTypeClassifier:
    """Rule-based first pass for dynamic Type A-P routing states."""

    def classify(self, profile: FounderReadinessProfile) -> Dict[str, Any]:
        dims = {name: profile.get_dimension(name) for name in profile.DIMENSIONS}
        evidence = dims.get("evidence_discipline", {}).get("status", "unknown")
        support = dims.get("support_network", {}).get("status", "unknown")
        idea = dims.get("founder_idea_fit", {}).get("status", "unknown")
        financial = dims.get("financial_readiness", {}).get("status", "unknown")
        operational = dims.get("operational_discipline", {}).get("status", "unknown")

        if profile.survival_risk_indicator in {"high", "critical"} or financial == "critical":
            return self._result("I", "Underprepared but Highly Motivated User", "high", "stabilization", "direct_supportive", "high")
        if idea in {"weak", "unknown"} and evidence in {"weak", "unknown"}:
            return self._result("P", "Non-Idea or unclear-idea entrepreneur", "medium", "slow", "exploratory", "medium")
        if evidence in {"adequate", "strong"} and operational in {"weak", "unknown"}:
            return self._result("E", "Side-Hustler With Traction", "medium", "medium", "practical", "medium")
        if support in {"weak", "unknown"} and evidence in {"weak", "unknown"}:
            return self._result("A", "Aspiring First-Time Founder", "medium", "slow", "simple_structured", "medium")
        if "impact" in (profile.summary or "").lower() or "non-profit" in (profile.summary or "").lower():
            return self._result("H", "Impact-Driven Founder", "low", "medium", "mission_and_sustainability", "medium")
        if "software" in (profile.summary or "").lower() or "app" in (profile.summary or "").lower():
            return self._result("L", "Digital Product / Software Founder", "low", "medium", "validation_before_building", "high")
        return self._result("B", "Career Switcher or general early founder", "low", "medium", "balanced", "medium")

    def _result(self, code: str, label: str, confidence: str, pacing: str, language: str, risk: str) -> Dict[str, Any]:
        return {
            "founder_type": code,
            "label": label,
            "confidence": confidence,
            "reason": f"Classified as {label} using the current typed readiness profile.",
            "recommended_pacing": pacing,
            "language_style": language,
            "risk_sensitivity": risk,
        }


class UserFitClassifier:
    def classify_from_text(self, *, user_id: int, venture_id: Optional[int], text: str) -> UserFitAssessment:
        lower = (text or "").lower()
        category = "conditional_fit"
        reason = "User appears eligible for guided venture-building with normal safeguards."
        allowed_mode = "guided"
        blocked_actions: List[str] = []
        redirect_route = None
        unlock_condition = None

        if any(term in lower for term in ["get rich quick", "guaranteed income", "passive income without effort"]):
            category = "permanent_non_fit"
            reason = "User appears to seek get-rich-quick outcomes rather than responsible venture-building."
            allowed_mode = "expectation_reset_only"
            blocked_actions = ["normal_venture_progression", "fundraising", "paid_execution"]
            redirect_route = "expectation_reset"
        elif any(term in lower for term in ["scam", "fake reviews", "deceive", "fraud", "illegal"]):
            category = "hard_exclusion"
            reason = "Requested venture direction appears harmful, deceptive, or illegal."
            allowed_mode = "refuse_direction"
            blocked_actions = ["all_build_actions"]
            redirect_route = "refusal_or_ethical_reframe"
        elif any(term in lower for term in ["no money", "no income", "urgent debt", "homeless", "crisis"]):
            category = "temporary_non_fit"
            reason = "User may need stabilization before active venture-building."
            allowed_mode = "stabilization"
            blocked_actions = ["paid_execution", "high_commitment_actions", "fundraising"]
            redirect_route = "stabilization_track"
            unlock_condition = "Minimum stability, runway, or support route must be clarified."

        assessment = UserFitAssessment(
            user_id=user_id,
            venture_id=venture_id,
            fit_category=category,
            reason=reason,
            allowed_mode=allowed_mode,
            redirect_route=redirect_route,
            unlock_condition=unlock_condition,
        )
        assessment.set_blocked_actions(blocked_actions)
        db.session.add(assessment)
        db.session.commit()
        return assessment


class PermissionPolicyService:
    EXTERNAL_EFFECT_SCOPES = {"send", "submit", "apply", "publish", "spend", "external_execute", "follow_up"}

    def create_for_action(
        self,
        *,
        action: UserAction,
        permission_scope: str = "prepare",
        execution_mode: str = "manual",
        allowed_operations: Optional[List[str]] = None,
    ) -> ActionPermissionPolicy:
        requires_external = permission_scope in self.EXTERNAL_EFFECT_SCOPES or execution_mode == "external_execute"
        policy = ActionPermissionPolicy(
            action_id=action.id,
            user_id=action.user_id,
            permission_scope=permission_scope,
            execution_mode=execution_mode,
            requires_external_effect=requires_external,
            requires_explicit_approval=True,
        )
        policy.set_allowed_operations(allowed_operations or ["review", "edit", "approve", "reject"])
        db.session.add(policy)
        db.session.commit()
        return policy

    def can_execute(self, action: UserAction) -> Dict[str, Any]:
        policy = ActionPermissionPolicy.query.filter_by(action_id=action.id).order_by(ActionPermissionPolicy.created_at.desc()).first()
        if not policy:
            return {"allowed": action.status == "approved", "reason": "No policy found; default requires approval."}
        if policy.requires_explicit_approval and action.status != "approved":
            return {"allowed": False, "reason": "Explicit approval is required before execution."}
        return {"allowed": True, "reason": "Permission policy allows execution."}


class OutcomeService:
    def record(
        self,
        *,
        action: UserAction,
        outcome_status: str,
        outcome_summary: Optional[str] = None,
        next_recommended_action_type: Optional[str] = None,
        next_follow_up_at: Optional[datetime] = None,
    ) -> ActionOutcome:
        outcome = ActionOutcome(
            action_id=action.id,
            user_id=action.user_id,
            venture_id=action.venture_id,
            outcome_status=outcome_status,
            outcome_summary=outcome_summary,
            next_follow_up_at=next_follow_up_at,
            next_recommended_action_type=next_recommended_action_type,
        )
        db.session.add(outcome)
        db.session.commit()
        BenchmarkService().record_event(
            user_id=action.user_id,
            venture_id=action.venture_id,
            event_type="action_outcome",
            action_type=action.action_type,
            outcome_status=outcome_status,
            metadata={"action_id": action.id},
        )
        return outcome


class BenchmarkService:
    def record_event(
        self,
        *,
        user_id: int,
        event_type: str,
        venture_id: Optional[int] = None,
        route: Optional[str] = None,
        founder_type: Optional[str] = None,
        phase_id: Optional[str] = None,
        action_type: Optional[str] = None,
        outcome_status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BenchmarkEvent:
        event = BenchmarkEvent(
            user_id=user_id,
            venture_id=venture_id,
            event_type=event_type,
            route=route,
            founder_type=founder_type,
            phase_id=phase_id,
            action_type=action_type,
            outcome_status=outcome_status,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event


class CostEstimateService:
    DEFAULT_MULTIPLIER = 2.5

    def create_estimate(
        self,
        *,
        user_id: int,
        estimated_direct_cost: float,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        currency: str = "EUR",
    ) -> CostEstimate:
        estimate = CostEstimate(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            estimated_direct_cost=estimated_direct_cost,
            estimated_billed_price=round(estimated_direct_cost * self.DEFAULT_MULTIPLIER, 2),
            pricing_multiplier=self.DEFAULT_MULTIPLIER,
            currency=currency,
        )
        db.session.add(estimate)
        db.session.commit()
        return estimate


class SpendingCapService:
    def create_cap(
        self,
        *,
        user_id: int,
        amount: float,
        venture_id: Optional[int] = None,
        cap_type: str = "per_action",
        currency: str = "EUR",
    ) -> SpendingCap:
        cap = SpendingCap(user_id=user_id, venture_id=venture_id, amount=amount, cap_type=cap_type, currency=currency)
        db.session.add(cap)
        db.session.commit()
        return cap

    def check_per_action_cap(self, *, user_id: int, venture_id: Optional[int], billed_price: float) -> Dict[str, Any]:
        cap = SpendingCap.query.filter_by(user_id=user_id, venture_id=venture_id, cap_type="per_action").order_by(SpendingCap.created_at.desc()).first()
        if not cap:
            return {"allowed": True, "requires_approval": False, "reason": "No per-action cap set."}
        if billed_price > cap.amount:
            return {"allowed": False, "requires_approval": cap.requires_approval_above_amount, "reason": "Estimated price exceeds per-action cap.", "cap": cap.to_dict()}
        return {"allowed": True, "requires_approval": False, "reason": "Within spending cap.", "cap": cap.to_dict()}


class AIBoundaryPolicy:
    RULES = {
        "no_fabricated_evidence": "AI must not invent evidence, interviews, customers, revenue, legal approval, or validation.",
        "no_validated_claims_without_evidence": "AI must downgrade unsupported claims to assumption language.",
        "no_hard_blocker_override": "AI cannot override hard blockers or professional review requirements.",
        "no_external_action_without_consent": "AI cannot send, submit, publish, spend, or change external records without user approval.",
        "no_professional_advice_replacement": "AI must refer where licensed professional judgment is required.",
        "no_spending_without_approval": "AI cannot trigger paid work above approval thresholds without approval.",
    }

    def evaluate_generated_action(self, *, action_payload: Dict[str, Any], venture_id: Optional[int]) -> Dict[str, Any]:
        text = str(action_payload).lower()
        violations = []
        if any(term in text for term in ["validated", "proven", "guaranteed", "confirmed demand"]):
            if not EvidencePolicy().has_minimum_strength(venture_id=venture_id, minimum="partial_validation"):
                violations.append("no_validated_claims_without_evidence")
        if any(term in text for term in ["legal advice", "tax advice", "medical advice", "investment advice"]):
            violations.append("no_professional_advice_replacement")
        return {
            "allowed": not violations,
            "violations": violations,
            "rules": {key: self.RULES[key] for key in violations},
        }


class ProfessionalReviewService:
    TRIGGER_TERMS = {
        "legal": ["legal", "lawsuit", "contract", "regulation", "permit", "non-compete"],
        "tax": ["tax", "vat", "belasting", "irs"],
        "accounting": ["audit", "accounting", "bookkeeping"],
        "financial": ["investment advice", "loan advice", "securities", "fundraising guarantee"],
        "medical": ["medical", "health diagnosis", "treatment"],
        "mental_health": ["therapy", "depression", "suicidal", "mental health diagnosis"],
    }

    def detect_and_create(self, *, user_id: int, venture_id: Optional[int], text: str, action_type: Optional[str] = None) -> List[ProfessionalReviewRequirement]:
        lower = (text or "").lower()
        created = []
        for category, terms in self.TRIGGER_TERMS.items():
            if any(term in lower for term in terms):
                req = ProfessionalReviewRequirement(
                    user_id=user_id,
                    venture_id=venture_id,
                    category=category,
                    trigger_reason=f"Detected possible {category} professional-review trigger.",
                    required_before_action_type=action_type,
                    status="required",
                )
                db.session.add(req)
                created.append(req)
        if created:
            db.session.commit()
        return created

    def is_satisfied_for_action(self, *, user_id: int, venture_id: Optional[int], action_type: str) -> Dict[str, Any]:
        requirements = ProfessionalReviewRequirement.query.filter_by(user_id=user_id, venture_id=venture_id, required_before_action_type=action_type, status="required").all()
        return {"allowed": len(requirements) == 0, "requirements": [req.to_dict() for req in requirements]}


class ConnectionModeService:
    def set_mode(self, *, user_id: int, venture_id: Optional[int], mode: str, explanation: Optional[str] = None) -> VentureConnectionMode:
        record = VentureConnectionMode(user_id=user_id, venture_id=venture_id, connection_mode=mode, explanation=explanation)
        db.session.add(record)
        db.session.commit()
        return record

    def current_mode(self, *, user_id: int, venture_id: Optional[int]) -> Dict[str, Any]:
        record = VentureConnectionMode.query.filter_by(user_id=user_id, venture_id=venture_id).order_by(VentureConnectionMode.created_at.desc()).first()
        if record:
            return record.to_dict()
        return {
            "connection_mode": "manual_mode",
            "explanation": "No connected-account mode set. Defaulting to manual/draft-only execution.",
        }
