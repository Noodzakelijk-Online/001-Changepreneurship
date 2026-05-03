"""MVP infrastructure models for readiness, gating, consent, and trusted actions.

These models intentionally do not replace the existing assessment flow yet. They add
structured backend primitives that move Changepreneurship from a questionnaire/report
product toward the MVP loop:

    diagnose -> decide -> propose action -> user approves -> execute/record
"""

from datetime import datetime
import json
from typing import Any, Dict, Optional

from src.models.assessment import db


class JsonTextMixin:
    """Small helper for models storing JSON payloads in Text columns."""

    @staticmethod
    def _loads(value: Optional[str], fallback: Any = None) -> Any:
        if value in (None, ""):
            return {} if fallback is None else fallback
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {} if fallback is None else fallback

    @staticmethod
    def _dumps(value: Any) -> str:
        if value is None:
            return json.dumps({})
        return json.dumps(value)


class Venture(db.Model):
    """Separates the user from a specific venture/idea.

    This is deliberately light for the first infrastructure pass. It prevents the
    current codebase from permanently treating one user as one idea.
    """

    __tablename__ = "venture"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False, default="Untitled venture")
    venture_type = db.Column(db.String(80), nullable=True)
    stage = db.Column(db.String(80), nullable=False, default="self_discovery")
    status = db.Column(db.String(30), nullable=False, default="active")  # active, paused, archived, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("ventures", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "venture_type": self.venture_type,
            "stage": self.stage,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FounderReadinessProfile(db.Model, JsonTextMixin):
    """Typed readiness profile used by rule-based decisions.

    Each dimension is stored as a small JSON object, for example:
    {"status": "weak", "confidence": "medium", "evidence_note": "...", "blocker_flag": true}
    """

    __tablename__ = "founder_readiness_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)

    financial_readiness = db.Column(db.Text, nullable=False, default="{}")
    time_capacity = db.Column(db.Text, nullable=False, default="{}")
    personal_readiness = db.Column(db.Text, nullable=False, default="{}")
    skills_experience = db.Column(db.Text, nullable=False, default="{}")
    execution_behaviour = db.Column(db.Text, nullable=False, default="{}")
    evidence_discipline = db.Column(db.Text, nullable=False, default="{}")
    communication_ability = db.Column(db.Text, nullable=False, default="{}")
    support_network = db.Column(db.Text, nullable=False, default="{}")
    founder_idea_fit = db.Column(db.Text, nullable=False, default="{}")
    founder_market_fit = db.Column(db.Text, nullable=False, default="{}")
    risk_awareness = db.Column(db.Text, nullable=False, default="{}")
    operational_discipline = db.Column(db.Text, nullable=False, default="{}")
    automation_leverage = db.Column(db.Text, nullable=False, default="{}")

    venture_readiness_status = db.Column(db.String(40), nullable=False, default="unknown")
    risk_level = db.Column(db.String(40), nullable=False, default="unknown")
    evidence_confidence = db.Column(db.String(40), nullable=False, default="low")
    next_step_eligibility = db.Column(db.String(80), nullable=False, default="needs_diagnosis")
    external_readiness_status = db.Column(db.String(80), nullable=False, default="not_ready")
    survival_risk_indicator = db.Column(db.String(40), nullable=False, default="unknown")
    founder_venture_fit_status = db.Column(db.String(80), nullable=False, default="unknown")
    route_confidence = db.Column(db.String(40), nullable=False, default="low")

    founder_type = db.Column(db.String(8), nullable=True)  # Future A-P classifier
    routing_state = db.Column(db.String(80), nullable=False, default="needs_diagnosis")
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("readiness_profiles", lazy=True, cascade="all, delete-orphan"))
    venture = db.relationship("Venture", backref=db.backref("readiness_profiles", lazy=True, cascade="all, delete-orphan"))

    DIMENSIONS = [
        "financial_readiness",
        "time_capacity",
        "personal_readiness",
        "skills_experience",
        "execution_behaviour",
        "evidence_discipline",
        "communication_ability",
        "support_network",
        "founder_idea_fit",
        "founder_market_fit",
        "risk_awareness",
        "operational_discipline",
        "automation_leverage",
    ]

    def get_dimension(self, name: str) -> Dict[str, Any]:
        if name not in self.DIMENSIONS:
            raise ValueError(f"Unknown readiness dimension: {name}")
        return self._loads(getattr(self, name))

    def set_dimension(self, name: str, payload: Dict[str, Any]) -> None:
        if name not in self.DIMENSIONS:
            raise ValueError(f"Unknown readiness dimension: {name}")
        setattr(self, name, self._dumps(payload))

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "venture_readiness_status": self.venture_readiness_status,
            "risk_level": self.risk_level,
            "evidence_confidence": self.evidence_confidence,
            "next_step_eligibility": self.next_step_eligibility,
            "external_readiness_status": self.external_readiness_status,
            "survival_risk_indicator": self.survival_risk_indicator,
            "founder_venture_fit_status": self.founder_venture_fit_status,
            "route_confidence": self.route_confidence,
            "founder_type": self.founder_type,
            "routing_state": self.routing_state,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "dimensions": {},
        }
        for dimension in self.DIMENSIONS:
            data["dimensions"][dimension] = self.get_dimension(dimension)
        return data


