"""Routes for commercial sustainability and user-impact metrics."""

from flask import Blueprint, jsonify, request

from src.models.mvp_metrics import (
    HardBlockerMetric,
    MeaningfulActivityEvent,
    MeteredRevenueEvent,
    ReadinessSnapshot,
    VentureContinuationStatus,
)
from src.services.mvp_success_metrics import (
    HardBlockerMetricsService,
    MeaningfulActivityService,
    MeteredRevenueService,
    ReadinessImpactService,
    SuccessDashboardService,
    VentureContinuationService,
)
from src.utils.auth import verify_session_token

mvp_success_bp = Blueprint("mvp_success_metrics", __name__)


def _current_user_or_error():
    user, session, error, status = verify_session_token()
    if error:
        return None, (jsonify(error), status)
    return user, None


@mvp_success_bp.route("/dashboard", methods=["GET"])
def success_dashboard():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    return jsonify({"success": True, "dashboard": SuccessDashboardService().dashboard()})


@mvp_success_bp.route("/activity", methods=["POST"])
def record_activity():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    event = MeaningfulActivityService().record(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        activity_type=data.get("activity_type") or "passive_read",
        impact_category=data.get("impact_category"),
        source=data.get("source") or "manual_api",
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "activity_event": event.to_dict()}), 201


@mvp_success_bp.route("/activity", methods=["GET"])
def list_activity():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = MeaningfulActivityEvent.query.filter_by(user_id=user.id).order_by(MeaningfulActivityEvent.created_at.desc()).limit(100).all()
    return jsonify({"success": True, "activity_events": [record.to_dict() for record in records]})


@mvp_success_bp.route("/activity/wau", methods=["GET"])
def weekly_active_users():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    return jsonify({"success": True, "wau": MeaningfulActivityService().weekly_active_users()})


@mvp_success_bp.route("/revenue", methods=["POST"])
def record_revenue():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    event = MeteredRevenueService().record(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        action_id=data.get("action_id"),
        direct_platform_cost=float(data.get("direct_platform_cost") or 0),
        payer_type=data.get("payer_type") or "individual",
        revenue_category=data.get("revenue_category") or "metered_individual_usage",
        currency=data.get("currency") or "EUR",
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "revenue_event": event.to_dict()}), 201


@mvp_success_bp.route("/revenue", methods=["GET"])
def list_revenue():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = MeteredRevenueEvent.query.filter_by(user_id=user.id).order_by(MeteredRevenueEvent.created_at.desc()).limit(100).all()
    return jsonify({"success": True, "revenue_events": [record.to_dict() for record in records]})


@mvp_success_bp.route("/revenue/monthly-metered", methods=["GET"])
def monthly_revenue():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    return jsonify({"success": True, "monthly_metered_revenue": MeteredRevenueService().monthly_repeatable_metered_revenue()})


@mvp_success_bp.route("/readiness-snapshots", methods=["POST"])
def create_readiness_snapshot():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    snapshot = ReadinessImpactService().create_snapshot(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        snapshot_type=data.get("snapshot_type") or "periodic",
        financial_runway_score=float(data.get("financial_runway_score") or 0),
        time_capacity_score=float(data.get("time_capacity_score") or 0),
        idea_clarity_score=float(data.get("idea_clarity_score") or 0),
        market_evidence_score=float(data.get("market_evidence_score") or 0),
        business_model_score=float(data.get("business_model_score") or 0),
        real_world_execution_score=float(data.get("real_world_execution_score") or 0),
        risk_reduction_score=float(data.get("risk_reduction_score") or 0),
        source=data.get("source") or "manual_api",
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "readiness_snapshot": snapshot.to_dict()}), 201


@mvp_success_bp.route("/readiness-snapshots", methods=["GET"])
def list_readiness_snapshots():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = ReadinessSnapshot.query.filter_by(user_id=user.id).order_by(ReadinessSnapshot.created_at.desc()).limit(100).all()
    return jsonify({"success": True, "readiness_snapshots": [record.to_dict() for record in records]})


@mvp_success_bp.route("/readiness-improvement", methods=["GET"])
def readiness_improvement():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    venture_id = request.args.get("venture_id", type=int)
    days = request.args.get("days", default=90, type=int)
    result = ReadinessImpactService().readiness_improvement(user_id=user.id, venture_id=venture_id, days=days)
    return jsonify({"success": True, "readiness_improvement": result})


@mvp_success_bp.route("/hard-blockers", methods=["POST"])
def record_hard_blocker():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    metric = HardBlockerMetricsService().record(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        blocker_type=data.get("blocker_type") or "general",
        blocked_action_type=data.get("blocked_action_type") or "unknown",
        controlled_by_platform=bool(data.get("controlled_by_platform", True)),
        enforcement_status=data.get("enforcement_status") or "blocked",
        user_reported_external_proceeded=data.get("user_reported_external_proceeded"),
        risk_period_days=int(data.get("risk_period_days") or 30),
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "hard_blocker_metric": metric.to_dict()}), 201


@mvp_success_bp.route("/hard-blockers", methods=["GET"])
def list_hard_blockers():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = HardBlockerMetric.query.filter_by(user_id=user.id).order_by(HardBlockerMetric.created_at.desc()).limit(100).all()
    return jsonify({"success": True, "hard_blocker_metrics": [record.to_dict() for record in records]})


@mvp_success_bp.route("/hard-blockers/summary", methods=["GET"])
def hard_blocker_summary():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    days = request.args.get("days", default=30, type=int)
    return jsonify({"success": True, "hard_blocker_summary": HardBlockerMetricsService().summary(days=days)})


@mvp_success_bp.route("/venture-continuation", methods=["POST"])
def record_venture_continuation():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    record = VentureContinuationService().record(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        status=data.get("status") or "unknown",
        report_period_month=int(data.get("report_period_month") or 12),
        report_summary=data.get("report_summary"),
        responsible_outcome=bool(data.get("responsible_outcome", False)),
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "venture_continuation_status": record.to_dict()}), 201


@mvp_success_bp.route("/venture-continuation", methods=["GET"])
def list_venture_continuation():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = VentureContinuationStatus.query.filter_by(user_id=user.id).order_by(VentureContinuationStatus.created_at.desc()).limit(100).all()
    return jsonify({"success": True, "venture_continuation_statuses": [record.to_dict() for record in records]})
