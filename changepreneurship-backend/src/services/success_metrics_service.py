"""Commercial sustainability and user-impact metrics service.

Turns five-year targets into measurable calculations:
- monthly repeatable metered revenue;
- strict WAU based only on meaningful venture-building actions;
- direct-cost gross margin from cost x 2.5 pricing;
- hard-blocker enforcement and external compliance;
- readiness improvement based on measurable snapshots.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func

from src.models.assessment import db
from src.models.mvp_success_metrics import (
    HardBlockerEvent,
    MeaningfulActivityEvent,
    MeteredRevenueEvent,
    ReadinessSnapshot,
    SuccessMetricSnapshot,
)


COMMERCIAL_TARGETS = {
    "monthly_repeatable_metered_revenue": 500000.0,
    "annualized_repeatable_revenue": 6000000.0,
    "baseline_variable_gross_margin": 0.60,
    "long_term_gross_margin_target_min": 0.65,
    "monthly_logo_churn_max": 0.04,
    "net_revenue_retention_min": 1.0,
    "cac_payback_months_max": 12,
    "ltv_cac_ratio_min": 3.0,
    "operating_runway_months_min": 12,
    "largest_customer_revenue_share_max": 0.15,
}

IMPACT_TARGETS = {
    "strict_weekly_active_users": 100000,
    "phase_1_completion_rate": 0.65,
    "phase_2_completion_rate": 0.50,
    "phase_3_completion_rate": 0.35,
    "phase_4_completion_rate": 0.25,
    "real_world_validation_completion_rate": 0.40,
    "platform_hard_blocker_enforcement_rate": 1.0,
    "external_hard_blocker_compliance_rate": 0.80,
    "readiness_improvement_rate": 0.25,
    "time_to_first_value_minutes_80pct": 15,
    "venture_continuation_reporting_rate": 0.70,
}

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
    "venture_component_approved",
    "real_world_task_reported",
    "blocker_reviewed_safer_route_chosen",
    "next_action_approved",
    "account_connected_for_context",
    "business_model_updated",
    "validation_result_updated",
    "operating_assumption_updated",
    "venture_status_reported",
    "responsible_pause_reported",
    "pivot_reported",
    "closure_reported",
    "continuation_reported",
}

VANITY_ACTIVITY_TYPES = {
    "login_only",
    "dashboard_opened",
    "passive_reading",
    "click_without_progress",
    "old_output_viewed",
    "abandoned_session",
    "accidental_visit",
}

REPEATABLE_REVENUE_CATEGORIES = {
    "metered_individual_usage",
    "prepaid_usage",
    "institutional_usage",
    "sponsored_access",
    "capped_usage_bundle",
    "organization_usage_pool",
    "monthly_invoiced_usage",
}

EXCLUDED_REVENUE_CATEGORIES = {
    "one_time_consulting",
    "one_off_custom_project",
    "non_repeatable_grant",
    "irregular_implementation_fee",
    "manual_agency_work_outside_product",
    "one_time_setup_fee",
    "non_recurring_development_work",
    "unrelated_service_revenue",
    "exceptional_partnership_income",
}


class SuccessMetricsService:
    PRICING_MULTIPLIER = 2.5

    def record_meaningful_activity(
        self,
        *,
        user_id: int,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        activity_type: str,
        impact_category: str = "venture_progress",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeaningfulActivityEvent:
        qualifies = activity_type in MEANINGFUL_ACTIVITY_TYPES and activity_type not in VANITY_ACTIVITY_TYPES
        event = MeaningfulActivityEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            activity_type=activity_type,
            qualifies_for_wau=qualifies,
            impact_category=impact_category,
            description=description,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def record_revenue_event(
        self,
        *,
        actual_direct_cost: float,
        user_id: Optional[int] = None,
        venture_id: Optional[int] = None,
        action_id: Optional[int] = None,
        revenue_category: str = "metered_individual_usage",
        payer_type: str = "individual",
        payer_reference: Optional[str] = None,
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeteredRevenueEvent:
        should_count = revenue_category in REPEATABLE_REVENUE_CATEGORIES and revenue_category not in EXCLUDED_REVENUE_CATEGORIES
        billed_price = round(float(actual_direct_cost or 0) * self.PRICING_MULTIPLIER, 2)
        event = MeteredRevenueEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            revenue_category=revenue_category,
            payer_type=payer_type,
            payer_reference=payer_reference,
            actual_direct_cost=float(actual_direct_cost or 0),
            billed_price=billed_price,
            pricing_multiplier=self.PRICING_MULTIPLIER,
            currency=currency,
            repeatable_platform_revenue=should_count,
            should_count_toward_metered_mrr=should_count,
            excluded_reason=None if should_count else "Revenue category is not repeatable platform usage.",
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def record_readiness_snapshot(
        self,
        *,
        user_id: int,
        venture_id: Optional[int] = None,
        financial_readiness_score: float = 0.0,
        time_capacity_score: float = 0.0,
        idea_clarity_score: float = 0.0,
        market_evidence_score: float = 0.0,
        business_model_score: float = 0.0,
        execution_score: float = 0.0,
        risk_reduction_score: float = 0.0,
        source: str = "manual_or_profile",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReadinessSnapshot:
        scores = [
            financial_readiness_score,
            time_capacity_score,
            idea_clarity_score,
            market_evidence_score,
            business_model_score,
            execution_score,
            risk_reduction_score,
        ]
        aggregate = round(sum(float(value or 0) for value in scores) / len(scores), 2)
        snapshot = ReadinessSnapshot(
            user_id=user_id,
            venture_id=venture_id,
            aggregate_score=aggregate,
            financial_readiness_score=financial_readiness_score,
            time_capacity_score=time_capacity_score,
            idea_clarity_score=idea_clarity_score,
            market_evidence_score=market_evidence_score,
            business_model_score=business_model_score,
            execution_score=execution_score,
            risk_reduction_score=risk_reduction_score,
            source=source,
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
        platform_controlled: bool = True,
        enforcement_status: str = "enforced",
        risk_explanation: Optional[str] = None,
        unlock_condition: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HardBlockerEvent:
        event = HardBlockerEvent(
            user_id=user_id,
            venture_id=venture_id,
            action_id=action_id,
            blocker_type=blocker_type,
            blocked_action=blocked_action,
            platform_controlled=platform_controlled,
            enforcement_status=enforcement_status,
            risk_explanation=risk_explanation,
            unlock_condition=unlock_condition,
        )
        event.set_metadata(metadata or {})
        db.session.add(event)
        db.session.commit()
        return event

    def aggregate(self, *, period_days: int = 30, end: Optional[datetime] = None, persist_snapshot: bool = False) -> Dict[str, Any]:
        end = end or datetime.utcnow()
        start = end - timedelta(days=period_days)
        week_start = end - timedelta(days=7)

        revenue_query = MeteredRevenueEvent.query.filter(
            MeteredRevenueEvent.created_at >= start,
            MeteredRevenueEvent.created_at <= end,
            MeteredRevenueEvent.should_count_toward_metered_mrr.is_(True),
        )
        total_billed = float(revenue_query.with_entities(func.coalesce(func.sum(MeteredRevenueEvent.billed_price), 0)).scalar() or 0)
        total_direct_cost = float(revenue_query.with_entities(func.coalesce(func.sum(MeteredRevenueEvent.actual_direct_cost), 0)).scalar() or 0)
        gross_margin = round((total_billed - total_direct_cost) / total_billed, 4) if total_billed else 0.0
        annualized = round(total_billed * 12, 2)

        strict_wau = (
            db.session.query(func.count(func.distinct(MeaningfulActivityEvent.user_id)))
            .filter(
                MeaningfulActivityEvent.created_at >= week_start,
                MeaningfulActivityEvent.created_at <= end,
                MeaningfulActivityEvent.qualifies_for_wau.is_(True),
            )
            .scalar()
            or 0
        )
        meaningful_count = (
            MeaningfulActivityEvent.query
            .filter(
                MeaningfulActivityEvent.created_at >= week_start,
                MeaningfulActivityEvent.created_at <= end,
                MeaningfulActivityEvent.qualifies_for_wau.is_(True),
            )
            .count()
        )

        platform_blockers = HardBlockerEvent.query.filter(
            HardBlockerEvent.created_at >= start,
            HardBlockerEvent.created_at <= end,
            HardBlockerEvent.platform_controlled.is_(True),
        ).all()
        platform_enforced = [item for item in platform_blockers if item.enforcement_status in {"enforced", "blocked"}]
        platform_rate = round(len(platform_enforced) / len(platform_blockers), 4) if platform_blockers else 1.0

        external_blockers = HardBlockerEvent.query.filter(
            HardBlockerEvent.created_at >= start,
            HardBlockerEvent.created_at <= end,
            HardBlockerEvent.platform_controlled.is_(False),
        ).all()
        external_compliant = [item for item in external_blockers if item.enforcement_status in {"complied", "alternative_chosen", "not_proceeded"}]
        external_rate = round(len(external_compliant) / len(external_blockers), 4) if external_blockers else 0.0

        readiness_rate = self._readiness_improvement_rate(start=start, end=end)
        target_progress = {
            "monthly_repeatable_metered_revenue": self._progress(total_billed, COMMERCIAL_TARGETS["monthly_repeatable_metered_revenue"]),
            "annualized_repeatable_revenue": self._progress(annualized, COMMERCIAL_TARGETS["annualized_repeatable_revenue"]),
            "variable_gross_margin": self._progress(gross_margin, COMMERCIAL_TARGETS["baseline_variable_gross_margin"]),
            "strict_weekly_active_users": self._progress(strict_wau, IMPACT_TARGETS["strict_weekly_active_users"]),
            "platform_hard_blocker_enforcement_rate": self._progress(platform_rate, IMPACT_TARGETS["platform_hard_blocker_enforcement_rate"]),
            "external_hard_blocker_compliance_rate": self._progress(external_rate, IMPACT_TARGETS["external_hard_blocker_compliance_rate"]),
            "readiness_improvement_rate": self._progress(readiness_rate, IMPACT_TARGETS["readiness_improvement_rate"]),
        }

        result = {
            "period": {"start": start.isoformat(), "end": end.isoformat(), "days": period_days},
            "commercial_targets": COMMERCIAL_TARGETS,
            "impact_targets": IMPACT_TARGETS,
            "monthly_repeatable_metered_revenue": round(total_billed, 2),
            "annualized_repeatable_revenue": annualized,
            "variable_gross_margin_before_fixed_overhead": gross_margin,
            "strict_weekly_active_users": int(strict_wau),
            "meaningful_activity_count_7d": int(meaningful_count),
            "platform_hard_blocker_enforcement_rate": platform_rate,
            "external_hard_blocker_compliance_rate": external_rate,
            "readiness_improvement_rate": readiness_rate,
            "target_progress": target_progress,
            "non_negotiable_check": {
                "revenue_without_impact_is_not_enough": total_billed > 0 and strict_wau > 0,
                "activity_without_financial_sustainability_is_not_enough": strict_wau > 0 and total_billed > 0,
                "passive_logins_do_not_count_as_impact": True,
                "baseline_margin_matches_cost_x_2_5": gross_margin == 0.0 or abs(gross_margin - 0.60) <= 0.10,
            },
        }

        if persist_snapshot:
            snapshot = SuccessMetricSnapshot(
                period_start=start,
                period_end=end,
                monthly_repeatable_metered_revenue=round(total_billed, 2),
                annualized_repeatable_revenue=annualized,
                variable_gross_margin=gross_margin,
                strict_weekly_active_users=int(strict_wau),
                meaningful_activity_count=int(meaningful_count),
                platform_hard_blocker_enforcement_rate=platform_rate,
                external_hard_blocker_compliance_rate=external_rate,
                readiness_improvement_rate=readiness_rate,
            )
            snapshot.set_target_progress(target_progress)
            db.session.add(snapshot)
            db.session.commit()
            result["snapshot"] = snapshot.to_dict()

        return result

    def _readiness_improvement_rate(self, *, start: datetime, end: datetime) -> float:
        users = (
            db.session.query(ReadinessSnapshot.user_id)
            .filter(ReadinessSnapshot.created_at >= start, ReadinessSnapshot.created_at <= end)
            .distinct()
            .all()
        )
        improved = 0
        measured = 0
        for (user_id,) in users:
            first = (
                ReadinessSnapshot.query
                .filter_by(user_id=user_id)
                .filter(ReadinessSnapshot.created_at >= start, ReadinessSnapshot.created_at <= end)
                .order_by(ReadinessSnapshot.created_at.asc())
                .first()
            )
            last = (
                ReadinessSnapshot.query
                .filter_by(user_id=user_id)
                .filter(ReadinessSnapshot.created_at >= start, ReadinessSnapshot.created_at <= end)
                .order_by(ReadinessSnapshot.created_at.desc())
                .first()
            )
            if first and last and first.id != last.id:
                measured += 1
                if last.aggregate_score > first.aggregate_score:
                    improved += 1
        return round(improved / measured, 4) if measured else 0.0

    def _progress(self, value: float, target: float) -> Dict[str, Any]:
        ratio = round(float(value or 0) / float(target or 1), 4)
        return {"value": value, "target": target, "ratio": ratio, "percent": round(ratio * 100, 2)}
