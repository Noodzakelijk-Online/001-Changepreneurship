"""Commercial sustainability and user-impact metric services.

This service translates the five-year success text into measurable behaviour:

- monthly repeatable metered revenue, not classic unlimited SaaS MRR;
- meaningful weekly active users, not passive logins;
- readiness improvement based on 4 of 7 indicators;
- platform hard-blocker enforcement and external blocker compliance;
- commercial/impact balance rules.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func

from src.models.assessment import db
from src.models.mvp_metrics import (
    HardBlockerMetric,
    MeaningfulActivityEvent,
    MeteredRevenueEvent,
    ReadinessSnapshot,
    VentureContinuationStatus,
)


COMMERCIAL_TARGETS = {
    "monthly_repeatable_metered_revenue_eur": 500_000,
    "annualized_repeatable_revenue_eur": 6_000_000,
    "pricing_multiplier": 2.5,
    "baseline_variable_gross_margin": 0.60,
    "long_term_gross_margin_target_min": 0.65,
    "monthly_logo_churn_max": 0.04,
    "net_revenue_retention_min": 1.00,
    "cac_payback_months_max": 12,
    "ltv_cac_ratio_min": 3.0,
    "operating_runway_months_min": 12,
    "max_single_customer_revenue_concentration": 0.15,
}

IMPACT_TARGETS = {
    "weekly_active_users": 100_000,
    "phase_1_completion_rate_min": 0.65,
    "phase_2_completion_rate_min": 0.50,
    "phase_3_completion_rate_min": 0.35,
    "phase_4_completion_rate_min": 0.25,
    "real_world_validation_completion_min": 0.40,
    "platform_hard_blocker_enforcement": 1.00,
    "external_hard_blocker_compliance_min": 0.80,
    "readiness_improvement_90d_min": 0.25,
    "time_to_first_value_minutes_target": 15,
    "time_to_first_value_user_share": 0.80,
    "venture_continuation_12m_reporting_min": 0.70,
}


class MeaningfulActivityService:
    def record(
        self,
        *,
        user_id: int,
        activity_type: str,
        venture_id: Optional[int] = None,
        impact_category: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeaningfulActivityEvent:
        is_meaningful = self.is_meaningful(activity_type)
        event = MeaningfulActivityEvent(
            user_id=user_id,
            venture_id=venture_id,
            activity_type=activity_type,
            is_meaningful=is_meaningful,
            impact_category=impact_category,
            source=source,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def is_meaningful(self, activity_type: str) -> bool:
        if activity_type in MeaningfulActivityEvent.VANITY_TYPES:
            return False
        return activity_type in MeaningfulActivityEvent.MEANINGFUL_TYPES

    def weekly_active_users(self, *, end_at: Optional[datetime] = None) -> Dict[str, Any]:
        end_at = end_at or datetime.utcnow()
        start_at = end_at - timedelta(days=7)
        count = (
            db.session.query(func.count(func.distinct(MeaningfulActivityEvent.user_id)))
            .filter(MeaningfulActivityEvent.created_at >= start_at)
            .filter(MeaningfulActivityEvent.created_at <= end_at)
            .filter(MeaningfulActivityEvent.is_meaningful.is_(True))
            .scalar()
        ) or 0
        return {
            "weekly_active_users": count,
            "target": IMPACT_TARGETS["weekly_active_users"],
            "target_progress": round(count / IMPACT_TARGETS["weekly_active_users"], 4),
            "window_start": start_at.isoformat(),
            "window_end": end_at.isoformat(),
            "definition": "Users with at least one meaningful venture-building action in the last seven days.",
        }


class MeteredRevenueService:
    PRICING_MULTIPLIER = 2.5

    def record(
        self,
        *,
        direct_platform_cost: float,
        user_id: Optional[int] = None,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        payer_type: str = "individual",
        revenue_category: str = "metered_individual_usage",
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeteredRevenueEvent:
        excluded = revenue_category in MeteredRevenueEvent.EXCLUDED_CATEGORIES
        repeatable = revenue_category in MeteredRevenueEvent.REPEATABLE_CATEGORIES and not excluded
        event = MeteredRevenueEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            payer_type=payer_type,
            revenue_category=revenue_category,
            direct_platform_cost=direct_platform_cost,
            billed_amount=round(direct_platform_cost * self.PRICING_MULTIPLIER, 2),
            pricing_multiplier=self.PRICING_MULTIPLIER,
            currency=currency,
            is_repeatable_platform_revenue=repeatable,
            is_excluded_from_core_target=excluded,
            exclusion_reason="Excluded from core target because this is not repeatable platform usage." if excluded else None,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def monthly_repeatable_metered_revenue(self, *, end_at: Optional[datetime] = None) -> Dict[str, Any]:
        end_at = end_at or datetime.utcnow()
        start_at = end_at - timedelta(days=30)
        revenue = (
            db.session.query(func.coalesce(func.sum(MeteredRevenueEvent.billed_amount), 0.0))
            .filter(MeteredRevenueEvent.created_at >= start_at)
            .filter(MeteredRevenueEvent.created_at <= end_at)
            .filter(MeteredRevenueEvent.is_repeatable_platform_revenue.is_(True))
            .filter(MeteredRevenueEvent.is_excluded_from_core_target.is_(False))
            .scalar()
        ) or 0.0
        direct_cost = (
            db.session.query(func.coalesce(func.sum(MeteredRevenueEvent.direct_platform_cost), 0.0))
            .filter(MeteredRevenueEvent.created_at >= start_at)
            .filter(MeteredRevenueEvent.created_at <= end_at)
            .filter(MeteredRevenueEvent.is_repeatable_platform_revenue.is_(True))
            .filter(MeteredRevenueEvent.is_excluded_from_core_target.is_(False))
            .scalar()
        ) or 0.0
        margin = ((revenue - direct_cost) / revenue) if revenue else 0.0
        return {
            "monthly_repeatable_metered_revenue": round(revenue, 2),
            "target": COMMERCIAL_TARGETS["monthly_repeatable_metered_revenue_eur"],
            "target_progress": round(revenue / COMMERCIAL_TARGETS["monthly_repeatable_metered_revenue_eur"], 4),
            "annualized_repeatable_revenue": round(revenue * 12, 2),
            "direct_platform_cost": round(direct_cost, 2),
            "variable_gross_margin_before_fixed_overhead": round(margin, 4),
            "pricing_formula": "billed_amount = actual_direct_platform_cost x 2.5",
            "window_start": start_at.isoformat(),
            "window_end": end_at.isoformat(),
        }


class ReadinessImpactService:
    def create_snapshot(
        self,
        *,
        user_id: int,
        venture_id: Optional[int] = None,
        snapshot_type: str = "periodic",
        financial_runway_score: float = 0.0,
        time_capacity_score: float = 0.0,
        idea_clarity_score: float = 0.0,
        market_evidence_score: float = 0.0,
        business_model_score: float = 0.0,
        real_world_execution_score: float = 0.0,
        risk_reduction_score: float = 0.0,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReadinessSnapshot:
        scores = [
            financial_runway_score,
            time_capacity_score,
            idea_clarity_score,
            market_evidence_score,
            business_model_score,
            real_world_execution_score,
            risk_reduction_score,
        ]
        snapshot = ReadinessSnapshot(
            user_id=user_id,
            venture_id=venture_id,
            snapshot_type=snapshot_type,
            financial_runway_score=financial_runway_score,
            time_capacity_score=time_capacity_score,
            idea_clarity_score=idea_clarity_score,
            market_evidence_score=market_evidence_score,
            business_model_score=business_model_score,
            real_world_execution_score=real_world_execution_score,
            risk_reduction_score=risk_reduction_score,
            overall_score=round(sum(scores) / len(scores), 4),
            source=source,
        )
        snapshot.set_metadata(metadata or {})
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def readiness_improvement(self, *, user_id: int, venture_id: Optional[int] = None, days: int = 90) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=days)
        query = ReadinessSnapshot.query.filter_by(user_id=user_id)
        if venture_id is not None:
            query = query.filter_by(venture_id=venture_id)
        snapshots = query.filter(ReadinessSnapshot.created_at >= since).order_by(ReadinessSnapshot.created_at.asc()).all()
        if len(snapshots) < 2:
            return {
                "has_enough_data": False,
                "message": "At least two readiness snapshots are required to measure improvement.",
                "days": days,
            }
        first, last = snapshots[0], snapshots[-1]
        improvements = {}
        improved_count = 0
        for indicator in ReadinessSnapshot.INDICATORS:
            delta = getattr(last, indicator) - getattr(first, indicator)
            improvements[indicator] = round(delta, 4)
            if delta > 0:
                improved_count += 1
        overall_delta = last.overall_score - first.overall_score
        return {
            "has_enough_data": True,
            "days": days,
            "first_snapshot": first.to_dict(),
            "latest_snapshot": last.to_dict(),
            "indicator_improvements": improvements,
            "improved_indicator_count": improved_count,
            "better_prepared": improved_count >= 4,
            "overall_improvement_ratio": round(overall_delta / first.overall_score, 4) if first.overall_score else None,
            "definition": "A user is better prepared when at least 4 of 7 readiness indicators improve.",
        }


class HardBlockerMetricsService:
    def record(
        self,
        *,
        user_id: int,
        blocker_type: str,
        blocked_action_type: str,
        venture_id: Optional[int] = None,
        controlled_by_platform: bool = True,
        enforcement_status: str = "blocked",
        user_reported_external_proceeded: Optional[bool] = None,
        risk_period_days: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HardBlockerMetric:
        metric = HardBlockerMetric(
            user_id=user_id,
            venture_id=venture_id,
            blocker_type=blocker_type,
            controlled_by_platform=controlled_by_platform,
            blocked_action_type=blocked_action_type,
            enforcement_status=enforcement_status,
            user_reported_external_proceeded=user_reported_external_proceeded,
            risk_period_days=risk_period_days,
        )
        metric.set_metadata(metadata or {})
        db.session.add(metric)
        db.session.commit()
        return metric

    def summary(self, *, days: int = 30) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=days)
        records = HardBlockerMetric.query.filter(HardBlockerMetric.created_at >= since).all()
        platform = [r for r in records if r.controlled_by_platform]
        external = [r for r in records if not r.controlled_by_platform]
        platform_enforced = [r for r in platform if r.enforcement_status == "blocked"]
        external_compliant = [r for r in external if r.user_reported_external_proceeded is False]
        return {
            "days": days,
            "platform_hard_blocker_enforcement_rate": round(len(platform_enforced) / len(platform), 4) if platform else None,
            "platform_target": IMPACT_TARGETS["platform_hard_blocker_enforcement"],
            "external_hard_blocker_compliance_rate": round(len(external_compliant) / len(external), 4) if external else None,
            "external_target": IMPACT_TARGETS["external_hard_blocker_compliance_min"],
            "platform_records": len(platform),
            "external_records": len(external),
        }


class VentureContinuationService:
    def record(
        self,
        *,
        user_id: int,
        status: str,
        venture_id: Optional[int] = None,
        report_period_month: int = 12,
        report_summary: Optional[str] = None,
        responsible_outcome: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VentureContinuationStatus:
        record = VentureContinuationStatus(
            user_id=user_id,
            venture_id=venture_id,
            status=status,
            report_period_month=report_period_month,
            report_summary=report_summary,
            responsible_outcome=responsible_outcome,
        )
        record.set_metadata(metadata or {})
        db.session.add(record)
        db.session.commit()
        return record


class SuccessDashboardService:
    def dashboard(self) -> Dict[str, Any]:
        activity = MeaningfulActivityService().weekly_active_users()
        revenue = MeteredRevenueService().monthly_repeatable_metered_revenue()
        blockers = HardBlockerMetricsService().summary(days=30)
        return {
            "commercial_sustainability": revenue,
            "user_impact": activity,
            "hard_blockers": blockers,
            "targets": {
                "commercial": COMMERCIAL_TARGETS,
                "impact": IMPACT_TARGETS,
            },
            "balance_rules": [
                "Do not monetize confusion.",
                "Do not monetize desperation aggressively.",
                "Do not push paid actions before readiness.",
                "Do not treat user excitement as evidence.",
                "Do not count passive logins as impact.",
                "Do not count polished documents as progress unless the underlying evidence improved.",
                "Do not count revenue as success if the user becomes less safe, less clear, or more financially exposed.",
                "Do count responsible pauses, pivots, and stopped actions when they prevent harm.",
            ],
        }
