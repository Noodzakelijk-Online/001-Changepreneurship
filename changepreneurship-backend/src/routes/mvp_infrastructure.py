"""MVP infrastructure API routes.

These routes expose the first diagnosis-to-action loop without real external
integrations yet:

1. Create/update a structured readiness profile.
2. Run the rule-based path decision engine.
3. Turn a decision into a proposed UserAction.
4. Approve/edit/reject/cancel/mock-execute the action.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request

from src.models.assessment import db
from src.models.mvp_infrastructure import (
    DataConsentLog,
    ExternalConnection,
    FounderReadinessProfile,
    PhaseGate,
    UserAction,
    Venture,
)
from src.services.action_engine import ActionEngine, ActionStateError
from src.services.assessment_to_mvp_adapter import AssessmentToMVPAdapter
from src.services.path_decision_engine import PathDecisionEngine
from src.utils.auth import verify_session_token

mvp_bp = Blueprint("mvp_infrastructure", __name__)


def _current_user_or_error():
    user, session, error, status = verify_session_token()
    if error:
        return None, (jsonify(error), status)
    return user, None


def _get_user_action_or_404(action_id: int, user_id: int):
    action = UserAction.query.filter_by(id=action_id, user_id=user_id).first()
    if not action:
        return None, (jsonify({"error": "Action not found"}), 404)
    return action, None


@mvp_bp.route("/bootstrap-from-assessment", methods=["POST"])
def bootstrap_from_assessment():
    """Connect existing assessment responses to the MVP readiness/action layer."""
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    venture_id = data.get("venture_id")
    create_action = bool(data.get("create_action", False))

    try:
        venture, profile, decision, gate = AssessmentToMVPAdapter().bootstrap(
            user_id=user.id,
            venture_id=venture_id,
        )
        response = {
            "success": True,
            "venture": venture.to_dict(),
            "readiness_profile": profile.to_dict(),
            "decision": decision.to_dict(),
            "phase_gate": gate.to_dict() if gate else None,
        }

        if create_action:
            action = ActionEngine().propose_action(
                user_id=user.id,
                venture_id=venture.id,
                action_type=decision.next_action_type,
                title=decision.recommended_action_title or "Recommended next action",
                description=decision.explanation,
                proposed_content=decision.recommended_action_payload or {},
            )
            response["action"] = action.to_dict()

        return jsonify(response)
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500


@mvp_bp.route("/ventures", methods=["POST"])
def create_venture():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    venture = Venture(
        user_id=user.id,
        name=data.get("name") or "Untitled venture",
        venture_type=data.get("venture_type"),
        stage=data.get("stage") or "self_discovery",
        status=data.get("status") or "active",
    )
    db.session.add(venture)
    db.session.commit()
    return jsonify({"success": True, "venture": venture.to_dict()}), 201


@mvp_bp.route("/ventures", methods=["GET"])
def list_ventures():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    ventures = Venture.query.filter_by(user_id=user.id).order_by(Venture.created_at.desc()).all()
    return jsonify({"success": True, "ventures": [venture.to_dict() for venture in ventures]})


@mvp_bp.route("/readiness-profile", methods=["POST"])
def upsert_readiness_profile():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    venture_id = data.get("venture_id")

    profile = FounderReadinessProfile.query.filter_by(user_id=user.id, venture_id=venture_id).first()
    if not profile:
        profile = FounderReadinessProfile(user_id=user.id, venture_id=venture_id)
        db.session.add(profile)

    for dimension, payload in (data.get("dimensions") or {}).items():
        if dimension in FounderReadinessProfile.DIMENSIONS:
            profile.set_dimension(dimension, payload or {})

    for field in [
        "venture_readiness_status",
        "risk_level",
        "evidence_confidence",
        "next_step_eligibility",
        "external_readiness_status",
        "survival_risk_indicator",
        "founder_venture_fit_status",
        "route_confidence",
        "founder_type",
        "routing_state",
        "summary",
    ]:
        if field in data:
            setattr(profile, field, data.get(field))

    db.session.commit()
    return jsonify({"success": True, "readiness_profile": profile.to_dict()})


@mvp_bp.route("/readiness-profile", methods=["GET"])
def get_readiness_profile():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    venture_id = request.args.get("venture_id", type=int)
    profile = FounderReadinessProfile.query.filter_by(user_id=user.id, venture_id=venture_id).first()
    if not profile:
        return jsonify({"error": "Readiness profile not found"}), 404
    return jsonify({"success": True, "readiness_profile": profile.to_dict()})


@mvp_bp.route("/decide-next-step", methods=["POST"])
def decide_next_step():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    venture_id = data.get("venture_id")
    create_action = bool(data.get("create_action", False))

    profile = FounderReadinessProfile.query.filter_by(user_id=user.id, venture_id=venture_id).first()
    if not profile:
        return jsonify({"error": "Readiness profile required before decision"}), 400

    decision = PathDecisionEngine().decide(profile)
    response = {"success": True, "decision": decision.to_dict()}

    if create_action:
        action = ActionEngine().propose_action(
            user_id=user.id,
            venture_id=venture_id,
            action_type=decision.next_action_type,
            title=decision.recommended_action_title or "Recommended next action",
            description=decision.explanation,
            proposed_content=decision.recommended_action_payload or {},
        )
        response["action"] = action.to_dict()

    return jsonify(response)


@mvp_bp.route("/phase-gates", methods=["POST"])
def create_phase_gate():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    gate = PhaseGate(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        phase_id=data.get("phase_id") or "self_discovery",
        gate_status=data.get("gate_status") or "open",
        blocking_dimension=data.get("blocking_dimension"),
        blocking_reason=data.get("blocking_reason"),
        unlock_condition=data.get("unlock_condition"),
    )
    db.session.add(gate)
    db.session.commit()
    return jsonify({"success": True, "phase_gate": gate.to_dict()}), 201


@mvp_bp.route("/phase-gates", methods=["GET"])
def list_phase_gates():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    venture_id = request.args.get("venture_id", type=int)
    query = PhaseGate.query.filter_by(user_id=user.id)
    if venture_id:
        query = query.filter_by(venture_id=venture_id)
    gates = query.order_by(PhaseGate.created_at.desc()).all()
    return jsonify({"success": True, "phase_gates": [gate.to_dict() for gate in gates]})


@mvp_bp.route("/actions", methods=["POST"])
def propose_action():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    if not data.get("action_type") or not data.get("title"):
        return jsonify({"error": "action_type and title are required"}), 400

    action = ActionEngine().propose_action(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        action_type=data["action_type"],
        title=data["title"],
        description=data.get("description"),
        proposed_content=data.get("proposed_content") or {},
        external_platform=data.get("external_platform"),
        external_account_id=data.get("external_account_id"),
        estimated_cost=data.get("estimated_cost"),
    )
    return jsonify({"success": True, "action": action.to_dict()}), 201


@mvp_bp.route("/actions", methods=["GET"])
def list_actions():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    venture_id = request.args.get("venture_id", type=int)
    query = UserAction.query.filter_by(user_id=user.id)
    if venture_id:
        query = query.filter_by(venture_id=venture_id)
    actions = query.order_by(UserAction.created_at.desc()).all()
    return jsonify({"success": True, "actions": [action.to_dict() for action in actions]})


@mvp_bp.route("/actions/<int:action_id>", methods=["GET"])
def get_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response
    return jsonify({"success": True, "action": action.to_dict()})


@mvp_bp.route("/actions/<int:action_id>/edit", methods=["POST"])
def edit_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response

    data = request.get_json() or {}
    try:
        action = ActionEngine().edit_action(
            action=action,
            user_id=user.id,
            approved_content=data.get("approved_content") or {},
        )
        return jsonify({"success": True, "action": action.to_dict()})
    except ActionStateError as exc:
        return jsonify({"error": str(exc)}), 409


@mvp_bp.route("/actions/<int:action_id>/approve", methods=["POST"])
def approve_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response

    data = request.get_json() or {}
    try:
        action = ActionEngine().approve_action(
            action=action,
            user_id=user.id,
            approved_content=data.get("approved_content"),
        )
        return jsonify({"success": True, "action": action.to_dict()})
    except ActionStateError as exc:
        return jsonify({"error": str(exc)}), 409


@mvp_bp.route("/actions/<int:action_id>/reject", methods=["POST"])
def reject_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response

    data = request.get_json() or {}
    try:
        action = ActionEngine().reject_action(action=action, user_id=user.id, reason=data.get("reason"))
        return jsonify({"success": True, "action": action.to_dict()})
    except ActionStateError as exc:
        return jsonify({"error": str(exc)}), 409


@mvp_bp.route("/actions/<int:action_id>/cancel", methods=["POST"])
def cancel_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response

    data = request.get_json() or {}
    try:
        action = ActionEngine().cancel_action(action=action, user_id=user.id, reason=data.get("reason"))
        return jsonify({"success": True, "action": action.to_dict()})
    except ActionStateError as exc:
        return jsonify({"error": str(exc)}), 409


@mvp_bp.route("/actions/<int:action_id>/execute-mock", methods=["POST"])
def execute_mock_action(action_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    action, error_response = _get_user_action_or_404(action_id, user.id)
    if error_response:
        return error_response

    data = request.get_json() or {}
    try:
        action = ActionEngine().execute_mock_action(
            action=action,
            user_id=user.id,
            result=data.get("result") or {"result": "mock_completed"},
        )
        return jsonify({"success": True, "action": action.to_dict()})
    except ActionStateError as exc:
        return jsonify({"error": str(exc)}), 409


@mvp_bp.route("/external-connections/stub", methods=["POST"])
def create_external_connection_stub():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    if not data.get("platform"):
        return jsonify({"error": "platform is required"}), 400

    connection = ExternalConnection(
        user_id=user.id,
        platform=data["platform"],
        connection_status=data.get("connection_status") or "stub",
        scope=data.get("scope"),
        permission_level=data.get("permission_level") or 1,
        connected_at=datetime.utcnow() if data.get("connection_status") == "connected" else None,
    )
    db.session.add(connection)
    db.session.commit()
    return jsonify({"success": True, "external_connection": connection.to_dict()}), 201


@mvp_bp.route("/external-connections", methods=["GET"])
def list_external_connections():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    connections = ExternalConnection.query.filter_by(user_id=user.id).order_by(ExternalConnection.created_at.desc()).all()
    return jsonify({"success": True, "external_connections": [connection.to_dict() for connection in connections]})


@mvp_bp.route("/consent", methods=["POST"])
def record_consent():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    if not data.get("data_category"):
        return jsonify({"error": "data_category is required"}), 400

    consent_given = bool(data.get("consent_given"))
    consent = DataConsentLog(
        user_id=user.id,
        data_category=data["data_category"],
        consent_given=consent_given,
        consent_text_version=data.get("consent_text_version") or "mvp-v1",
        legal_basis=data.get("legal_basis") or "explicit_consent",
        consented_at=datetime.utcnow() if consent_given else None,
        revoked_at=datetime.utcnow() if not consent_given else None,
    )
    db.session.add(consent)
    db.session.commit()
    return jsonify({"success": True, "consent": consent.to_dict()}), 201


@mvp_bp.route("/consent", methods=["GET"])
def list_consent():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    logs = DataConsentLog.query.filter_by(user_id=user.id).order_by(DataConsentLog.created_at.desc()).all()
    return jsonify({"success": True, "consent_logs": [log.to_dict() for log in logs]})
