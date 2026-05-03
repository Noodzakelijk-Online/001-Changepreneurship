"""Routes for codable MVP logic requirements.

These endpoints expose the document-derived policy models/services without
requiring real external integrations. They are meant for backend testing and for a
future frontend action-review/admin view.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request

from src.models.assessment import db
from src.models.mvp_infrastructure import FounderReadinessProfile, UserAction
from src.models.mvp_logic import (
    ActionOutcome,
    ActionPermissionPolicy,
    AssumptionRecord,
    BenchmarkEvent,
    CostEstimate,
    EvidenceRecord,
    ProfessionalReviewRequirement,
    SpendingCap,
    UserFitAssessment,
    VentureConnectionMode,
)
from src.services.mvp_policies import (
    AIBoundaryPolicy,
    AssumptionPolicy,
    BlockerPolicy,
    ConnectionModeService,
    CostEstimateService,
    EvidencePolicy,
    FounderTypeClassifier,
    OutcomeService,
    PermissionPolicyService,
    ProfessionalReviewService,
    SpendingCapService,
    UserFitClassifier,
)
from src.utils.auth import verify_session_token

mvp_logic_bp = Blueprint("mvp_logic", __name__)


def _current_user_or_error():
    user, session, error, status = verify_session_token()
    if error:
        return None, (jsonify(error), status)
    return user, None


def _action_or_404(action_id: int, user_id: int):
    action = UserAction.query.filter_by(id=action_id, user_id=user_id).first()
    if not action:
        return None, (jsonify({"error": "Action not found"}), 404)
    return action, None


@mvp_logic_bp.route("/blocker-message", methods=["POST"])
def create_blocker_message():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    message = BlockerPolicy().message(
        blocked_action=data.get("blocked_action") or "unsafe action",
        reason=data.get("reason") or "A platform safety rule requires this action to be delayed.",
        risk_explanation=data.get("risk_explanation") or "Proceeding now may create avoidable harm or unreliable progress.",
        unlock_condition=data.get("unlock_condition") or "Resolve the blocker and provide enough evidence to proceed.",
        blocker_category=data.get("blocker_category") or "market_demand_or_evidence_quality",
        severity=data.get("severity") or "warning",
        allowed_actions=data.get("allowed_actions") or None,
    )
    return jsonify({"success": True, "blocker_message": {**message.to_dict(), "user_facing_message": message.user_facing_message}})


@mvp_logic_bp.route("/evidence", methods=["POST"])
def create_evidence():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    if not data.get("claim"):
        return jsonify({"error": "claim is required"}), 400
    record = EvidencePolicy().create_evidence(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        claim=data["claim"],
        evidence_type=data.get("evidence_type") or "general",
        source=data.get("source"),
        evidence_strength=data.get("evidence_strength") or "assumption",
        confidence=data.get("confidence") or "low",
        metadata=data.get("metadata") or {},
    )
    return jsonify({"success": True, "evidence": record.to_dict()}), 201


@mvp_logic_bp.route("/evidence", methods=["GET"])
def list_evidence():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    venture_id = request.args.get("venture_id", type=int)
    query = EvidenceRecord.query.filter_by(user_id=user.id)
    if venture_id:
        query = query.filter_by(venture_id=venture_id)
    records = query.order_by(EvidenceRecord.created_at.desc()).all()
    return jsonify({"success": True, "evidence": [record.to_dict() for record in records]})


@mvp_logic_bp.route("/evidence/guard-claim", methods=["POST"])
def guard_claim():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    result = EvidencePolicy().guard_claim(
        venture_id=data.get("venture_id"),
        claim_text=data.get("claim_text") or "",
        required_strength=data.get("required_strength") or "partial_validation",
    )
    return jsonify({"success": True, "guard": result})


@mvp_logic_bp.route("/assumptions", methods=["POST"])
def create_assumption():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    if not data.get("assumption_text"):
        return jsonify({"error": "assumption_text is required"}), 400
    assumption = AssumptionPolicy().create_assumption(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        assumption_text=data["assumption_text"],
        category=data.get("category") or "general",
        risk_level=data.get("risk_level") or "medium",
    )
    return jsonify({"success": True, "assumption": assumption.to_dict()}), 201


@mvp_logic_bp.route("/assumptions", methods=["GET"])
def list_assumptions():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    venture_id = request.args.get("venture_id", type=int)
    query = AssumptionRecord.query.filter_by(user_id=user.id)
    if venture_id:
        query = query.filter_by(venture_id=venture_id)
    assumptions = query.order_by(AssumptionRecord.created_at.desc()).all()
    return jsonify({"success": True, "assumptions": [assumption.to_dict() for assumption in assumptions]})


@mvp_logic_bp.route("/assumptions/<int:assumption_id>/validation-action", methods=["POST"])
def assumption_validation_action(assumption_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    assumption = AssumptionRecord.query.filter_by(id=assumption_id, user_id=user.id).first()
    if not assumption:
        return jsonify({"error": "Assumption not found"}), 404
    payload = AssumptionPolicy().validation_action_payload(assumption)
    return jsonify({"success": True, "validation_action_payload": payload})


@mvp_logic_bp.route("/founder-type", methods=["POST"])
def classify_founder_type():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    profile = FounderReadinessProfile.query.filter_by(user_id=user.id, venture_id=data.get("venture_id")).first()
    if not profile:
        return jsonify({"error": "Readiness profile required"}), 400
    result = FounderTypeClassifier().classify(profile)
    profile.founder_type = result["founder_type"]
    db.session.commit()
    return jsonify({"success": True, "founder_type": result})


@mvp_logic_bp.route("/user-fit", methods=["POST"])
def classify_user_fit():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    assessment = UserFitClassifier().classify_from_text(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        text=data.get("text") or "",
    )
    return jsonify({"success": True, "user_fit": assessment.to_dict()}), 201


@mvp_logic_bp.route("/user-fit", methods=["GET"])
def list_user_fit():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = UserFitAssessment.query.filter_by(user_id=user.id).order_by(UserFitAssessment.created_at.desc()).all()
    return jsonify({"success": True, "user_fit_assessments": [record.to_dict() for record in records]})


@mvp_logic_bp.route("/actions/<int:action_id>/permission-policy", methods=["POST"])
def create_action_permission(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    action, error_response = _action_or_404(action_id, user.id)
    if error_response:
        return error_response
    data = request.get_json() or {}
    policy = PermissionPolicyService().create_for_action(
        action=action,
        permission_scope=data.get("permission_scope") or "prepare",
        execution_mode=data.get("execution_mode") or "manual",
        allowed_operations=data.get("allowed_operations"),
    )
    return jsonify({"success": True, "permission_policy": policy.to_dict()}), 201


@mvp_logic_bp.route("/actions/<int:action_id>/can-execute", methods=["GET"])
def can_execute_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    action, error_response = _action_or_404(action_id, user.id)
    if error_response:
        return error_response
    return jsonify({"success": True, "execution_check": PermissionPolicyService().can_execute(action)})


@mvp_logic_bp.route("/actions/<int:action_id>/outcome", methods=["POST"])
def record_action_outcome(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    action, error_response = _action_or_404(action_id, user.id)
    if error_response:
        return error_response
    data = request.get_json() or {}
    follow_up = None
    if data.get("next_follow_up_at"):
        follow_up = datetime.fromisoformat(data["next_follow_up_at"])
    outcome = OutcomeService().record(
        action=action,
        outcome_status=data.get("outcome_status") or "completed",
        outcome_summary=data.get("outcome_summary"),
        next_recommended_action_type=data.get("next_recommended_action_type"),
        next_follow_up_at=follow_up,
    )
    return jsonify({"success": True, "outcome": outcome.to_dict()}), 201


@mvp_logic_bp.route("/actions/<int:action_id>/outcomes", methods=["GET"])
def list_action_outcomes(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    action, error_response = _action_or_404(action_id, user.id)
    if error_response:
        return error_response
    outcomes = ActionOutcome.query.filter_by(action_id=action.id, user_id=user.id).order_by(ActionOutcome.created_at.desc()).all()
    return jsonify({"success": True, "outcomes": [outcome.to_dict() for outcome in outcomes]})


@mvp_logic_bp.route("/benchmark-events", methods=["GET"])
def list_benchmark_events():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    events = BenchmarkEvent.query.filter_by(user_id=user.id).order_by(BenchmarkEvent.created_at.desc()).all()
    return jsonify({"success": True, "benchmark_events": [event.to_dict() for event in events]})


@mvp_logic_bp.route("/cost-estimates", methods=["POST"])
def create_cost_estimate():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    direct_cost = float(data.get("estimated_direct_cost") or 0)
    estimate = CostEstimateService().create_estimate(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        action_id=data.get("action_id"),
        estimated_direct_cost=direct_cost,
        currency=data.get("currency") or "EUR",
    )
    return jsonify({"success": True, "cost_estimate": estimate.to_dict()}), 201


@mvp_logic_bp.route("/cost-estimates", methods=["GET"])
def list_cost_estimates():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    records = CostEstimate.query.filter_by(user_id=user.id).order_by(CostEstimate.created_at.desc()).all()
    return jsonify({"success": True, "cost_estimates": [record.to_dict() for record in records]})


@mvp_logic_bp.route("/spending-caps", methods=["POST"])
def create_spending_cap():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    cap = SpendingCapService().create_cap(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        amount=float(data.get("amount") or 0),
        cap_type=data.get("cap_type") or "per_action",
        currency=data.get("currency") or "EUR",
    )
    return jsonify({"success": True, "spending_cap": cap.to_dict()}), 201


@mvp_logic_bp.route("/spending-caps/check", methods=["POST"])
def check_spending_cap():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    result = SpendingCapService().check_per_action_cap(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        billed_price=float(data.get("billed_price") or 0),
    )
    return jsonify({"success": True, "spending_cap_check": result})


@mvp_logic_bp.route("/ai-boundary/evaluate-action", methods=["POST"])
def evaluate_ai_action():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    result = AIBoundaryPolicy().evaluate_generated_action(
        action_payload=data.get("action_payload") or {},
        venture_id=data.get("venture_id"),
    )
    return jsonify({"success": True, "ai_boundary_check": result})


@mvp_logic_bp.route("/professional-review/detect", methods=["POST"])
def detect_professional_review():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    requirements = ProfessionalReviewService().detect_and_create(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        text=data.get("text") or "",
        action_type=data.get("action_type"),
    )
    return jsonify({"success": True, "requirements": [req.to_dict() for req in requirements]})


@mvp_logic_bp.route("/professional-review/check", methods=["POST"])
def check_professional_review():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    result = ProfessionalReviewService().is_satisfied_for_action(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        action_type=data.get("action_type") or "general",
    )
    return jsonify({"success": True, "professional_review_check": result})


@mvp_logic_bp.route("/connection-mode", methods=["POST"])
def set_connection_mode():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data = request.get_json() or {}
    mode = ConnectionModeService().set_mode(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        mode=data.get("connection_mode") or "manual_mode",
        explanation=data.get("explanation"),
    )
    return jsonify({"success": True, "connection_mode": mode.to_dict()}), 201


@mvp_logic_bp.route("/connection-mode", methods=["GET"])
def get_connection_mode():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    venture_id = request.args.get("venture_id", type=int)
    return jsonify({"success": True, "connection_mode": ConnectionModeService().current_mode(user_id=user.id, venture_id=venture_id)})
