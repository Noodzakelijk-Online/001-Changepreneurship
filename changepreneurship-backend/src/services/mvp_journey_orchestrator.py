"""MVP Journey Orchestrator.

This is the missing product-level layer between the existing assessment/report
system and the new action infrastructure.

It answers the core MVP question for a user:

    Where am I now, what is unsafe or unclear, and what is the next concrete step?

The orchestrator deliberately avoids being a generic advice generator. It composes
existing structured systems:

- assessment collector / readiness adapter;
- PathDecisionEngine;
- FounderTypeClassifier;
- evidence and assumption records;
- mentor-source routing;
- action proposal/approval lifecycle.
"""

from typing import Any, Dict, Optional

from src.models.mvp_infrastructure import FounderReadinessProfile, PhaseGate, UserAction, Venture
from src.models.mvp_logic import AssumptionRecord, EvidenceRecord, ProfessionalReviewRequirement, UserFitAssessment
from src.services.action_engine import ActionEngine
from src.services.assessment_to_mvp_adapter import AssessmentToMVPAdapter
from src.services.mentor_source_router import MentorSourceRouter
from src.services.mvp_policies import EvidencePolicy, FounderTypeClassifier


PARTY_EXPLANATION = (
    "Changepreneurship helps people safely and seriously turn an idea into a real "
    "business or non-profit by acting like an automated co-founder that guides, "
    "challenges, validates, and helps build the venture step by step."
)

NON_NEGOTIABLES = [
    "The platform must not merely explain entrepreneurship.",
    "The platform must actively help test, structure, and build the venture.",
    "The platform must protect the user from avoidable failure and poorly timed risk.",
    "The platform must turn uncertainty into structured decisions, evidence, and concrete next actions.",
]


