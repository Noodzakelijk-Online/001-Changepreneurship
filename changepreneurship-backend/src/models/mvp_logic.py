"""Additional MVP logic models derived from the Changepreneurship requirements.

These models extend the first MVP infrastructure pass without replacing it. They
turn document requirements into structured backend records that can be used by
routing, blockers, action approvals, evidence checks, billing, and analytics.

Migration note: generate/review Alembic migrations locally before deployment.
"""

from datetime import datetime
import json
from typing import Any, Dict, Optional

from src.models.assessment import db


class JsonTextMixin:
    @staticmethod
    def _loads(value: Optional[str], fallback: Any = None) -> Any:
        if value in (None, ""):
            return {} if fallback is None else fallback
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {} if fallback is None else fallback

    @staticmethod
    def _dumps(value: Any) -> str:
        return json.dumps(value if value is not None else {})


class EvidenceRecord(db.Model, JsonTextMixin):
    """Evidence attached to a venture claim.

    Evidence strength is deliberately explicit so assumptions cannot silently turn
    into validated claims.
    """

    __tablename__ = "evidence_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    evidence_type = db.Column(db.String(80), nullable=False, default="general")
    source = db.Column(db.String(160), nullable=True)
    claim = db.Column(db.Text, nullable=False)
    evidence_strength = db.Column(db.String(40), nullable=False, default="assumption")
    confidence = db.Column(db.String(40), nullable=False, default="low")
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("evidence_records", lazy=True, cascade="all, delete-orphan"))

    VALID_STRENGTHS = {"assumption", "weak_signal", "partial_validation", "strong_validation", "verified_fact"}

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "evidence_type": self.evidence_type,
            "source": self.source,
            "claim": self.claim,
            "evidence_strength": self.evidence_strength,
            "confidence": self.confidence,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AssumptionRecord(db.Model):
    """A venture assumption that may require validation before serious action."""

    __tablename__ = "assumption_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    assumption_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, default="general")
    status = db.Column(db.String(40), nullable=False, default="untested")
    risk_level = db.Column(db.String(40), nullable=False, default="medium")
    linked_evidence_id = db.Column(db.Integer, db.ForeignKey("evidence_record.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("assumption_records", lazy=True, cascade="all, delete-orphan"))
    linked_evidence = db.relationship("EvidenceRecord")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "assumption_text": self.assumption_text,
            "category": self.category,
            "status": self.status,
            "risk_level": self.risk_level,
            "linked_evidence_id": self.linked_evidence_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserFitAssessment(db.Model, JsonTextMixin):
    """Structured user fit / exclusion classification."""

    __tablename__ = "user_fit_assessment"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    fit_category = db.Column(db.String(40), nullable=False, default="conditional_fit")
    reason = db.Column(db.Text, nullable=True)
    allowed_mode = db.Column(db.String(80), nullable=False, default="guided")
    blocked_actions_json = db.Column(db.Text, nullable=False, default="[]")
    redirect_route = db.Column(db.String(80), nullable=True)
    unlock_condition = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("fit_assessments", lazy=True, cascade="all, delete-orphan"))

    def set_blocked_actions(self, actions: list) -> None:
        self.blocked_actions_json = self._dumps(actions)

    def get_blocked_actions(self) -> list:
        return self._loads(self.blocked_actions_json, fallback=[])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "fit_category": self.fit_category,
            "reason": self.reason,
            "allowed_mode": self.allowed_mode,
            "blocked_actions": self.get_blocked_actions(),
            "redirect_route": self.redirect_route,
            "unlock_condition": self.unlock_condition,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ActionPermissionPolicy(db.Model, JsonTextMixin):
    """Explicit permission and execution-mode policy for a UserAction."""

    __tablename__ = "action_permission_policy"

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    permission_scope = db.Column(db.String(80), nullable=False, default="prepare")
    execution_mode = db.Column(db.String(80), nullable=False, default="manual")
    requires_external_effect = db.Column(db.Boolean, nullable=False, default=False)
    requires_explicit_approval = db.Column(db.Boolean, nullable=False, default=True)
    allowed_operations_json = db.Column(db.Text, nullable=False, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_allowed_operations(self, operations: list) -> None:
        self.allowed_operations_json = self._dumps(operations)

    def get_allowed_operations(self) -> list:
        return self._loads(self.allowed_operations_json, fallback=[])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_id": self.action_id,
            "user_id": self.user_id,
            "permission_scope": self.permission_scope,
            "execution_mode": self.execution_mode,
            "requires_external_effect": self.requires_external_effect,
            "requires_explicit_approval": self.requires_explicit_approval,
            "allowed_operations": self.get_allowed_operations(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ActionOutcome(db.Model):
    """Structured outcome tracking for actions."""

    __tablename__ = "action_outcome"

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    outcome_status = db.Column(db.String(60), nullable=False, default="pending")
    outcome_summary = db.Column(db.Text, nullable=True)
    next_follow_up_at = db.Column(db.DateTime, nullable=True)
    next_recommended_action_type = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_id": self.action_id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "outcome_status": self.outcome_status,
            "outcome_summary": self.outcome_summary,
            "next_follow_up_at": self.next_follow_up_at.isoformat() if self.next_follow_up_at else None,
            "next_recommended_action_type": self.next_recommended_action_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BenchmarkEvent(db.Model, JsonTextMixin):
    """Internal analytics event for learning from routes, actions, and outcomes."""

    __tablename__ = "benchmark_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    event_type = db.Column(db.String(80), nullable=False)
    route = db.Column(db.String(80), nullable=True)
    founder_type = db.Column(db.String(8), nullable=True)
    phase_id = db.Column(db.String(80), nullable=True)
    action_type = db.Column(db.String(80), nullable=True)
    outcome_status = db.Column(db.String(80), nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "event_type": self.event_type,
            "route": self.route,
            "founder_type": self.founder_type,
            "phase_id": self.phase_id,
            "action_type": self.action_type,
            "outcome_status": self.outcome_status,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CostEstimate(db.Model):
    """Resource-metered estimate using the official direct cost x 2.5 formula."""

    __tablename__ = "cost_estimate"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    estimated_direct_cost = db.Column(db.Float, nullable=False, default=0.0)
    estimated_billed_price = db.Column(db.Float, nullable=False, default=0.0)
    actual_direct_cost = db.Column(db.Float, nullable=True)
    actual_billed_price = db.Column(db.Float, nullable=True)
    pricing_multiplier = db.Column(db.Float, nullable=False, default=2.5)
    pricing_basis = db.Column(db.String(160), nullable=False, default="actual_direct_platform_cost_x_2_5")
    currency = db.Column(db.String(8), nullable=False, default="EUR")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "action_id": self.action_id,
            "estimated_direct_cost": self.estimated_direct_cost,
            "estimated_billed_price": self.estimated_billed_price,
            "actual_direct_cost": self.actual_direct_cost,
            "actual_billed_price": self.actual_billed_price,
            "pricing_multiplier": self.pricing_multiplier,
            "pricing_basis": self.pricing_basis,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SpendingCap(db.Model):
    """User/venture spending cap for metered actions."""

    __tablename__ = "spending_cap"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    cap_type = db.Column(db.String(40), nullable=False, default="per_action")
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), nullable=False, default="EUR")
    requires_approval_above_amount = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "cap_type": self.cap_type,
            "amount": self.amount,
            "currency": self.currency,
            "requires_approval_above_amount": self.requires_approval_above_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProfessionalReviewRequirement(db.Model):
    """Tracks required professional review before high-stakes actions."""

    __tablename__ = "professional_review_requirement"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    category = db.Column(db.String(80), nullable=False)
    trigger_reason = db.Column(db.Text, nullable=False)
    required_before_action_type = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="required")
    professional_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "category": self.category,
            "trigger_reason": self.trigger_reason,
            "required_before_action_type": self.required_before_action_type,
            "status": self.status,
            "professional_notes": self.professional_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VentureConnectionMode(db.Model):
    """Manual / partially connected / fully connected execution mode."""

    __tablename__ = "venture_connection_mode"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    connection_mode = db.Column(db.String(40), nullable=False, default="manual_mode")
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "connection_mode": self.connection_mode,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
