"""Commercial sustainability and user-impact metric models.

These models turn the five-year success text into measurable platform behaviour.
They intentionally separate vanity activity from meaningful venture-building work.
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


class MeaningfulActivityEvent(db.Model, JsonTextMixin):
    """A strict activity event that may count toward WAU only if meaningful."""

    __tablename__ = "meaningful_activity_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    activity_type = db.Column(db.String(100), nullable=False)
    is_meaningful = db.Column(db.Boolean, nullable=False, default=False)
    impact_category = db.Column(db.String(100), nullable=True)
    source = db.Column(db.String(100), nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    MEANINGFUL_TYPES = {
        "assessment_answered",
        "assessment_revised",
        "validation_task_completed",
        "evidence_uploaded",
        "evidence_connected",
        "business_component_reviewed",
        "business_component_approved",
        "market_research_step_completed",
        "outreach_task_completed",
        "mentor_task_completed",
        "customer_task_completed",
        "stakeholder_task_completed",
        "readiness_updated",
        "financial_runway_updated",
        "availability_updated",
        "venture_component_approved",
        "real_world_task_reported",
        "blocker_reviewed_safe_route_chosen",
        "next_action_approved",
        "account_connected_context_improved",
        "business_model_updated",
        "validation_result_updated",
        "operating_assumption_updated",
        "progress_status_reported",
        "pause_pivot_closure_continuation_reported",
        "action_outcome_recorded",
    }

    VANITY_TYPES = {
        "login_only",
        "dashboard_opened",
        "passive_read",
        "click_without_progress",
        "old_output_viewed",
        "passive_browsing",
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
            "is_meaningful": self.is_meaningful,
            "impact_category": self.impact_category,
            "source": self.source,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MeteredRevenueEvent(db.Model, JsonTextMixin):
    """Revenue event based on direct platform cost x pricing multiplier."""

    __tablename__ = "metered_revenue_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    payer_type = db.Column(db.String(60), nullable=False, default="individual")
    revenue_category = db.Column(db.String(80), nullable=False, default="metered_individual_usage")
    direct_platform_cost = db.Column(db.Float, nullable=False, default=0.0)
    billed_amount = db.Column(db.Float, nullable=False, default=0.0)
    pricing_multiplier = db.Column(db.Float, nullable=False, default=2.5)
    currency = db.Column(db.String(8), nullable=False, default="EUR")
    is_repeatable_platform_revenue = db.Column(db.Boolean, nullable=False, default=True)
    is_excluded_from_core_target = db.Column(db.Boolean, nullable=False, default=False)
    exclusion_reason = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    REPEATABLE_CATEGORIES = {
        "metered_individual_usage",
        "prepaid_usage_consumption",
        "institutional_usage_pool",
        "sponsored_access_usage",
        "organization_level_usage",
        "monthly_invoiced_usage",
        "capped_usage_bundle_consumption",
    }

    EXCLUDED_CATEGORIES = {
        "one_time_consulting_fee",
        "one_off_custom_project",
        "non_repeatable_grant",
        "irregular_implementation_fee",
        "manual_agency_work_outside_product",
        "one_time_setup_fee",
        "non_recurring_development_work",
        "unrelated_service_revenue",
        "exceptional_non_platform_partnership_income",
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
            "action_id": self.action_id,
            "payer_type": self.payer_type,
            "revenue_category": self.revenue_category,
            "direct_platform_cost": self.direct_platform_cost,
            "billed_amount": self.billed_amount,
            "pricing_multiplier": self.pricing_multiplier,
            "currency": self.currency,
            "is_repeatable_platform_revenue": self.is_repeatable_platform_revenue,
            "is_excluded_from_core_target": self.is_excluded_from_core_target,
            "exclusion_reason": self.exclusion_reason,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReadinessSnapshot(db.Model, JsonTextMixin):
    """Point-in-time readiness measurement for impact improvement tracking."""

    __tablename__ = "readiness_snapshot"

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
    source = db.Column(db.String(100), nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    INDICATORS = [
        "financial_runway_score",
        "time_capacity_score",
        "idea_clarity_score",
        "market_evidence_score",
        "business_model_score",
        "real_world_execution_score",
        "risk_reduction_score",
    ]

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
            "source": self.source,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class HardBlockerMetric(db.Model, JsonTextMixin):
    """Separates platform-controlled enforcement from external user compliance."""

    __tablename__ = "hard_blocker_metric"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    blocker_type = db.Column(db.String(100), nullable=False)
    controlled_by_platform = db.Column(db.Boolean, nullable=False, default=True)
    blocked_action_type = db.Column(db.String(100), nullable=False)
    enforcement_status = db.Column(db.String(60), nullable=False, default="blocked")
    user_reported_external_proceeded = db.Column(db.Boolean, nullable=True)
    risk_period_days = db.Column(db.Integer, nullable=False, default=30)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_metadata(self, payload: Dict[str, Any]) -> None:
        self.metadata_json = self._dumps(payload)

    def get_metadata(self) -> Dict[str, Any]:
        return self._loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "blocker_type": self.blocker_type,
            "controlled_by_platform": self.controlled_by_platform,
            "blocked_action_type": self.blocked_action_type,
            "enforcement_status": self.enforcement_status,
            "user_reported_external_proceeded": self.user_reported_external_proceeded,
            "risk_period_days": self.risk_period_days,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VentureContinuationStatus(db.Model, JsonTextMixin):
    """12-month continuation, pause, pivot, closure, or responsible stop tracking."""

    __tablename__ = "venture_continuation_status"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    status = db.Column(db.String(60), nullable=False)
    report_period_month = db.Column(db.Integer, nullable=False, default=12)
    report_summary = db.Column(db.Text, nullable=True)
    responsible_outcome = db.Column(db.Boolean, nullable=False, default=False)
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
            "status": self.status,
            "report_period_month": self.report_period_month,
            "report_summary": self.report_summary,
            "responsible_outcome": self.responsible_outcome,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
