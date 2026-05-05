"""Additional MVP logic models derived from the Changepreneurship requirements.

These models extend the first MVP infrastructure pass without replacing it. They
turn document requirements into structured backend records that can be used by
routing, blockers, action approvals, evidence checks, billing, analytics, and
five-year commercial/impact measurement.

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


class MeaningfulActivityEvent(db.Model, JsonTextMixin):
    """Strict WAU event: only meaningful venture-building activity counts.

    Passive dashboard views and abandoned sessions should not be stored here.
    """

    __tablename__ = "meaningful_activity_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    activity_type = db.Column(db.String(100), nullable=False)
    source_object_type = db.Column(db.String(80), nullable=True)
    source_object_id = db.Column(db.Integer, nullable=True)
    impact_category = db.Column(db.String(80), nullable=False, default="venture_progress")
    qualifies_for_wau = db.Column(db.Boolean, nullable=False, default=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    MEANINGFUL_TYPES = {
        "assessment_answered",
        "assessment_revised",
        "validation_task_completed",
        "evidence_uploaded_or_connected",
        "business_component_reviewed",
        "business_component_approved",
        "market_research_step_completed",
        "outreach_task_completed",
        "mentor_task_completed",
        "customer_task_completed",
        "stakeholder_task_completed",
        "readiness_data_updated",
        "venture_component_approved",
        "real_world_task_reported",
        "blocker_reviewed_and_route_chosen",
        "next_action_approved",
        "account_connected_for_context",
        "business_model_updated",
        "validation_result_updated",
        "operating_assumption_updated",
        "progress_pause_pivot_or_closure_reported",
    }

    NON_MEANINGFUL_TYPES = {
        "login_only",
        "dashboard_view",
        "passive_reading",
        "click_without_progress",
        "old_output_viewed",
        "abandoned_session",
        "accidental_visit",
    }

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "activity_type": self.activity_type,
            "source_object_type": self.source_object_type,
            "source_object_id": self.source_object_id,
            "impact_category": self.impact_category,
            "qualifies_for_wau": self.qualifies_for_wau,
            "metadata": self.get_metadata(),
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
        }


class ReadinessImpactSnapshot(db.Model, JsonTextMixin):
    """Snapshot for measuring whether users become better-prepared entrepreneurs."""

    __tablename__ = "readiness_impact_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    snapshot_type = db.Column(db.String(40), nullable=False, default="periodic")
    financial_runway_score = db.Column(db.Float, nullable=False, default=0.0)
    time_capacity_score = db.Column(db.Float, nullable=False, default=0.0)
    idea_clarity_score = db.Column(db.Float, nullable=False, default=0.0)
    market_evidence_score = db.Column(db.Float, nullable=False, default=0.0)
    business_model_score = db.Column(db.Float, nullable=False, default=0.0)
    real_world_execution_score = db.Column(db.Float, nullable=False, default=0.0)
    risk_reduction_score = db.Column(db.Float, nullable=False, default=0.0)
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    improved_indicators_json = db.Column(db.Text, nullable=False, default="[]")
    better_prepared = db.Column(db.Boolean, nullable=False, default=False)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def set_improved_indicators(self, indicators: list) -> None:
        self.improved_indicators_json = self._dumps(indicators)

    def get_improved_indicators(self) -> list:
        return self._loads(self.improved_indicators_json, fallback=[])

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "snapshot_type": self.snapshot_type,
            "financial_runway_score": self.financial_runway_score,
            "time_capacity_score": self.time_capacity_score,
            "idea_clarity_score": self.idea_clarity_score,
            "market_evidence_score": self.market_evidence_score,
            "business_model_score": self.business_model_score,
            "real_world_execution_score": self.real_world_execution_score,
            "risk_reduction_score": self.risk_reduction_score,
            "overall_score": self.overall_score,
            "improved_indicators": self.get_improved_indicators(),
            "better_prepared": self.better_prepared,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CommercialMetricSnapshot(db.Model, JsonTextMixin):
    """Monthly commercial sustainability metrics.

    Revenue target is metered repeatable revenue, not unlimited subscription MRR.
    """

    __tablename__ = "commercial_metric_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    period_start = db.Column(db.DateTime, nullable=False, index=True)
    period_end = db.Column(db.DateTime, nullable=False, index=True)
    monthly_repeatable_metered_revenue = db.Column(db.Float, nullable=False, default=0.0)
    annualized_repeatable_revenue = db.Column(db.Float, nullable=False, default=0.0)
    direct_platform_cost = db.Column(db.Float, nullable=False, default=0.0)
    variable_gross_margin_percent = db.Column(db.Float, nullable=False, default=0.0)
    monthly_logo_churn_percent = db.Column(db.Float, nullable=True)
    net_revenue_retention_percent = db.Column(db.Float, nullable=True)
    cac_payback_months = db.Column(db.Float, nullable=True)
    ltv_cac_ratio = db.Column(db.Float, nullable=True)
    operating_runway_months = db.Column(db.Float, nullable=True)
    largest_customer_revenue_share_percent = db.Column(db.Float, nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "monthly_repeatable_metered_revenue": self.monthly_repeatable_metered_revenue,
            "annualized_repeatable_revenue": self.annualized_repeatable_revenue,
            "direct_platform_cost": self.direct_platform_cost,
            "variable_gross_margin_percent": self.variable_gross_margin_percent,
            "monthly_logo_churn_percent": self.monthly_logo_churn_percent,
            "net_revenue_retention_percent": self.net_revenue_retention_percent,
            "cac_payback_months": self.cac_payback_months,
            "ltv_cac_ratio": self.ltv_cac_ratio,
            "operating_runway_months": self.operating_runway_months,
            "largest_customer_revenue_share_percent": self.largest_customer_revenue_share_percent,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ImpactMetricSnapshot(db.Model, JsonTextMixin):
    """Monthly impact metrics with strict meaningful-activity definitions."""

    __tablename__ = "impact_metric_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    period_start = db.Column(db.DateTime, nullable=False, index=True)
    period_end = db.Column(db.DateTime, nullable=False, index=True)
    weekly_active_users = db.Column(db.Integer, nullable=False, default=0)
    phase_1_completion_rate = db.Column(db.Float, nullable=True)
    phase_2_completion_rate = db.Column(db.Float, nullable=True)
    phase_3_completion_rate = db.Column(db.Float, nullable=True)
    phase_4_completion_rate = db.Column(db.Float, nullable=True)
    real_world_validation_completion_rate = db.Column(db.Float, nullable=True)
    platform_hard_blocker_enforcement_rate = db.Column(db.Float, nullable=True)
    external_hard_blocker_compliance_rate = db.Column(db.Float, nullable=True)
    average_readiness_improvement_percent_90d = db.Column(db.Float, nullable=True)
    time_to_first_value_15min_rate = db.Column(db.Float, nullable=True)
    venture_continuation_12mo_reporting_rate = db.Column(db.Float, nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "weekly_active_users": self.weekly_active_users,
            "phase_1_completion_rate": self.phase_1_completion_rate,
            "phase_2_completion_rate": self.phase_2_completion_rate,
            "phase_3_completion_rate": self.phase_3_completion_rate,
            "phase_4_completion_rate": self.phase_4_completion_rate,
            "real_world_validation_completion_rate": self.real_world_validation_completion_rate,
            "platform_hard_blocker_enforcement_rate": self.platform_hard_blocker_enforcement_rate,
            "external_hard_blocker_compliance_rate": self.external_hard_blocker_compliance_rate,
            "average_readiness_improvement_percent_90d": self.average_readiness_improvement_percent_90d,
            "time_to_first_value_15min_rate": self.time_to_first_value_15min_rate,
            "venture_continuation_12mo_reporting_rate": self.venture_continuation_12mo_reporting_rate,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CommercialImpactGuardrailEvent(db.Model, JsonTextMixin):
    """Records cases where the AI/product must balance revenue and user safety.

    This turns rules like 'do not monetize confusion' and 'do not push paid work
    before readiness' into auditable records.
    """

    __tablename__ = "commercial_impact_guardrail_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    guardrail_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(40), nullable=False, default="warning")
    message = db.Column(db.Text, nullable=False)
    paid_action_allowed = db.Column(db.Boolean, nullable=False, default=False)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "action_id": self.action_id,
            "guardrail_type": self.guardrail_type,
            "severity": self.severity,
            "message": self.message,
            "paid_action_allowed": self.paid_action_allowed,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
