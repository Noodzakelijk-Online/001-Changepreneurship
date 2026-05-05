"""Commercial sustainability and user-impact metric services.

This module turns the five-year outcome text into enforceable measurement logic:

- repeatable metered revenue, not vague MRR;
- strict weekly active user counting based only on meaningful actions;
- readiness-improvement snapshots;
- platform hard-blocker enforcement vs external compliance;
- commercial/impact guardrails so paid work is not pushed when unsafe.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func

from src.models.assessment import db
from src.models.mvp_infrastructure import FounderReadinessProfile, PhaseGate, UserAction
from src.models.mvp_logic import (
    CommercialImpactGuardrailEvent,
    CommercialMetricSnapshot,
    CostEstimate,
    ImpactMetricSnapshot,
    MeaningfulActivityEvent,
    ReadinessImpactSnapshot,
)


COMMERCIAL_TARGETS = {
    "monthly_repeatable_metered_revenue": 500_000,
    "annualized_repeatable_revenue": 6_000_000,
    "pricing_multiplier": 2.5,
    "baseline_variable_gross_margin_percent": 60,
    "long_term_gross_margin_target_min_percent": 65,
    "monthly_logo_churn_max_percent": 4,
    "net_revenue_retention_min_percent": 100,
    "cac_payback_max_months": 12,
    "ltv_cac_min_ratio": 3,
    "operating_runway_min_months": 12,
    "largest_customer_revenue_share_max_percent": 15,
}


IMPACT_TARGETS = {
    "weekly_active_users": 100_000,
    "phase_1_completion_rate_min_percent": 65,
    "phase_2_completion_rate_min_percent": 50,
    "phase_3_completion_rate_min_percent": 35,
    "phase_4_completion_rate_min_percent": 25,
    "real_world_validation_completion_rate_min_percent": 40,
    "platform_hard_blocker_enforcement_rate_percent": 100,
    "external_hard_blocker_compliance_rate_min_percent": 80,
    "readiness_improvement_90d_min_percent": 25,
    "time_to_first_value_15min_min_percent": 80,
    "venture_continuation_12mo_reporting_min_percent": 70,
}


class MeaningfulActivityService:
    """Records only meaningful venture-building activity for strict WAU counting."""

    def record(
        self,
        *,
        user_id: int,
        activity_type: str,
        venture_id: Optional[int] = None,
        source_object_type: Optional[str] = None,
        source_object_id: Optional[int] = None,
        impact_category: str = "venture_progress",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeaningfulActivityEvent:
        qualifies = activity_type in MeaningfulActivityEvent.MEANINGFUL_TYPES
        if activity_type in MeaningfulActivityEvent.NON_MEANINGFUL_TYPES:
            qualifies = False
        event = MeaningfulActivityEvent(
            user_id=user_id,
            venture_id=venture_id,
            activity_type=activity_type,
            source_object_type=source_object_type,
            source_object_id=source_object_id,
            impact_category=impact_category,
            qualifies_for_wau=qualifies,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def weekly_active_users(self, *, since: Optional[datetime] = None, until: Optional[datetime] = None) -> int:
        until = until or datetime.utcnow()
        since = since or (until - timedelta(days=7))
        return (
            db.session.query(func.count(func.distinct(MeaningfulActivityEvent.user_id)))
            .filter(MeaningfulActivityEvent.qualifies_for_wau.is_(True))
            .filter(MeaningfulActivityEvent.occurred_at >= since)
            .filter(MeaningfulActivityEvent.occurred_at < until)
            .scalar()
            or 0
        )


class ReadinessImpactService:
    """Measures whether a user becomes a better-prepared entrepreneur."""

    INDICATORS = [
        "financial_runway_score",
        "time_capacity_score",
        "idea_clarity_score",
        "market_evidence_score",
        "business_model_score",
        "real_world_execution_score",
        "risk_reduction_score",
    ]

    def create_snapshot_from_profile(
        self,
        *,
        profile: FounderReadinessProfile,
        snapshot_type: str = "periodic",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReadinessImpactSnapshot:
        scores = self._scores_from_profile(profile)
        overall = round(sum(scores.values()) / len(scores), 2)
        previous = (
            ReadinessImpactSnapshot.query
            .filter_by(user_id=profile.user_id, venture_id=profile.venture_id)
            .order_by(ReadinessImpactSnapshot.created_at.desc())
            .first()
        )
        improved = []
        if previous:
            for field, score in scores.items():
                if score > getattr(previous, field):
                    improved.append(field)
        better_prepared = len(improved) >= 4

        snapshot = ReadinessImpactSnapshot(
            user_id=profile.user_id,
            venture_id=profile.venture_id,
            snapshot_type=snapshot_type,
            overall_score=overall,
            better_prepared=better_prepared,
            **scores,
        )
        snapshot.set_improved_indicators(improved)
        snapshot.set_metadata(metadata or {})
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def _scores_from_profile(self, profile: FounderReadinessProfile) -> Dict[str, float]:
        return {
            "financial_runway_score": self._dimension_score(profile, "financial_readiness"),
            "time_capacity_score": self._dimension_score(profile, "time_capacity"),
            "idea_clarity_score": self._dimension_score(profile, "founder_idea_fit"),
            "market_evidence_score": self._dimension_score(profile, "evidence_discipline"),
            "business_model_score": self._dimension_score(profile, "operational_discipline"),
            "real_world_execution_score": self._dimension_score(profile, "execution_behaviour"),
            "risk_reduction_score": self._dimension_score(profile, "risk_awareness"),
        }

    def _dimension_score(self, profile: FounderReadinessProfile, dimension: str) -> float:
        status = profile.get_dimension(dimension).get("status", "unknown")
        return {
            "critical": 0,
            "weak": 35,
            "unknown": 45,
            "adequate": 70,
            "strong": 90,
        }.get(status, 45)


class CommercialMetricService:
    """Computes and stores metered revenue snapshots."""

    def create_snapshot(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        monthly_logo_churn_percent: Optional[float] = None,
        net_revenue_retention_percent: Optional[float] = None,
        cac_payback_months: Optional[float] = None,
        ltv_cac_ratio: Optional[float] = None,
        operating_runway_months: Optional[float] = None,
        largest_customer_revenue_share_percent: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CommercialMetricSnapshot:
        billed = (
            db.session.query(func.coalesce(func.sum(CostEstimate.actual_billed_price), 0.0))
            .filter(CostEstimate.updated_at >= period_start)
            .filter(CostEstimate.updated_at < period_end)
            .scalar()
            or 0.0
        )
        estimated_billed = (
            db.session.query(func.coalesce(func.sum(CostEstimate.estimated_billed_price), 0.0))
            .filter(CostEstimate.created_at >= period_start)
            .filter(CostEstimate.created_at < period_end)
            .scalar()
            or 0.0
        )
        revenue = billed or estimated_billed
        direct_cost = (
            db.session.query(func.coalesce(func.sum(CostEstimate.actual_direct_cost), 0.0))
            .filter(CostEstimate.updated_at >= period_start)
            .filter(CostEstimate.updated_at < period_end)
            .scalar()
            or 0.0
        )
        if not direct_cost:
            direct_cost = revenue / COMMERCIAL_TARGETS["pricing_multiplier"] if revenue else 0.0
        margin = round(((revenue - direct_cost) / revenue) * 100, 2) if revenue else 0.0
        snapshot = CommercialMetricSnapshot(
            period_start=period_start,
            period_end=period_end,
            monthly_repeatable_metered_revenue=round(revenue, 2),
            annualized_repeatable_revenue=round(revenue * 12, 2),
            direct_platform_cost=round(direct_cost, 2),
            variable_gross_margin_percent=margin,
            monthly_logo_churn_percent=monthly_logo_churn_percent,
            net_revenue_retention_percent=net_revenue_retention_percent,
            cac_payback_months=cac_payback_months,
            ltv_cac_ratio=ltv_cac_ratio,
            operating_runway_months=operating_runway_months,
            largest_customer_revenue_share_percent=largest_customer_revenue_share_percent,
        )
        snapshot.set_metadata(metadata or {"targets": COMMERCIAL_TARGETS})
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def target_report(self, snapshot: CommercialMetricSnapshot) -> Dict[str, Any]:
        return {
            "commercially_sustainable": snapshot.monthly_repeatable_metered_revenue >= COMMERCIAL_TARGETS["monthly_repeatable_metered_revenue"],
            "checks": {
                "monthly_repeatable_metered_revenue": snapshot.monthly_repeatable_metered_revenue >= COMMERCIAL_TARGETS["monthly_repeatable_metered_revenue"],
                "annualized_repeatable_revenue": snapshot.annualized_repeatable_revenue >= COMMERCIAL_TARGETS["annualized_repeatable_revenue"],
                "variable_gross_margin_baseline": snapshot.variable_gross_margin_percent >= COMMERCIAL_TARGETS["baseline_variable_gross_margin_percent"],
                "monthly_logo_churn": snapshot.monthly_logo_churn_percent is None or snapshot.monthly_logo_churn_percent <= COMMERCIAL_TARGETS["monthly_logo_churn_max_percent"],
                "net_revenue_retention": snapshot.net_revenue_retention_percent is None or snapshot.net_revenue_retention_percent >= COMMERCIAL_TARGETS["net_revenue_retention_min_percent"],
                "cac_payback": snapshot.cac_payback_months is None or snapshot.cac_payback_months <= COMMERCIAL_TARGETS["cac_payback_max_months"],
                "ltv_cac": snapshot.ltv_cac_ratio is None or snapshot.ltv_cac_ratio >= COMMERCIAL_TARGETS["ltv_cac_min_ratio"],
                "operating_runway": snapshot.operating_runway_months is None or snapshot.operating_runway_months >= COMMERCIAL_TARGETS["operating_runway_min_months"],
                "revenue_concentration": snapshot.largest_customer_revenue_share_percent is None or snapshot.largest_customer_revenue_share_percent <= COMMERCIAL_TARGETS["largest_customer_revenue_share_max_percent"],
            },
        }


class ImpactMetricService:
    """Computes strict impact snapshots."""

    def create_snapshot(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        phase_1_completion_rate: Optional[float] = None,
        phase_2_completion_rate: Optional[float] = None,
        phase_3_completion_rate: Optional[float] = None,
        phase_4_completion_rate: Optional[float] = None,
        real_world_validation_completion_rate: Optional[float] = None,
        platform_hard_blocker_enforcement_rate: Optional[float] = None,
        external_hard_blocker_compliance_rate: Optional[float] = None,
        average_readiness_improvement_percent_90d: Optional[float] = None,
        time_to_first_value_15min_rate: Optional[float] = None,
        venture_continuation_12mo_reporting_rate: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ImpactMetricSnapshot:
        wau = MeaningfulActivityService().weekly_active_users(since=period_start, until=period_end)
        snapshot = ImpactMetricSnapshot(
            period_start=period_start,
            period_end=period_end,
            weekly_active_users=wau,
            phase_1_completion_rate=phase_1_completion_rate,
            phase_2_completion_rate=phase_2_completion_rate,
            phase_3_completion_rate=phase_3_completion_rate,
            phase_4_completion_rate=phase_4_completion_rate,
            real_world_validation_completion_rate=real_world_validation_completion_rate,
            platform_hard_blocker_enforcement_rate=platform_hard_blocker_enforcement_rate,
            external_hard_blocker_compliance_rate=external_hard_blocker_compliance_rate,
            average_readiness_improvement_percent_90d=average_readiness_improvement_percent_90d,
            time_to_first_value_15min_rate=time_to_first_value_15min_rate,
            venture_continuation_12mo_reporting_rate=venture_continuation_12mo_reporting_rate,
        )
        snapshot.set_metadata(metadata or {"targets": IMPACT_TARGETS})
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def target_report(self, snapshot: ImpactMetricSnapshot) -> Dict[str, Any]:
        return {
            "impact_target_met": snapshot.weekly_active_users >= IMPACT_TARGETS["weekly_active_users"],
            "checks": {
                "weekly_active_users": snapshot.weekly_active_users >= IMPACT_TARGETS["weekly_active_users"],
                "phase_1_completion": snapshot.phase_1_completion_rate is None or snapshot.phase_1_completion_rate >= IMPACT_TARGETS["phase_1_completion_rate_min_percent"],
                "phase_2_completion": snapshot.phase_2_completion_rate is None or snapshot.phase_2_completion_rate >= IMPACT_TARGETS["phase_2_completion_rate_min_percent"],
                "phase_3_completion": snapshot.phase_3_completion_rate is None or snapshot.phase_3_completion_rate >= IMPACT_TARGETS["phase_3_completion_rate_min_percent"],
                "phase_4_completion": snapshot.phase_4_completion_rate is None or snapshot.phase_4_completion_rate >= IMPACT_TARGETS["phase_4_completion_rate_min_percent"],
                "real_world_validation": snapshot.real_world_validation_completion_rate is None or snapshot.real_world_validation_completion_rate >= IMPACT_TARGETS["real_world_validation_completion_rate_min_percent"],
                "platform_hard_blocker_enforcement": snapshot.platform_hard_blocker_enforcement_rate is None or snapshot.platform_hard_blocker_enforcement_rate >= IMPACT_TARGETS["platform_hard_blocker_enforcement_rate_percent"],
                "external_hard_blocker_compliance": snapshot.external_hard_blocker_compliance_rate is None or snapshot.external_hard_blocker_compliance_rate >= IMPACT_TARGETS["external_hard_blocker_compliance_rate_min_percent"],
                "readiness_improvement_90d": snapshot.average_readiness_improvement_percent_90d is None or snapshot.average_readiness_improvement_percent_90d >= IMPACT_TARGETS["readiness_improvement_90d_min_percent"],
                "time_to_first_value": snapshot.time_to_first_value_15min_rate is None or snapshot.time_to_first_value_15min_rate >= IMPACT_TARGETS["time_to_first_value_15min_min_percent"],
                "venture_continuation_reporting": snapshot.venture_continuation_12mo_reporting_rate is None or snapshot.venture_continuation_12mo_reporting_rate >= IMPACT_TARGETS["venture_continuation_12mo_reporting_min_percent"],
            },
        }


class CommercialImpactGuardrailService:
    """Prevents commercial incentives from overriding user-impact/safety logic."""

    GUARDRAIL_RULES = {
        "do_not_monetize_confusion": "Do not offer paid work when the user mainly needs clarification.",
        "do_not_monetize_desperation_aggressively": "Do not push paid action during financial/personal crisis.",
        "do_not_push_paid_actions_before_readiness": "Do not recommend paid execution before readiness allows it.",
        "do_not_treat_excitement_as_evidence": "Enthusiasm is not validation evidence.",
        "do_not_count_passive_logins_as_impact": "Passive sessions do not count as weekly active usage.",
        "do_not_count_polished_documents_without_evidence": "Documents count as progress only when underlying evidence improves.",
        "do_count_responsible_pause_or_pivot": "A pause, pivot, or stopped action can be a positive impact outcome.",
    }

    def evaluate_paid_action(
        self,
        *,
        user_id: int,
        venture_id: Optional[int],
        action_id: Optional[int],
        profile: Optional[FounderReadinessProfile],
        action_type: Optional[str],
        estimated_billed_price: float = 0.0,
    ) -> Dict[str, Any]:
        violations = []
        if profile:
            if profile.survival_risk_indicator in {"high", "critical"}:
                violations.append("do_not_monetize_desperation_aggressively")
            if profile.next_step_eligibility in {"stabilization_required", "needs_more_diagnosis"} and estimated_billed_price > 0:
                violations.append("do_not_push_paid_actions_before_readiness")
            if profile.routing_state in {"clarify_idea", "needs_diagnosis"} and estimated_billed_price > 0:
                violations.append("do_not_monetize_confusion")
        hard_gate = PhaseGate.query.filter_by(user_id=user_id, venture_id=venture_id).filter(PhaseGate.gate_status.in_(["hard_blocked", "hard_stop"])).first()
        if hard_gate and estimated_billed_price > 0:
            violations.append("do_not_push_paid_actions_before_readiness")

        allowed = len(violations) == 0
        event = CommercialImpactGuardrailEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            guardrail_type="paid_action_evaluation",
            severity="block" if not allowed else "info",
            message="Paid action allowed." if allowed else "Paid action blocked by commercial-impact guardrail.",
            paid_action_allowed=allowed,
        )
        event.set_metadata({
            "action_type": action_type,
            "estimated_billed_price": estimated_billed_price,
            "violations": violations,
            "rules": {key: self.GUARDRAIL_RULES[key] for key in violations},
        })
        db.session.add(event)
        db.session.commit()
        return {"allowed": allowed, "violations": violations, "event": event.to_dict()}
