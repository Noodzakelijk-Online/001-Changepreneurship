"""
UserActionService — Sprint 4 (S4-01)
========================================
CEO (Section 13.2): Trusted Action System.
"No action is taken without the user understanding what is being done."

State machine:
  PROPOSED → REVIEWED → APPROVED → QUEUED → EXECUTED → OUTCOME_RECORDED
           → REJECTED  (from REVIEWED)
           → CANCELLED (from PROPOSED/APPROVED)
           → EXPIRED   (from PROPOSED/REVIEWED)
           → FAILED    (from QUEUED/EXECUTED)

Rules:
  - Duplicate detection (content hash). Cannot propose same action twice.
  - REQUIRES_APPROVAL actions need explicit user approve before QUEUED.
  - AUTO_APPROVE actions skip manual approval.
  - EXECUTED without APPROVED is architecturally impossible (guarded in service).
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from src.models.assessment import db
from src.models.user_action import (
    UserAction, BlockerEvent,
    VALID_TRANSITIONS, REQUIRES_APPROVAL, AUTO_APPROVE,
)
from src.services.audit_log_service import AuditLogService

logger = logging.getLogger(__name__)

_audit = AuditLogService()

# Default expiry for pending actions (72h)
ACTION_DEFAULT_EXPIRY_HOURS = 72


class UserActionService:
    """
    Core business logic for UserAction state machine.
    All methods write to DB and append audit trail.
    """

    def propose_action(
        self,
        user_id: int,
        action_type: str,
        action_data: dict,
        rationale: str = '',
        external_platform: str = None,
        cost_credits: int = 0,
    ) -> UserAction:
        """
        Create a new PROPOSED UserAction.
        Raises ValueError on duplicate (same content hash, pending).
        AUTO_APPROVE types transition immediately to APPROVED.
        """
        # Duplicate guard
        content_hash = UserAction.compute_content_hash(action_type, action_data)
        existing = UserAction.query.filter_by(
            user_id=user_id,
            content_hash=content_hash,
            approval_status='PROPOSED',
        ).first()
        if existing:
            raise ValueError(
                f'Duplicate action: {action_type} already proposed (id={existing.id})'
            )

        action = UserAction(
            user_id=user_id,
            action_type=action_type,
            action_data=action_data,
            rationale=rationale,
            external_platform=external_platform,
            content_hash=content_hash,
            approval_status='PROPOSED',
            cost_credits=cost_credits,
            expires_at=datetime.utcnow() + timedelta(hours=ACTION_DEFAULT_EXPIRY_HOURS),
            audit_trail=[],
        )
        db.session.add(action)
        db.session.flush()  # get action.id

        # Auto-review + auto-approve if eligible
        if action_type in AUTO_APPROVE:
            action.transition('REVIEWED', actor='system', data={'reason': 'auto_review'})
            action.transition('APPROVED', actor='system', data={'reason': 'auto_approve'})

        _audit.log_action_state_change(action, 'NEW', 'PROPOSED', 'system')
        db.session.commit()
        return action

    def approve_action(
        self,
        action_id: int,
        user_id: int,
        actor: str = 'user',
    ) -> UserAction:
        """
        User explicitly approves a PROPOSED/REVIEWED action.
        REQUIRES_APPROVAL: must go through this path.
        """
        action = self._get_action_for_user(action_id, user_id)

        # Transition PROPOSED → REVIEWED if needed
        if action.approval_status == 'PROPOSED':
            if not action.transition('REVIEWED', actor=actor, data={'reason': 'user_review'}):
                raise ValueError(f'Cannot transition from {action.approval_status} to REVIEWED')

        if not action.transition('APPROVED', actor=actor, data={'reason': 'user_approved'}):
            raise ValueError(f'Cannot approve action in state {action.approval_status}')

        _audit.log_approval(action, actor)
        db.session.commit()
        return action

    def reject_action(
        self,
        action_id: int,
        user_id: int,
        reason: str,
        actor: str = 'user',
    ) -> UserAction:
        """Reject a PROPOSED or REVIEWED action."""
        action = self._get_action_for_user(action_id, user_id)

        if action.approval_status == 'PROPOSED':
            action.transition('REVIEWED', actor=actor, data={'reason': 'user_review'})

        if not action.transition('REJECTED', actor=actor, data={'reason': reason}):
            raise ValueError(f'Cannot reject action in state {action.approval_status}')

        action.rejection_reason = reason
        _audit.log_rejection(action, actor, reason)
        db.session.commit()
        return action

    def queue_action(self, action_id: int) -> UserAction:
        """
        Move APPROVED action to QUEUED (ready for worker).
        CEO invariant: cannot queue without APPROVED.
        """
        action = UserAction.query.get(action_id)
        if not action:
            raise ValueError(f'Action {action_id} not found')
        if action.approval_status != 'APPROVED':
            raise ValueError(
                f'Cannot queue action in state {action.approval_status} — must be APPROVED first'
            )
        action.transition('QUEUED', actor='system', data={'reason': 'queue_worker'})
        db.session.commit()
        return action

    def mark_executed(
        self,
        action_id: int,
        result_data: dict,
        platform: str = None,
        content_preview: str = '',
    ) -> UserAction:
        """Record execution result and transition to EXECUTED."""
        action = UserAction.query.get(action_id)
        if not action:
            raise ValueError(f'Action {action_id} not found')
        if action.approval_status != 'QUEUED':
            raise ValueError(
                f'Cannot execute action in state {action.approval_status} — must be QUEUED'
            )
        action.transition('EXECUTED', actor='system', data={'result_summary': str(result_data)[:200]})
        action.result_data = result_data

        if platform and content_preview:
            _audit.log_external_action(
                action,
                platform=platform,
                content_preview=content_preview,
                outcome=result_data.get('outcome', 'UNKNOWN'),
            )

        db.session.commit()
        return action

    def record_outcome(
        self,
        action_id: int,
        outcome: str,
        outcome_data: dict = None,
    ) -> UserAction:
        """
        User or system records what actually happened (last state).
        Required for learning loop (CEO: track action effectiveness).
        """
        action = UserAction.query.get(action_id)
        if not action:
            raise ValueError(f'Action {action_id} not found')
        if action.approval_status != 'EXECUTED':
            raise ValueError(
                f'Cannot record outcome for action in state {action.approval_status}'
            )
        action.transition(
            'OUTCOME_RECORDED',
            actor='user',
            data={'outcome': outcome, 'outcome_data': outcome_data or {}},
        )
        action.result_data = {**(action.result_data or {}), 'outcome': outcome, **(outcome_data or {})}
        db.session.commit()
        return action

    def mark_failed(self, action_id: int, reason: str) -> UserAction:
        """Mark action as FAILED (from QUEUED or EXECUTED)."""
        action = UserAction.query.get(action_id)
        if not action:
            raise ValueError(f'Action {action_id} not found')
        action.transition('FAILED', actor='system', data={'reason': reason})
        action.failure_reason = reason
        db.session.commit()
        return action

    def cancel_action(self, action_id: int, user_id: int, reason: str = '') -> UserAction:
        """User cancels a pending action (PROPOSED or APPROVED only)."""
        action = self._get_action_for_user(action_id, user_id)
        if not action.transition('CANCELLED', actor='user', data={'reason': reason}):
            raise ValueError(f'Cannot cancel action in state {action.approval_status}')
        db.session.commit()
        return action

    def expire_stale_actions(self) -> int:
        """
        Background: expire PROPOSED/REVIEWED actions past expires_at.
        Returns count expired.
        """
        stale = UserAction.query.filter(
            UserAction.approval_status.in_(['PROPOSED', 'REVIEWED']),
            UserAction.expires_at < datetime.utcnow(),
        ).all()
        for action in stale:
            action.transition('EXPIRED', actor='system', data={'reason': 'ttl_exceeded'})
        db.session.commit()
        return len(stale)

    def get_pending_actions(self, user_id: int) -> list:
        """Return actions awaiting user approval."""
        actions = UserAction.query.filter(
            UserAction.user_id == user_id,
            UserAction.approval_status.in_(['PROPOSED', 'REVIEWED']),
            UserAction.action_type.in_(REQUIRES_APPROVAL),
        ).order_by(UserAction.proposed_at.desc()).all()
        return [a.to_dict() for a in actions]

    def get_action_history(self, user_id: int, limit: int = 20) -> list:
        """Return recent actions with full audit trail."""
        actions = (
            UserAction.query
            .filter_by(user_id=user_id)
            .order_by(UserAction.proposed_at.desc())
            .limit(limit)
            .all()
        )
        return [a.to_dict() for a in actions]

    # ------------------------------------------------------------------
    def _get_action_for_user(self, action_id: int, user_id: int) -> UserAction:
        action = UserAction.query.filter_by(id=action_id, user_id=user_id).first()
        if not action:
            raise ValueError(f'Action {action_id} not found or access denied')
        return action
