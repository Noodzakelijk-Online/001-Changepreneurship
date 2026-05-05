"""
AuditLogService — Sprint 4 (S4-04)
=====================================
CEO (Section 13.2): every important action must be auditable.
"Every action in the venture should be traceable and auditable."

Audit log is APPEND-ONLY. Hard delete is forbidden.
Stored in UserAction.audit_trail JSONB + optional separate audit_log table.
This service writes to UserAction.audit_trail and provides query helpers.

What is logged:
  - All routing decisions
  - All blocker events (create/resolve)
  - All UserAction state changes
  - All AI calls (input/output summary)
  - All external actions (content + outcome)
  - All consent/approval events
  - All version changes on documents
"""
import hashlib
import json
import logging
from datetime import datetime
from typing import Optional

from src.models.assessment import db
from src.models.user_action import UserAction, BlockerEvent

logger = logging.getLogger(__name__)

# Event types
EVENT_ROUTING_DECISION = 'ROUTING_DECISION'
EVENT_BLOCKER_CREATED = 'BLOCKER_CREATED'
EVENT_BLOCKER_RESOLVED = 'BLOCKER_RESOLVED'
EVENT_ACTION_STATE_CHANGE = 'ACTION_STATE_CHANGE'
EVENT_AI_CALL = 'AI_CALL'
EVENT_EXTERNAL_ACTION = 'EXTERNAL_ACTION'
EVENT_APPROVAL = 'APPROVAL'
EVENT_REJECTION = 'REJECTION'
EVENT_DOCUMENT_VERSION = 'DOCUMENT_VERSION'
EVENT_USER_CONSENT = 'USER_CONSENT'
EVENT_PHASE_GATE_CHANGE = 'PHASE_GATE_CHANGE'
EVENT_VENTURE_VERSION = 'VENTURE_VERSION'


def _audit_entry(
    event_type: str,
    user_id: int,
    entity_type: str,
    entity_id,
    details: dict,
    ai_involved: bool = False,
    external_action: bool = False,
    user_approved: bool = False,
) -> dict:
    return {
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'entity_type': entity_type,
        'entity_id': str(entity_id) if entity_id is not None else None,
        'details': details,
        'ai_involved': ai_involved,
        'external_action': external_action,
        'user_approved': user_approved,
    }