class PhaseGate(db.Model):
    """Tracks whether the user may proceed through a phase or action route."""

    __tablename__ = "phase_gate"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    phase_id = db.Column(db.String(80), nullable=False, default="self_discovery")
    gate_status = db.Column(db.String(40), nullable=False, default="open")  # open, warning, soft_blocked, hard_blocked, hard_stop
    blocking_dimension = db.Column(db.String(120), nullable=True)
    blocking_reason = db.Column(db.Text, nullable=True)
    unlock_condition = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("phase_gates", lazy=True, cascade="all, delete-orphan"))
    venture = db.relationship("Venture", backref=db.backref("phase_gates", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "phase_id": self.phase_id,
            "gate_status": self.gate_status,
            "blocking_dimension": self.blocking_dimension,
            "blocking_reason": self.blocking_reason,
            "unlock_condition": self.unlock_condition,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class UserAction(db.Model, JsonTextMixin):
    """Trusted action lifecycle record.

    External integrations should plug into this table later. The MVP can start with
    mock/manual execution while preserving approval and audit discipline.
    """

    __tablename__ = "user_action"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    venture_id = db.Column(db.Integer, db.ForeignKey("venture.id"), nullable=True, index=True)
    action_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="proposed")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    proposed_content = db.Column(db.Text, nullable=False, default="{}")
    approved_content = db.Column(db.Text, nullable=True)
    approval_required = db.Column(db.Boolean, default=True, nullable=False)
    external_platform = db.Column(db.String(80), nullable=True)
    external_account_id = db.Column(db.Integer, db.ForeignKey("external_connection.id"), nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)
    audit_log = db.Column(db.Text, nullable=False, default="[]")
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    proposed_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("actions", lazy=True, cascade="all, delete-orphan"))
    venture = db.relationship("Venture", backref=db.backref("actions", lazy=True, cascade="all, delete-orphan"))

    def get_proposed_content(self) -> Dict[str, Any]:
        return self._loads(self.proposed_content)

    def set_proposed_content(self, value: Dict[str, Any]) -> None:
        self.proposed_content = self._dumps(value)

    def get_approved_content(self) -> Dict[str, Any]:
        return self._loads(self.approved_content)

    def set_approved_content(self, value: Dict[str, Any]) -> None:
        self.approved_content = self._dumps(value)

    def get_audit_log(self) -> list:
        return self._loads(self.audit_log, fallback=[])

    def append_audit(self, event: str, actor_user_id: Optional[int] = None, payload: Optional[Dict[str, Any]] = None) -> None:
        audit = self.get_audit_log()
        audit.append({
            "event": event,
            "actor_user_id": actor_user_id,
            "payload": payload or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.audit_log = self._dumps(audit)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "venture_id": self.venture_id,
            "action_type": self.action_type,
            "status": self.status,
            "title": self.title,
            "description": self.description,
            "proposed_content": self.get_proposed_content(),
            "approved_content": self.get_approved_content(),
            "approval_required": self.approval_required,
            "external_platform": self.external_platform,
            "external_account_id": self.external_account_id,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "audit_log": self.get_audit_log(),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "proposed_at": self.proposed_at.isoformat() if self.proposed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ExternalConnection(db.Model):
    """Placeholder-ready model for OAuth/API connections.

    Tokens must be encrypted before production use. This pass stores the structural
    fields and permission state so integrations can plug in later.
    """

    __tablename__ = "external_connection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    platform = db.Column(db.String(80), nullable=False)
    connection_status = db.Column(db.String(40), nullable=False, default="stub")  # stub, connected, revoked, expired, failed
    encrypted_access_token = db.Column(db.Text, nullable=True)
    encrypted_refresh_token = db.Column(db.Text, nullable=True)
    scope = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    permission_level = db.Column(db.Integer, nullable=False, default=1)
    connected_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("external_connections", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform,
            "connection_status": self.connection_status,
            "scope": self.scope,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "permission_level": self.permission_level,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DataConsentLog(db.Model):
    """Consent tracking for sensitive readiness and external-action processing."""

    __tablename__ = "data_consent_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    data_category = db.Column(db.String(120), nullable=False)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)
    consent_text_version = db.Column(db.String(80), nullable=False, default="mvp-v1")
    legal_basis = db.Column(db.String(80), nullable=False, default="explicit_consent")
    consented_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("consent_logs", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "data_category": self.data_category,
            "consent_given": self.consent_given,
            "consent_text_version": self.consent_text_version,
            "legal_basis": self.legal_basis,
            "consented_at": self.consented_at.isoformat() if self.consented_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
