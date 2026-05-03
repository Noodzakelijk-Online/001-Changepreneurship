"""Mentor source routing API.

Provides a first-class way for Changepreneurship to recommend free or low-cost
mentor platforms as the next logical step, without implementing external OAuth/API
connections yet.
"""

from flask import Blueprint, jsonify, request

from src.models.mvp_infrastructure import FounderReadinessProfile
from src.services.action_engine import ActionEngine
from src.services.mentor_source_router import MentorSourceRouter
from src.utils.auth import verify_session_token

mentor_sources_bp = Blueprint("mentor_sources", __name__)


def _current_user_or_error():
    user, session, error, status = verify_session_token()
    if error:
        return None, (jsonify(error), status)
    return user, None


@mentor_sources_bp.route("/sources", methods=["GET"])
def list_sources():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    return jsonify({"success": True, "mentor_sources": MentorSourceRouter().list_sources()})


@mentor_sources_bp.route("/recommend", methods=["POST"])
def recommend_sources():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    venture_id = data.get("venture_id")
    profile = None
    if venture_id is not None:
        profile = FounderReadinessProfile.query.filter_by(user_id=user.id, venture_id=venture_id).first()

    result = MentorSourceRouter().recommend(
        profile=profile,
        region=data.get("region"),
        venture_type=data.get("venture_type"),
        founder_type=data.get("founder_type"),
        mentor_need=data.get("mentor_need"),
        female_founder=bool(data.get("female_founder", False)),
        max_results=int(data.get("max_results") or 5),
    )
    return jsonify({"success": True, "mentor_recommendation": result})


@mentor_sources_bp.route("/propose-outreach", methods=["POST"])
def propose_mentor_outreach():
    """Create a mentor outreach UserAction from a selected mentor source."""
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response

    data = request.get_json() or {}
    selected_source_key = data.get("selected_source_key") or "micromentor"
    payload = MentorSourceRouter().outreach_payload(
        selected_source_key=selected_source_key,
        user_goal=data.get("user_goal"),
    )

    action = ActionEngine().propose_action(
        user_id=user.id,
        venture_id=data.get("venture_id"),
        action_type="mentor_outreach",
        title=f"Prepare outreach via {payload['mentor_source_name']}",
        description="Mentor outreach is recommended as the next logical support step.",
        proposed_content=payload,
        external_platform=payload["mentor_source_key"],
        estimated_cost=0.0,
    )
    return jsonify({"success": True, "action": action.to_dict(), "mentor_payload": payload}), 201