class AuditLogService:
    """
    Stateless service. Methods append to UserAction.audit_trail
    or log to application logger (for events without a parent UserAction).
    """

    def log_routing_decision(self, user_id: int, decision: dict, action_id=None):
        entry = _audit_entry(
            EVENT_ROUTING_DECISION, user_id,
            'routing_decision', action_id or 'inline',
            {'category': decision.get('category'), 'priority': decision.get('priority_level')},
        )
        if action_id:
            self._append_to_action(action_id, entry)
        logger.info("AUDIT routing_decision user=%s category=%s", user_id, decision.get('category'))

    def log_blocker_created(self, user_id: int, blocker_event: BlockerEvent):
        entry = _audit_entry(
            EVENT_BLOCKER_CREATED, user_id,
            'blocker_event', blocker_event.id,
            {
                'blocker_type': blocker_event.blocker_type,
                'severity': blocker_event.severity_level,
                'dimension': blocker_event.dimension,
            },
        )
        logger.info(
            "AUDIT blocker_created user=%s type=%s severity=%s",
            user_id, blocker_event.blocker_type, blocker_event.severity_level,
        )
        return entry

    def log_blocker_resolved(self, user_id: int, blocker_event: BlockerEvent, resolution_type: str):
        entry = _audit_entry(
            EVENT_BLOCKER_RESOLVED, user_id,
            'blocker_event', blocker_event.id,
            {
                'blocker_type': blocker_event.blocker_type,
                'resolution_type': resolution_type,
            },
        )
        logger.info(
            "AUDIT blocker_resolved user=%s type=%s resolution=%s",
            user_id, blocker_event.blocker_type, resolution_type,
        )
        return entry

    def log_action_state_change(
        self,
        action: UserAction,
        old_status: str,
        new_status: str,
        actor: str,
        notes: str = '',
    ):
        """Appends to action.audit_trail."""
        entry = _audit_entry(
            EVENT_ACTION_STATE_CHANGE, action.user_id,
            'user_action', action.id,
            {
                'old_status': old_status,
                'new_status': new_status,
                'actor': actor,
                'notes': notes,
            },
            user_approved=(new_status == 'APPROVED'),
        )
        self._append_to_action(action.id, entry)
        return entry

    def log_ai_call(
        self,
        user_id: int,
        task_type: str,
        input_summary: str,
        output_summary: str,
        confidence: str = 'LOW',
        action_id=None,
    ):
        entry = _audit_entry(
            EVENT_AI_CALL, user_id,
            'ai_call', action_id or 'inline',
            {
                'task_type': task_type,
                'input_summary': input_summary[:200],
                'output_summary': output_summary[:200],
                'confidence': confidence,
            },
            ai_involved=True,
        )
        if action_id:
            self._append_to_action(action_id, entry)
        logger.info("AUDIT ai_call user=%s task=%s confidence=%s", user_id, task_type, confidence)
        return entry

    def log_external_action(
        self,
        action: UserAction,
        platform: str,
        content_preview: str,
        outcome: str,
    ):
        entry = _audit_entry(
            EVENT_EXTERNAL_ACTION, action.user_id,
            'user_action', action.id,
            {
                'platform': platform,
                'content_hash': _hash(content_preview),
                'outcome': outcome,
            },
            external_action=True,
            user_approved=True,
        )
        self._append_to_action(action.id, entry)
        return entry

    def log_approval(self, action: UserAction, approver: str):
        entry = _audit_entry(
            EVENT_APPROVAL, action.user_id,
            'user_action', action.id,
            {'approver': approver, 'action_type': action.action_type},
            user_approved=True,
        )
        self._append_to_action(action.id, entry)

    def log_rejection(self, action: UserAction, rejector: str, reason: str):
        entry = _audit_entry(
            EVENT_REJECTION, action.user_id,
            'user_action', action.id,
            {'rejector': rejector, 'reason': reason, 'action_type': action.action_type},
        )
        self._append_to_action(action.id, entry)

    def log_document_version(
        self,
        user_id: int,
        document_type: str,
        document_id,
        old_version: int,
        new_version: int,
        change_summary: str,
    ):
        entry = _audit_entry(
            EVENT_DOCUMENT_VERSION, user_id,
            document_type, document_id,
            {
                'old_version': old_version,
                'new_version': new_version,
                'change_summary': change_summary[:300],
            },
        )
        logger.info(
            "AUDIT document_version user=%s doc=%s v%s→v%s",
            user_id, document_type, old_version, new_version,
        )
        return entry

    def get_user_action_history(self, user_id: int, limit: int = 50) -> list:
        """Get recent user actions with audit trails."""
        actions = (
            UserAction.query
            .filter_by(user_id=user_id)
            .order_by(UserAction.proposed_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'id': a.id,
                'action_type': a.action_type,
                'approval_status': a.approval_status,
                'proposed_at': a.proposed_at.isoformat() if a.proposed_at else None,
                'executed_at': a.executed_at.isoformat() if a.executed_at else None,
                'audit_trail': a.audit_trail or [],
            }
            for a in actions
        ]

    # ------------------------------------------------------------------
    def _append_to_action(self, action_id, entry: dict):
        """Append audit entry to UserAction.audit_trail (JSONB)."""
        try:
            action = UserAction.query.get(action_id)
            if action:
                trail = list(action.audit_trail or [])
                trail.append(entry)
                action.audit_trail = trail
                db.session.commit()
        except Exception as exc:
            logger.warning("AuditLogService failed to append entry: %s", exc)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]
