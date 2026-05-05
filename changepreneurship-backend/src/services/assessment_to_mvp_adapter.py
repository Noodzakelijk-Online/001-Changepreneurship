"""Adapter from existing assessment data to MVP infrastructure.

The current codebase already collects phase responses for AI reports. This adapter
uses that existing data to create a first structured FounderReadinessProfile, then
runs the rule-based PathDecisionEngine. It is intentionally conservative and should
be refined over time with product-specific rules.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.models.assessment import db
from src.models.mvp_infrastructure import FounderReadinessProfile, PhaseGate, Venture
from src.services.path_decision_engine import PathDecisionEngine, PathDecision
from src.utils.assessment_collector import collect_assessment_data


class AssessmentToMVPAdapter:
    """Converts existing assessment responses into structured MVP primitives."""

    def bootstrap(self, *, user_id: int, venture_id: Optional[int] = None) -> Tuple[Venture, FounderReadinessProfile, PathDecision, Optional[PhaseGate]]:
        venture = self._get_or_create_venture(user_id=user_id, venture_id=venture_id)
        assessment_data = collect_assessment_data(user_id)
        profile = self._upsert_profile(user_id=user_id, venture_id=venture.id, assessment_data=assessment_data)
        decision = PathDecisionEngine().decide(profile)
        gate = self._sync_phase_gate(user_id=user_id, venture_id=venture.id, decision=decision)
        return venture, profile, decision, gate

    def _get_or_create_venture(self, *, user_id: int, venture_id: Optional[int]) -> Venture:
        if venture_id:
            venture = Venture.query.filter_by(id=venture_id, user_id=user_id).first()
            if venture:
                return venture

        venture = Venture.query.filter_by(user_id=user_id, status="active").order_by(Venture.created_at.asc()).first()
        if venture:
            return venture

        venture = Venture(
            user_id=user_id,
            name="Default venture",
            stage="self_discovery",
            status="active",
        )
        db.session.add(venture)
        db.session.commit()
        return venture

    def _upsert_profile(self, *, user_id: int, venture_id: int, assessment_data: Dict[str, Any]) -> FounderReadinessProfile:
        profile = FounderReadinessProfile.query.filter_by(user_id=user_id, venture_id=venture_id).first()
        if not profile:
            profile = FounderReadinessProfile(user_id=user_id, venture_id=venture_id)
            db.session.add(profile)

        responses = self._flatten_responses(assessment_data)
        phase_summary = self._phase_summary(assessment_data)

        dimensions = {
            "financial_readiness": self._score_financial(responses),
            "time_capacity": self._score_time_capacity(responses),
            "personal_readiness": self._score_personal_readiness(responses),
            "skills_experience": self._score_by_phase(phase_summary, "self", "Skills and experience inferred from assessment completion."),
            "execution_behaviour": self._score_execution(assessment_data),
            "evidence_discipline": self._score_evidence(assessment_data, responses),
            "communication_ability": self._score_communication(responses),
            "support_network": self._score_support_network(responses),
            "founder_idea_fit": self._score_idea_fit(assessment_data, responses),
            "founder_market_fit": self._score_market_fit(assessment_data, responses),
            "risk_awareness": self._score_risk_awareness(responses),
            "operational_discipline": self._score_by_phase(phase_summary, "business", "Operational discipline inferred from business-planning responses."),
            "automation_leverage": self._status("unknown", "low", "Automation leverage is not yet assessed by the existing questionnaire.", False),
        }

        for name, payload in dimensions.items():
            profile.set_dimension(name, payload)

        critical_count = sum(1 for payload in dimensions.values() if payload.get("status") == "critical")
        weak_count = sum(1 for payload in dimensions.values() if payload.get("status") == "weak")
        adequate_count = sum(1 for payload in dimensions.values() if payload.get("status") in {"adequate", "strong"})

        if critical_count:
            profile.venture_readiness_status = "blocked"
            profile.risk_level = "high"
            profile.next_step_eligibility = "stabilization_required"
            profile.survival_risk_indicator = "critical"
        elif weak_count >= 4:
            profile.venture_readiness_status = "fragile"
            profile.risk_level = "medium"
            profile.next_step_eligibility = "limited_next_action"
            profile.survival_risk_indicator = "medium"
        elif adequate_count >= 7:
            profile.venture_readiness_status = "adequate"
            profile.risk_level = "medium"
            profile.next_step_eligibility = "next_action_allowed"
            profile.survival_risk_indicator = "low"
        else:
            profile.venture_readiness_status = "early"
            profile.risk_level = "medium"
            profile.next_step_eligibility = "needs_more_diagnosis"
            profile.survival_risk_indicator = "unknown"

        profile.evidence_confidence = dimensions["evidence_discipline"].get("confidence", "low")
        profile.external_readiness_status = "not_ready" if critical_count else "manual_or_mock_only"
        profile.founder_venture_fit_status = dimensions["founder_idea_fit"].get("status", "unknown")
        profile.route_confidence = "medium" if len(responses) >= 15 else "low"
        profile.routing_state = profile.next_step_eligibility
        profile.summary = self._summary_text(assessment_data, dimensions)

        db.session.commit()
        return profile

    def _sync_phase_gate(self, *, user_id: int, venture_id: int, decision: PathDecision) -> Optional[PhaseGate]:
        if decision.blocker_status == "open":
            return None

        gate = PhaseGate(
            user_id=user_id,
            venture_id=venture_id,
            phase_id="self_discovery",
            gate_status=decision.blocker_status,
            blocking_dimension=decision.route,
            blocking_reason=decision.explanation,
            unlock_condition=decision.unlock_condition,
        )
        db.session.add(gate)
        db.session.commit()
        return gate

    def _flatten_responses(self, assessment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        flattened: List[Dict[str, Any]] = []
        for phase_id, responses in (assessment_data.get("responses") or {}).items():
            for response in responses:
                flattened.append({**response, "phase_id": phase_id})
        return flattened

    def _phase_summary(self, assessment_data: Dict[str, Any]) -> Dict[str, int]:
        return {phase.get("id", ""): int(phase.get("progress") or 0) for phase in assessment_data.get("phases", [])}

    def _text_blob(self, responses: List[Dict[str, Any]]) -> str:
        parts = []
        for response in responses:
            parts.append(str(response.get("question_text", "")))
            parts.append(str(response.get("response_value", "")))
            parts.append(str(response.get("question_id", "")))
        return " ".join(parts).lower()

    def _status(self, status: str, confidence: str, note: str, blocker: bool = False) -> Dict[str, Any]:
        return {
            "status": status,
            "confidence": confidence,
            "evidence_note": note,
            "blocker_flag": blocker,
        }

    def _score_financial(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        if any(term in text for term in ["debt", "no income", "no savings", "zero runway", "bankrupt", "can't pay", "cannot pay"]):
            return self._status("critical", "medium", "Possible financial instability detected from assessment text.", True)
        if any(term in text for term in ["runway", "savings", "income", "salary", "budget", "financial"]):
            return self._status("adequate", "low", "Financial readiness has some supporting assessment signals.")
        return self._status("unknown", "low", "Financial readiness is not clearly assessed yet.")

    def _score_time_capacity(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        if any(term in text for term in ["no time", "0 hours", "zero hours", "too busy"]):
            return self._status("critical", "medium", "Possible time-capacity blocker detected.", True)
        if any(term in text for term in ["hours", "weekly", "schedule", "time"]):
            return self._status("adequate", "low", "Time capacity has some supporting assessment signals.")
        return self._status("unknown", "low", "Time capacity is not clearly assessed yet.")

    def _score_personal_readiness(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        if any(term in text for term in ["burnout", "depression", "crisis", "homeless", "unsafe"]):
            return self._status("critical", "medium", "Possible personal stability blocker detected.", True)
        if any(term in text for term in ["stress", "overwhelmed", "anxiety"]):
            return self._status("weak", "medium", "Possible personal readiness concern detected.")
        return self._status("adequate", "low", "No obvious personal-readiness blocker detected in existing responses.")

    def _score_evidence(self, assessment_data: Dict[str, Any], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        market_responses = assessment_data.get("responses", {}).get("market_research", [])
        if any(term in text for term in ["customer interview", "interviews", "pilot", "preorder", "survey", "validated"]):
            return self._status("adequate", "medium", "Some validation/evidence signals were detected.")
        if market_responses:
            return self._status("weak", "medium", "Market-research phase exists, but real-world validation evidence is not clear yet.")
        return self._status("weak", "low", "No clear market validation evidence detected.")

    def _score_support_network(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        if any(term in text for term in ["mentor", "advisor", "network", "cofounder", "co-founder", "team"]):
            return self._status("adequate", "low", "Support-network signals were detected.")
        return self._status("weak", "low", "No clear support network or mentor signal detected.")

    def _score_idea_fit(self, assessment_data: Dict[str, Any], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        idea_responses = assessment_data.get("responses", {}).get("idea_discovery", [])
        text = self._text_blob(responses)
        if len(idea_responses) >= 5 or any(term in text for term in ["problem", "solution", "target customer", "value proposition"]):
            return self._status("adequate", "medium", "Idea/founder fit has some supporting assessment signals.")
        return self._status("weak", "low", "Idea/founder fit needs clarification.")

    def _score_market_fit(self, assessment_data: Dict[str, Any], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        market_responses = assessment_data.get("responses", {}).get("market_research", [])
        if len(market_responses) >= 5:
            return self._status("adequate", "medium", "Market-fit assessment has some response depth.")
        return self._status("weak", "low", "Market fit is not sufficiently evidenced yet.")

    def _score_execution(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        completed_phases = [phase for phase in assessment_data.get("phases", []) if phase.get("completed")]
        if len(completed_phases) >= 4:
            return self._status("adequate", "medium", "Multiple phases completed, showing execution follow-through.")
        if len(completed_phases) >= 1:
            return self._status("weak", "medium", "Some follow-through exists, but execution pattern is still early.")
        return self._status("unknown", "low", "Execution behaviour is not yet demonstrated.")

    def _score_communication(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text_responses = [str(r.get("response_value", "")) for r in responses if r.get("response_type") == "text"]
        long_answers = [value for value in text_responses if len(value) >= 80]
        if len(long_answers) >= 3:
            return self._status("adequate", "medium", "Several detailed written answers suggest sufficient communication ability.")
        return self._status("unknown", "low", "Communication ability is not clearly assessed yet.")

    def _score_risk_awareness(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = self._text_blob(responses)
        if any(term in text for term in ["risk", "assumption", "uncertain", "unknown", "validation"]):
            return self._status("adequate", "medium", "Risk-awareness signals were detected.")
        return self._status("weak", "low", "Risk awareness is not clear from existing responses.")

    def _score_by_phase(self, phase_summary: Dict[str, int], phase_keyword: str, note: str) -> Dict[str, Any]:
        matching_progress = [progress for phase, progress in phase_summary.items() if phase_keyword in phase]
        if matching_progress and max(matching_progress) >= 80:
            return self._status("adequate", "low", note)
        if matching_progress and max(matching_progress) >= 30:
            return self._status("weak", "low", note)
        return self._status("unknown", "low", note)

    def _summary_text(self, assessment_data: Dict[str, Any], dimensions: Dict[str, Dict[str, Any]]) -> str:
        total_phases = len(assessment_data.get("phases", []))
        total_responses = sum(len(items) for items in (assessment_data.get("responses") or {}).values())
        weak_or_critical = [name for name, payload in dimensions.items() if payload.get("status") in {"weak", "critical"}]
        return (
            f"Bootstrapped from existing assessment data: {total_phases} phases and {total_responses} responses. "
            f"Dimensions needing attention: {', '.join(weak_or_critical[:5]) or 'none detected in basic adapter'}."
        )
