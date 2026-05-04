"""Commercial and impact metrics for the Changepreneurship MVP.

These models translate the five-year success definition into measurable data:

- repeatable metered revenue, not vague MRR;
- strict weekly active users based on meaningful venture-building actions;
- readiness improvement snapshots;
- platform vs external hard-blocker tracking.
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


class MeteredRevenueEvent(db.Model, JsonTextMixin):
    """Revenue event using actual direct platform cost x 2.5 pricing."""

    __tablename__ = "metered_revenue_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    revenue_category = db.Column(db.String(80), nullable=False, default="metered_individual_usage")
    payer_type = db.Column(db.String(80), nullable=False, default="individual")
    payer_reference = db.Column(db.String(160), nullable=True)
    actual_direct_cost = db.Column(db.Float, nullable=False, default=0.0)
    billed_price = db.Column(db.Float, nullable=False, default=0.0)
    pricing_multiplier = db.Column(db.Float, nullable=False, default=2.5)
    currency = db.Column(db.String(8), nullable=False, default="EUR")
    repeatable_platform_revenue = db.Column(db.Boolean, nullable=False, default=True)
    should_count_toward_metered_mrr = db.Column(db.Boolean, nullable=False, default=True)
    excluded_reason = db.Column(db.Text, nullable=True)
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
            "revenue_category": self.revenue_category,
            "payer_type": self.payer_type,
            "payer_reference": self.payer_reference,
            "actual_direct_cost": self.actual_direct_cost,
            "billed_price": self.billed_price,
            "pricing_multiplier": self.pricing_multiplier,
            "currency": self.currency,
            "repeatable_platform_revenue": self.repeatable_platform_revenue,
            "should_count_toward_metered_mrr": self.should_count_toward_metered_mrr,
            "excluded_reason": self.excluded_reason,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MeaningfulActivityEvent(db.Model, JsonTextMixin):
    """Strict WAU activity event.

    Logins, dashboard opens, passive reading, accidental visits, and pure browsing
    should not be recorded here unless the event moved readiness, evidence,
    venture structure, a decision, or real-world execution forward.
    """

    __tablename__ = "meaningful_activity_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    activity_type = db.Column(db.String(100), nullable=False)
    qualifies_for_wau = db.Column(db.Boolean, nullable=False, default=True)
    impact_category = db.Column(db.String(80), nullable=False, default="venture_progress")
    description = db.Column(db.Text, nullable=True)
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
            "activity_type": self.activity_type,
            "qualifies_for_wau": self.qualifies_for_wau,
            "impact_category": self.impact_category,
            "description": self.description,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReadinessSnapshot(db.Model, JsonTextMixin):
    """Point-in-time readiness measurement for improvement tracking."""

    __tablename__ = "readiness_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    aggregate_score = db.Column(db.Float, nullable=False, default=0.0)
    financial_readiness_score = db.Column(db.Float, nullable=False, default=0.0)
    time_capacity_score = db.Column(db.Float, nullable=False, default=0.0)
    idea_clarity_score = db.Column(db.Float, nullable=False, default=0.0)
    market_evidence_score = db.Column(db.Float, nullable=False, default=0.0)
    business_model_score = db.Column(db.Float, nullable=False, default=0.0)
    execution_score = db.Column(db.Float, nullable=False, default=0.0)
    risk_reduction_score = db.Column(db.Float, nullable=False, default=0.0)
    source = db.Column(db.String(80), nullable=False, default="readiness_profile")
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
            "aggregate_score": self.aggregate_score,
            "financial_readiness_score": self.financial_readiness_score,
            "time_capacity_score": self.time_capacity_score,
            "idea_clarity_score": self.idea_clarity_score,
            "market_evidence_score": self.market_evidence_score,
            "business_model_score": self.business_model_score,
            "execution_score": self.execution_score,
            "risk_reduction_score": self.risk_reduction_score,
            "source": self.source,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class HardBlockerEvent(db.Model, JsonTextMixin):
    """Tracks platform-controlled and external hard-blocker behaviour separately."""

    __tablename__ = "hard_blocker_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=True, index=True)
    blocker_type = db.Column(db.String(100), nullable=False)
    blocked_action = db.Column(db.String(160), nullable=False)
    platform_controlled = db.Column(db.Boolean, nullable=False, default=True)
    enforcement_status = db.Column(db.String(80), nullable=False, default="warning_shown")
    risk_explanation = db.Column(db.Text, nullable=True)
    unlock_condition = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

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
            "blocker_type": self.blocker_type,
            "blocked_action": self.blocked_action,
            "platform_controlled": self.platform_controlled,
            "enforcement_status": self.enforcement_status,
            "risk_explanation": self.risk_explanation,
            "unlock_condition": self.unlock_condition,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class SuccessMetricSnapshot(db.Model, JsonTextMixin):
    """Stored aggregate metric snapshot for management/investor reporting."""

    __tablename__ = "success_metric_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    monthly_repeatable_metered_revenue = db.Column(db.Float, nullable=False, default=0.0)
    annualized_repeatable_revenue = db.Column(db.Float, nullable=False, default=0.0)
    variable_gross_margin = db.Column(db.Float, nullable=False, default=0.0)
    strict_weekly_active_users = db.Column(db.Integer, nullable=False, default=0)
    meaningful_activity_count = db.Column(db.Integer, nullable=False, default=0)
    platform_hard_blocker_enforcement_rate = db.Column(db.Float, nullable=False, default=0.0)
    external_hard_blocker_compliance_rate = db.Column(db.Float, nullable=False, default=0.0)
    readiness_improvement_rate = db.Column(db.Float, nullable=False, default=0.0)
    target_progress_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def set_target_progress(self, payload: Dict[str, Any]) -> None:
        self.target_progress_json = self._dumps(payload)

    def get_target_progress(self) -> Dict[str, Any]:
        return self._loads(self.target_progress_json)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "monthly_repeatable_metered_revenue": self.monthly_repeatable_metered_revenue,
            "annualized_repeatable_revenue": self.annualized_repeatable_revenue,
            "variable_gross_margin": self.variable_gross_margin,
            "strict_weekly_active_users": self.strict_weekly_active_users,
            "meaningful_activity_count": self.meaningful_activity_count,
            "platform_hard_blocker_enforcement_rate": self.platform_hard_blocker_enforcement_rate,
            "external_hard_blocker_compliance_rate": self.external_hard_blocker_compliance_rate,
            "readiness_improvement_rate": self.readiness_improvement_rate,
            "target_progress": self.get_target_progress(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
