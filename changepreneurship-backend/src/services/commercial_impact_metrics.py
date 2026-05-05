"""Commercial sustainability and user-impact metrics service.

This service implements the measurement logic from the five-year outcome text:

- repeatable metered platform revenue, not traditional flat SaaS MRR;
- actual direct platform cost x 2.5;
- meaningful WAU only when users complete venture-building actions;
- readiness improvement based on measurable dimensions, not confidence alone;
- separate platform hard-blocker enforcement and external blocker compliance;
- responsible pauses/pivots/stops as valid impact outcomes.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import and_, func

from src.models.assessment import db
from src.models.mvp_metrics import (
    HardBlockerEvent,
    MeaningfulActivityEvent,
    MonthlyCommercialImpactSnapshot,
    ReadinessSnapshot,
    RevenueUsageEvent,
    VentureContinuationStatus,
)


MEANINGFUL_ACTIVITY_TYPES = {
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
    "blocker_reviewed",
    "safer_route_chosen",
    "next_action_approved",
    "account_connected_for_context",
    "business_model_updated",
    "validation_result_updated",
    "process_updated",
    "operating_assumption_updated",
    "progress_reported",
    "pause_reported",
    "pivot_reported",
    "closure_reported",
    "continuation_reported",
}

PASSIVE_ACTIVITY_TYPES = {
    "login",
    "dashboard_opened",
    "passive_read",
    "old_output_viewed",
    "click_without_progress",
    "abandoned_session",
}

REPEATABLE_REVENUE_CATEGORIES = {
    "metered_individual_usage",
    "prepaid_usage_consumed",
    "institutional_usage",
    "sponsored_access_usage",
    "capped_usage_bundle_consumed",
    "organization_level_usage",
    "monthly_invoiced_usage",
}

NON_REPEATABLE_REVENUE_CATEGORIES = {
    "one_time_consulting",
    "one_off_custom_project",
    "non_repeatable_grant",
    "irregular_implementation_fee",
    "manual_agency_work_outside_product",
    "one_time_setup_fee",
    "non_recurring_development_work",
    "unrelated_service_revenue",
    "exceptional_non_platform_partnership_income",
}


class CommercialImpactMetricsService:
    PRICING_MULTIPLIER = 2.5
    TARGET_MONTHLY_REVENUE = 500_000.0
    TARGET_ANNUALIZED_REVENUE = 6_000_000.0
    TARGET_WAU = 100_000
    TARGET_GROSS_MARGIN = 0.60
    TARGET_EXTERNAL_BLOCKER_COMPLIANCE = 0.80
    TARGET_READINESS_IMPROVEMENT = 0.25

    def record_meaningful_activity(
        self,
        *,
        user_id: int,
        activity_type: str,
        venture_id: Optional[int] = None,
        phase_id: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        evidence_strength_after: Optional[str] = None,
    ) -> MeaningfulActivityEvent:
        counts = activity_type in MEANINGFUL_ACTIVITY_TYPES
        if activity_type in PASSIVE_ACTIVITY_TYPES:
            counts = False
        event = MeaningfulActivityEvent(
            user_id=user_id,
            venture_id=venture_id,
            activity_type=activity_type,
            phase_id=phase_id,
            source=source,
            counts_toward_wau=counts,
            impact_weight=1.0 if counts else 0.0,
            evidence_strength_after=evidence_strength_after,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def record_revenue_usage(
        self,
        *,
        direct_platform_cost: float,
        user_id: Optional[int] = None,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        payer_type: str = "individual",
        revenue_category: str = "metered_individual_usage",
        currency: str = "EUR",
        value_justification: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RevenueUsageEvent:
        repeatable = revenue_category in REPEATABLE_REVENUE_CATEGORIES
        excluded_reason = None
        if revenue_category in NON_REPEATABLE_REVENUE_CATEGORIES:
            repeatable = False
            excluded_reason = "Excluded from repeatable metered platform revenue target."
        billed = round(float(direct_platform_cost) * self.PRICING_MULTIPLIER, 2)
        event = RevenueUsageEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            payer_type=payer_type,
            revenue_category=revenue_category,
            direct_platform_cost=float(direct_platform_cost),
            billed_amount=billed,
            pricing_multiplier=self.PRICING_MULTIPLIER,
            currency=currency,
            repeatable_platform_revenue=repeatable,
            excluded_reason=excluded_reason,
            value_justification=value_justification,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def capture_readiness_snapshot(
        self,
        *,
        user_id: int,
        venture_id: Optional[int] = None,
        snapshot_type: str = "periodic",
        financial_runway_score: float = 0,
        time_capacity_score: float = 0,
        idea_clarity_score: float = 0,
        market_evidence_score: float = 0,
        business_model_score: float = 0,
        real_world_execution_score: float = 0,
        risk_reduction_score: float = 0,
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
        overall = round(sum(scores) / len(scores), 2)
        previous = self._previous_readiness_snapshot(user_id=user_id, venture_id=venture_id)
        improved_count = 0
        if previous:
            previous_scores = [
                previous.financial_runway_score,
                previous.time_capacity_score,
                previous.idea_clarity_score,
                previous.market_evidence_score,
                previous.business_model_score,
                previous.real_world_execution_score,
                previous.risk_reduction_score,
            ]
            improved_count = sum(1 for new, old in zip(scores, previous_scores) if new > old)
        better_prepared = improved_count >= 4
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
            overall_readiness_score=overall,
            dimensions_improved_count=improved_count,
            better_prepared=better_prepared,
        )
        snapshot.set_metadata(metadata or {})
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def record_hard_blocker(
        self,
        *,
        user_id: int,
        blocker_type: str,
        blocked_action: str,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        blocker_scope: str = "platform_controlled",
        warning_message: Optional[str] = None,
        enforcement_status: str = "enforced",
        external_user_reported_status: Optional[str] = None,
        risk_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HardBlockerEvent:
        event = HardBlockerEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            blocker_type=blocker_type,
            blocker_scope=blocker_scope,
            blocked_action=blocked_action,
            warning_message=warning_message,
            enforcement_status=enforcement_status,
            external_user_reported_status=external_user_reported_status,
            risk_period_days=risk_period_days,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def record_venture_continuation_status(
        self,
        *,
        user_id: int,
        status: str,
        venture_id: Optional[int] = None,
        reason: Optional[str] = None,
        months_since_activation: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VentureContinuationStatus:
        responsible_statuses = {"responsible_start", "validated_continue", "responsible_pause", "responsible_pivot", "responsible_stop", "closed_before_harm"}
        record = VentureContinuationStatus(
            user_id=user_id,
            venture_id=venture_id,
            status=status,
            responsible_outcome=status in responsible_statuses,
            reason=reason,
            months_since_activation=months_since_activation,
        )
        record.set_metadata(metadata or {})
        db.session.add(record)
        db.session.commit()
        return record

    def monthly_snapshot(self, *, period: Optional[str] = None) -> MonthlyCommercialImpactSnapshot:
        start, end, period_label = self._period_bounds(period)
        revenue_rows = RevenueUsageEvent.query.filter(
            RevenueUsageEvent.occurred_at >= start,
            RevenueUsageEvent.occurred_at < end,
            RevenueUsageEvent.repeatable_platform_revenue.is_(True),
        ).all()
        monthly_revenue = sum(row.billed_amount for row in revenue_rows)
        direct_cost = sum(row.direct_platform_cost for row in revenue_rows)
        gross_margin = round((monthly_revenue - direct_cost) / monthly_revenue, 4) if monthly_revenue else 0.0
        wau = self.weekly_active_users(end=end)
        avg_revenue_per_wau = round(monthly_revenue / wau, 2) if wau else 0.0
        platform_enforcement = self.platform_hard_blocker_enforcement_rate(start=start, end=end)
        external_compliance = self.external_hard_blocker_compliance_rate(start=start, end=end)
        readiness_improvement = self.readiness_improvement_rate(start=start, end=end)

        target_status = {
            "monthly_revenue_target_met": monthly_revenue >= self.TARGET_MONTHLY_REVENUE,
            "annualized_revenue_target_met": monthly_revenue * 12 >= self.TARGET_ANNUALIZED_REVENUE,
            "gross_margin_target_met": gross_margin >= self.TARGET_GROSS_MARGIN,
            "wau_target_met": wau >= self.TARGET_WAU,
            "external_blocker_compliance_target_met": external_compliance >= self.TARGET_EXTERNAL_BLOCKER_COMPLIANCE,
            "readiness_improvement_target_met": readiness_improvement >= self.TARGET_READINESS_IMPROVEMENT,
            "pricing_multiplier": self.PRICING_MULTIPLIER,
            "target_monthly_revenue": self.TARGET_MONTHLY_REVENUE,
            "target_wau": self.TARGET_WAU,
        }

        snapshot = MonthlyCommercialImpactSnapshot.query.filter_by(period=period_label).first()
        if not snapshot:
            snapshot = MonthlyCommercialImpactSnapshot(period=period_label)
            db.session.add(snapshot)
        snapshot.monthly_repeatable_metered_revenue = monthly_revenue
        snapshot.annualized_repeatable_revenue = monthly_revenue * 12
        snapshot.direct_platform_cost = direct_cost
        snapshot.gross_margin_before_fixed_overhead = gross_margin
        snapshot.weekly_active_users = wau
        snapshot.average_revenue_per_wau = avg_revenue_per_wau
        snapshot.platform_hard_blocker_enforcement_rate = platform_enforcement
        snapshot.external_hard_blocker_compliance_rate = external_compliance
        snapshot.readiness_improvement_rate = readiness_improvement
        snapshot.updated_at = datetime.utcnow()
        snapshot.set_target_status(target_status)
        db.session.commit()
        return snapshot

    def weekly_active_users(self, *, end: Optional[datetime] = None) -> int:
        end = end or datetime.utcnow()
        start = end - timedelta(days=7)
        return db.session.query(func.count(func.distinct(MeaningfulActivityEvent.user_id))).filter(
            MeaningfulActivityEvent.occurred_at >= start,
            MeaningfulActivityEvent.occurred_at < end,
            MeaningfulActivityEvent.counts_toward_wau.is_(True),
        ).scalar() or 0

    def platform_hard_blocker_enforcement_rate(self, *, start: datetime, end: datetime) -> float:
        query = HardBlockerEvent.query.filter(
            HardBlockerEvent.occurred_at >= start,
            HardBlockerEvent.occurred_at < end,
            HardBlockerEvent.blocker_scope == "platform_controlled",
        )
        total = query.count()
        if total == 0:
            return 1.0
        enforced = query.filter(HardBlockerEvent.enforcement_status == "enforced").count()
        return round(enforced / total, 4)

    def external_hard_blocker_compliance_rate(self, *, start: datetime, end: datetime) -> float:
        query = HardBlockerEvent.query.filter(
            HardBlockerEvent.occurred_at >= start,
            HardBlockerEvent.occurred_at < end,
            HardBlockerEvent.blocker_scope == "external_behavior",
        )
        total = query.count()
        if total == 0:
            return 1.0
        compliant = query.filter(HardBlockerEvent.external_user_reported_status.in_(["did_not_proceed", "paused", "chose_safer_route"])).count()
        return round(compliant / total, 4)

    def readiness_improvement_rate(self, *, start: datetime, end: datetime) -> float:
        improved = ReadinessSnapshot.query.filter(
            ReadinessSnapshot.captured_at >= start,
            ReadinessSnapshot.captured_at < end,
            ReadinessSnapshot.better_prepared.is_(True),
        ).count()
        total = ReadinessSnapshot.query.filter(
            ReadinessSnapshot.captured_at >= start,
            ReadinessSnapshot.captured_at < end,
        ).count()
        if total == 0:
            return 0.0
        return round(improved / total, 4)

    def balance_check(self, *, period: Optional[str] = None) -> Dict[str, Any]:
        snapshot = self.monthly_snapshot(period=period)
        target = snapshot.get_target_status()
        red_flags = []
        if snapshot.monthly_repeatable_metered_revenue > 0 and snapshot.readiness_improvement_rate == 0:
            red_flags.append("Revenue exists but no measurable readiness improvement was recorded.")
        if snapshot.weekly_active_users > 0 and snapshot.monthly_repeatable_metered_revenue == 0:
            red_flags.append("User activity exists but no repeatable metered revenue was recorded.")
        if snapshot.platform_hard_blocker_enforcement_rate < 1.0:
            red_flags.append("Platform-controlled hard blockers were not enforced 100%.")
        if snapshot.average_revenue_per_wau > 25 and snapshot.readiness_improvement_rate < self.TARGET_READINESS_IMPROVEMENT:
            red_flags.append("Revenue per active user is high while readiness improvement is weak; review monetization pressure.")
        return {
            "snapshot": snapshot.to_dict(),
            "commercial_sustainability_ok": target.get("monthly_revenue_target_met") and target.get("gross_margin_target_met"),
            "user_impact_ok": target.get("wau_target_met") and target.get("readiness_improvement_target_met"),
            "red_flags": red_flags,
            "principle": "Revenue without measurable readiness improvement is not enough; activity without sustainability is also not enough.",
        }

    def _previous_readiness_snapshot(self, *, user_id: int, venture_id: Optional[int]) -> Optional[ReadinessSnapshot]:
        return ReadinessSnapshot.query.filter_by(user_id=user_id, venture_id=venture_id).order_by(ReadinessSnapshot.captured_at.desc()).first()

    def _period_bounds(self, period: Optional[str]) -> tuple[datetime, datetime, str]:
        if period:
            year, month = [int(part) for part in period.split("-")]
            start = datetime(year, month, 1)
        else:
            now = datetime.utcnow()
            start = datetime(now.year, now.month, 1)
        if start.month == 12:
            end = datetime(start.year + 1, 1, 1)
        else:
            end = datetime(start.year, start.month + 1, 1)
        return start, end, f"{start.year:04d}-{start.month:02d}"
