"""
UserAction and BlockerEvent models — Sprint 2.

UserAction: Trusted Action System state machine (CEO Section 13.2).
  PROPOSED → REVIEWED → APPROVED → QUEUED → EXECUTED → OUTCOME_RECORDED
  OR:                   → REJECTED
  OR:                   → EXPIRED / FAILED / CANCELLED

BlockerEvent: Immutable audit record of every blocker activation.
  Written by Layer 1 (Rule Engine / PathDecisionEngine).
  Never deleted — resolved_at is set when blocker is cleared.
"""
import hashlib
import json
from datetime import datetime

from src.models.assessment import db


# ---------------------------------------------------------------------------
# UserAction
# ---------------------------------------------------------------------------
# Valid state transitions — enforced in service layer
VALID_TRANSITIONS = {
    'PROPOSED':          {'REVIEWED', 'REJECTED', 'EXPIRED', 'CANCELLED'},
    'REVIEWED':          {'APPROVED', 'REJECTED', 'EXPIRED'},
    'APPROVED':          {'QUEUED', 'CANCELLED'},
    'QUEUED':            {'EXECUTED', 'FAILED', 'CANCELLED'},
    'EXECUTED':          {'OUTCOME_RECORDED', 'FAILED'},
    'OUTCOME_RECORDED':  set(),   # terminal
    'REJECTED':          set(),   # terminal
    'EXPIRED':           set(),   # terminal
    'FAILED':            set(),   # terminal
    'CANCELLED':         set(),   # terminal
}

# Actions that require explicit user approval (CEO Section 13.2)
REQUIRES_APPROVAL = {
    'SEND_MESSAGE',
    'SUBMIT_APPLICATION',
    'CHANGE_PROFILE',
    'SEND_OUTREACH',
    'POST_CONTENT',
    'HIGH_IMPACT_ACTION',
}

# Actions that are always automatic (drafts, reads, searches)
AUTO_APPROVE = {
    'DRAFT_DOCUMENT',
    'SEARCH_MENTORS',
    'DRAFT_OUTREACH',
    'DRAFT_FOLLOWUP',
    'IMPROVE_PROFILE_SUGGESTION',
}


class UserAction(db.Model):
    __tablename__ = 'user_action'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # What / why / where
    action_type = db.Column(db.String(80), nullable=False)
    action_data = db.Column(db.JSON, nullable=True)
    rationale = db.Column(db.Text, nullable=True)
    external_platform = db.Column(db.String(80), nullable=True)
    external_account_id = db.Column(db.String(255), nullable=True)
    content_hash = db.Column(db.String(64), nullable=True)  # SHA-256 for dedup

    # State machine
    approval_status = db.Column(db.String(30), nullable=False, default='PROPOSED')

    # Timestamps
    proposed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    queued_at = db.Column(db.DateTime, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=True)
    outcome_recorded_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Outputs
    result_data = db.Column(db.JSON, nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    cost_credits = db.Column(db.Integer, nullable=False, default=0)

    # Immutable audit trail (append-only list of {event, at, data})
    audit_trail = db.Column(db.JSON, nullable=False, default=list)

    # ----------------------------------------------------------------
    # Business logic helpers
    # ----------------------------------------------------------------

    @staticmethod
    def compute_content_hash(action_type: str, action_data: dict) -> str:
        """SHA-256 hash for duplicate detection."""
        payload = json.dumps({'type': action_type, 'data': action_data}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(self.approval_status, set())

    def transition(self, new_status: str, actor: str = 'system', data: dict = None) -> bool:
        """
        Attempt a state transition. Returns True on success, False if invalid.
        CEO Section 13.2: NEVER possible to reach EXECUTED without APPROVED.
        """
        if not self.can_transition_to(new_status):
            return False
        self.approval_status = new_status
        ts = datetime.utcnow()

        # Set individual timestamp columns
        ts_map = {
            'REVIEWED': 'reviewed_at',
            'APPROVED': 'approved_at',
            'QUEUED':   'queued_at',
            'EXECUTED': 'executed_at',
            'OUTCOME_RECORDED': 'outcome_recorded_at',
            'REJECTED': 'rejected_at',
        }
        col = ts_map.get(new_status)
        if col:
            setattr(self, col, ts)

        # Append to audit trail (never overwrite)
        trail = list(self.audit_trail or [])
        trail.append({
            'event': new_status,
            'at': ts.isoformat(),
            'by': actor,
            'data': data or {},
        })
        self.audit_trail = trail
        return True

    def requires_approval(self) -> bool:
        return self.action_type in REQUIRES_APPROVAL

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'approval_status': self.approval_status,
            'rationale': self.rationale,
            'external_platform': self.external_platform,
            'proposed_at': self.proposed_at.isoformat() if self.proposed_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'result_data': self.result_data,
            'requires_approval': self.requires_approval(),
            'audit_trail': self.audit_trail,
        }


# ---------------------------------------------------------------------------
# BlockerEvent
# ---------------------------------------------------------------------------
class BlockerEvent(db.Model):
    __tablename__ = 'blocker_event'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # Classification
    blocker_type = db.Column(db.String(80), nullable=False)
    dimension = db.Column(db.String(80), nullable=True)
    severity_level = db.Column(db.Integer, nullable=False)  # 0-5
    source_service = db.Column(db.String(80), nullable=True)

    # Trigger context
    trigger_signal = db.Column(db.JSON, nullable=True)
    what_is_blocked = db.Column(db.JSON, nullable=True)
    what_is_allowed = db.Column(db.JSON, nullable=True)
    unlock_condition = db.Column(db.Text, nullable=True)

    # Lifecycle
    triggered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_type = db.Column(db.String(50), nullable=True)
    # RESOLVED / OVERRIDDEN_BY_ADMIN / EXPIRED / SUPERSEDED

    # Optional FK to the assessment that triggered it
    founder_readiness_profile_id = db.Column(db.Integer, nullable=True)

    # ----------------------------------------------------------------
    def is_active(self) -> bool:
        return self.resolved_at is None

    def resolve(self, resolution_type: str = 'RESOLVED'):
        self.resolved_at = datetime.utcnow()
        self.resolution_type = resolution_type

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'blocker_type': self.blocker_type,
            'dimension': self.dimension,
            'severity_level': self.severity_level,
            'what_is_blocked': self.what_is_blocked,
            'what_is_allowed': self.what_is_allowed,
            'unlock_condition': self.unlock_condition,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'is_active': self.is_active(),
        }