class MVPJourneyOrchestrator:
    """Builds the one canonical MVP state for the current user/venture."""

    def get_state(
        self,
        *,
        user_id: int,
        venture_id: Optional[int] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        venture_type: Optional[str] = None,
        create_action: bool = False,
    ) -> Dict[str, Any]:
        venture, profile, decision, gate = AssessmentToMVPAdapter().bootstrap(user_id=user_id, venture_id=venture_id)
        founder_type = FounderTypeClassifier().classify(profile)
        latest_action = self._latest_action(user_id=user_id, venture_id=venture.id)

        evidence_summary = self._evidence_summary(user_id=user_id, venture_id=venture.id)
        assumption_summary = self._assumption_summary(user_id=user_id, venture_id=venture.id)
        risk_summary = self._risk_summary(user_id=user_id, venture_id=venture.id, profile=profile, gate=gate)
        mentor_recommendation = self._mentor_recommendation(
            profile=profile,
            country=country,
            region=region,
            venture_type=venture_type or venture.venture_type,
            founder_type=founder_type.get("founder_type"),
            decision_action_type=decision.next_action_type,
        )

        action = latest_action
        if create_action:
            action = self._get_or_create_current_action(
                user_id=user_id,
                venture_id=venture.id,
                decision=decision,
                existing_action=latest_action,
            )

        mvp_status = self._mvp_status(decision=decision, risk_summary=risk_summary, evidence_summary=evidence_summary)
        next_step_card = self._next_step_card(
            decision=decision,
            risk_summary=risk_summary,
            evidence_summary=evidence_summary,
            assumption_summary=assumption_summary,
            mentor_recommendation=mentor_recommendation,
            action=action,
        )

        return {
            "party_explanation": PARTY_EXPLANATION,
            "non_negotiables": NON_NEGOTIABLES,
            "mvp_status": mvp_status,
            "venture": venture.to_dict(),
            "readiness_profile": profile.to_dict(),
            "founder_type": founder_type,
            "decision": decision.to_dict(),
            "phase_gate": gate.to_dict() if gate else None,
            "evidence_summary": evidence_summary,
            "assumption_summary": assumption_summary,
            "risk_summary": risk_summary,
            "mentor_recommendation": mentor_recommendation,
            "current_action": action.to_dict() if action else None,
            "next_step_card": next_step_card,
            "mvp_completeness": self._mvp_completeness(
                profile=profile,
                evidence_summary=evidence_summary,
                assumption_summary=assumption_summary,
                current_action=action,
            ),
        }

    def _latest_action(self, *, user_id: int, venture_id: Optional[int]) -> Optional[UserAction]:
        return (
            UserAction.query
            .filter_by(user_id=user_id, venture_id=venture_id)
            .order_by(UserAction.created_at.desc())
            .first()
        )

    def _get_or_create_current_action(self, *, user_id: int, venture_id: int, decision, existing_action: Optional[UserAction]) -> UserAction:
        reusable_statuses = {"proposed", "edited", "approved"}
        if existing_action and existing_action.action_type == decision.next_action_type and existing_action.status in reusable_statuses:
            return existing_action
        return ActionEngine().propose_action(
            user_id=user_id,
            venture_id=venture_id,
            action_type=decision.next_action_type,
            title=decision.recommended_action_title or "Recommended next action",
            description=decision.explanation,
            proposed_content=decision.recommended_action_payload or {},
            estimated_cost=0.0,
        )

    def _evidence_summary(self, *, user_id: int, venture_id: Optional[int]) -> Dict[str, Any]:
        records = EvidenceRecord.query.filter_by(user_id=user_id, venture_id=venture_id).all()
        counts = {"assumption": 0, "weak_signal": 0, "partial_validation": 0, "strong_validation": 0, "verified_fact": 0}
        for record in records:
            counts[record.evidence_strength] = counts.get(record.evidence_strength, 0) + 1
        has_validation = EvidencePolicy().has_minimum_strength(venture_id=venture_id, minimum="partial_validation")
        return {
            "total": len(records),
            "counts_by_strength": counts,
            "has_partial_validation_or_better": has_validation,
            "strongest_available": self._strongest_evidence(counts),
            "message": "Evidence is strong enough for cautious next steps." if has_validation else "No partial validation or stronger evidence is recorded yet.",
        }

    def _strongest_evidence(self, counts: Dict[str, int]) -> str:
        order = ["verified_fact", "strong_validation", "partial_validation", "weak_signal", "assumption"]
        for strength in order:
            if counts.get(strength, 0) > 0:
                return strength
        return "none"

    def _assumption_summary(self, *, user_id: int, venture_id: Optional[int]) -> Dict[str, Any]:
        assumptions = AssumptionRecord.query.filter_by(user_id=user_id, venture_id=venture_id).all()
        high_risk_untested = [
            item for item in assumptions
            if item.status in {"untested", "testing"} and item.risk_level in {"high", "critical"}
        ]
        return {
            "total": len(assumptions),
            "high_risk_untested_count": len(high_risk_untested),
            "high_risk_untested": [item.to_dict() for item in high_risk_untested[:5]],
            "message": "High-risk assumptions need validation before serious execution." if high_risk_untested else "No high-risk untested assumptions are currently recorded.",
        }

    def _risk_summary(self, *, user_id: int, venture_id: Optional[int], profile: FounderReadinessProfile, gate: Optional[PhaseGate]) -> Dict[str, Any]:
        latest_fit = (
            UserFitAssessment.query
            .filter_by(user_id=user_id, venture_id=venture_id)
            .order_by(UserFitAssessment.created_at.desc())
            .first()
        )
        professional_requirements = (
            ProfessionalReviewRequirement.query
            .filter_by(user_id=user_id, venture_id=venture_id, status="required")
            .all()
        )
        return {
            "risk_level": profile.risk_level,
            "survival_risk_indicator": profile.survival_risk_indicator,
            "active_gate": gate.to_dict() if gate else None,
            "user_fit": latest_fit.to_dict() if latest_fit else None,
            "professional_review_required_count": len(professional_requirements),
            "professional_review_requirements": [item.to_dict() for item in professional_requirements],
            "is_hard_blocked": bool(gate and gate.gate_status in {"hard_blocked", "hard_stop"}) or len(professional_requirements) > 0,
        }

    def _mentor_recommendation(
        self,
        *,
        profile: FounderReadinessProfile,
        country: Optional[str],
        region: Optional[str],
        venture_type: Optional[str],
        founder_type: Optional[str],
        decision_action_type: str,
    ) -> Optional[Dict[str, Any]]:
        support = profile.get_dimension("support_network").get("status", "unknown")
        if decision_action_type != "mentor_outreach" and support not in {"weak", "unknown"}:
            return None
        return MentorSourceRouter().recommend(
            profile=profile,
            country=country,
            region=region,
            venture_type=venture_type,
            founder_type=founder_type,
            mentor_need="general_business",
            max_results=5,
        )

    def _mvp_status(self, *, decision, risk_summary: Dict[str, Any], evidence_summary: Dict[str, Any]) -> Dict[str, Any]:
        if risk_summary["is_hard_blocked"] or decision.blocker_status in {"hard_blocked", "hard_stop"}:
            code = "blocked_for_user_protection"
        elif decision.route in {"clarify_idea", "stabilize_founder", "stabilize_finances", "create_capacity"}:
            code = "foundation_not_ready"
        elif decision.route == "validate_market" or not evidence_summary["has_partial_validation_or_better"]:
            code = "needs_validation"
        elif decision.route == "seek_mentor":
            code = "needs_support"
        else:
            code = "ready_for_next_safe_action"
        return {
            "code": code,
            "label": code.replace("_", " ").title(),
            "is_safe_to_accelerate": code == "ready_for_next_safe_action",
        }

    def _next_step_card(
        self,
        *,
        decision,
        risk_summary: Dict[str, Any],
        evidence_summary: Dict[str, Any],
        assumption_summary: Dict[str, Any],
        mentor_recommendation: Optional[Dict[str, Any]],
        action: Optional[UserAction],
    ) -> Dict[str, Any]:
        allowed_now = ["review the diagnosis", "answer missing questions", "collect evidence"]
        if decision.blocker_status not in {"hard_blocked", "hard_stop"}:
            allowed_now.append("approve a low-risk next action")
        if mentor_recommendation:
            allowed_now.append("choose a mentor source")

        return {
            "title": decision.recommended_action_title or "Choose the next safe action",
            "why_this_now": decision.explanation,
            "risk_level": decision.risk_level,
            "blocked": risk_summary["is_hard_blocked"] or decision.blocker_status in {"hard_blocked", "hard_stop"},
            "blocker_status": decision.blocker_status,
            "unlock_condition": decision.unlock_condition,
            "allowed_now": allowed_now,
            "evidence_warning": evidence_summary["message"],
            "assumption_warning": assumption_summary["message"],
            "action_id": action.id if action else None,
            "action_status": action.status if action else None,
            "primary_api_action": "/api/mvp/journey-state?create_action=true" if not action else f"/api/mvp/actions/{action.id}/approve",
            "mentor_source_suggestions": (mentor_recommendation or {}).get("recommendations", [])[:3],
        }

    def _mvp_completeness(
        self,
        *,
        profile: FounderReadinessProfile,
        evidence_summary: Dict[str, Any],
        assumption_summary: Dict[str, Any],
        current_action: Optional[UserAction],
    ) -> Dict[str, Any]:
        checks = {
            "has_structured_readiness_profile": bool(profile),
            "has_next_decision": True,
            "has_concrete_action": bool(current_action),
            "has_evidence_tracking": evidence_summary["total"] > 0,
            "has_assumption_tracking": assumption_summary["total"] > 0,
            "has_user_protection_logic": profile.risk_level in {"medium", "high", "critical", "low", "unknown"},
        }
        score = round(sum(1 for value in checks.values() if value) / len(checks) * 100)
        return {
            "score": score,
            "checks": checks,
            "message": "This user has a usable MVP journey state." if score >= 70 else "This user still needs more structured data before the MVP journey feels complete.",
        }
