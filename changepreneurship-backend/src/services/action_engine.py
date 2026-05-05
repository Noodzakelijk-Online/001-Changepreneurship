"""Trusted Action System service.

Provides lifecycle operations for proposed actions. This is intentionally
integration-agnostic: real external execution can plug in later while the MVP
already preserves proposal, approval, mock execution, and audit history.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.models.assessment import db
from src.models.mvp_infrastructure import UserAction


VALID_TRANSITIONS = {
    "proposed": {"approved", "rejected", "cancelled", "edited"},
    "edited": {"approved", "rejected", "cancelled", "edited"},
    "approved": {"executing", "cancelled"},
    "executing": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
    "rejected": set(),
    "cancelled": set(),
}


class ActionStateError(ValueError):
    pass


class ActionEngine:
    def propose_action(
        self,
        *,
        user_id: int,
        action_type: str,
        title: str,
        venture_id: Optional[int] = None,
        description: Optional[str] = None,
        proposed_content: Optional[Dict[str, Any]] = None,
        external_platform: Optional[str] = None,
        external_account_id: Optional[int] = None,
        estimated_cost: Optional[float] = None,
    ) -> UserAction:
        action = UserAction(
            user_id=user_id,
            venture_id=venture_id,
            action_type=action_type,
            title=title,
            description=description,
            external_platform=external_platform,
            external_account_id=external_account_id,
            estimated_cost=estimated_cost,
            status="proposed",
        )
        action.set_proposed_content(proposed_content or {})
        action.append_audit("proposed", actor_user_id=user_id, payload={"action_type": action_type})
        db.session.add(action)
        db.session.commit()
        return action

    def edit_action(self, *, action: UserAction, user_id: int, approved_content: Dict[str, Any]) -> UserAction:
        self._assert_transition(action.status, "edited")
        action.status = "edited"
        action.set_approved_content(approved_content)
        action.append_audit("edited", actor_user_id=user_id, payload={"approved_content": approved_content})
        db.session.commit()
        return action

    def approve_action(self, *, action: UserAction, user_id: int, approved_content: Optional[Dict[str, Any]] = None) -> UserAction:
        self._assert_transition(action.status, "approved")
        action.status = "approved"
        action.approved_at = datetime.utcnow()
        action.set_approved_content(approved_content or action.get_approved_content() or action.get_proposed_content())
        action.append_audit("approved", actor_user_id=user_id)
        db.session.commit()
        return action

    def reject_action(self, *, action: UserAction, user_id: int, reason: Optional[str] = None) -> UserAction:
        self._assert_transition(action.status, "rejected")
        action.status = "rejected"
        action.append_audit("rejected", actor_user_id=user_id, payload={"reason": reason})
        db.session.commit()
        return action

    def cancel_action(self, *, action: UserAction, user_id: int, reason: Optional[str] = None) -> UserAction:
        self._assert_transition(action.status, "cancelled")
        action.status = "cancelled"
        action.append_audit("cancelled", actor_user_id=user_id, payload={"reason": reason})
        db.session.commit()
        return action

    def execute_mock_action(self, *, action: UserAction, user_id: int, result: Optional[Dict[str, Any]] = None) -> UserAction:
        """Mock/manual execution for MVP infrastructure testing.

        Real external integrations should replace this with platform-specific
        executors while preserving the same UserAction lifecycle.
        """
        self._assert_transition(action.status, "executing")
        action.status = "executing"
        action.executed_at = datetime.utcnow()
        action.append_audit("executing", actor_user_id=user_id, payload={"mode": "mock"})

        action.status = "completed"
        action.actual_cost = action.estimated_cost or 0.0
        action.append_audit("completed", actor_user_id=user_id, payload=result or {"result": "mock_completed"})
        db.session.commit()
        return action

    def fail_action(self, *, action: UserAction, user_id: int, error_message: str) -> UserAction:
        self._assert_transition(action.status, "failed")
        action.status = "failed"
        action.error_message = error_message
        action.append_audit("failed", actor_user_id=user_id, payload={"error": error_message})
        db.session.commit()
        return action

    def _assert_transition(self, current: str, target: str) -> None:
        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ActionStateError(f"Invalid action transition: {current} -> {target}")
