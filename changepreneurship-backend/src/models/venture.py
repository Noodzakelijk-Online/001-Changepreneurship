"""
Venture model — Sprint 7 (S7-03)

CEO: "Separate the user from the business idea."
A user may have multiple ideas over time. The platform must not treat
'Robert' and 'Robert's current idea' as the same object.

This prevents future problems when the user:
  - changes idea
  - archives an idea
  - starts a second venture in parallel

Venture links to:
  - VentureRecord (Phase 2 output — the clarified idea)
  - Assessment responses (scoped to this venture where relevant)
  - UserAction records (actions taken for this venture)
  - EvidenceItem records (market evidence for this venture)

Venture types (aligned with VentureRecord):
  FORPROFIT / NONPROFIT / SOCIAL / LOCAL / DEEPTECH / HYBRID

Venture stages (simplified, CEO Section 3.3):
  IDEA        — just an idea, pre-assessment
  CLARIFYING  — going through Phase 1-2
  VALIDATING  — Phase 3 market research
  BUILDING    — Phase 4-5
  OPERATING   — Phase 6-7
  PAUSED      — temporarily inactive
  ARCHIVED    — abandoned
  COMPLETED   — graduated / handed off
"""
from datetime import datetime

from src.models.assessment import db


# Stage constants
STAGE_IDEA       = 'IDEA'
STAGE_CLARIFYING = 'CLARIFYING'
STAGE_VALIDATING = 'VALIDATING'
STAGE_BUILDING   = 'BUILDING'
STAGE_OPERATING  = 'OPERATING'
STAGE_PAUSED     = 'PAUSED'
STAGE_ARCHIVED   = 'ARCHIVED'
STAGE_COMPLETED  = 'COMPLETED'

ALL_STAGES = {
    STAGE_IDEA, STAGE_CLARIFYING, STAGE_VALIDATING,
    STAGE_BUILDING, STAGE_OPERATING, STAGE_PAUSED,
    STAGE_ARCHIVED, STAGE_COMPLETED,
}

# Type constants (mirrors VentureRecord.venture_type)
TYPE_FORPROFIT = 'FORPROFIT'
TYPE_NONPROFIT = 'NONPROFIT'
TYPE_SOCIAL    = 'SOCIAL'
TYPE_LOCAL     = 'LOCAL'
TYPE_DEEPTECH  = 'DEEPTECH'
TYPE_HYBRID    = 'HYBRID'

# Status
STATUS_ACTIVE   = 'ACTIVE'
STATUS_PAUSED   = 'PAUSED'
STATUS_ARCHIVED = 'ARCHIVED'
STATUS_COMPLETED = 'COMPLETED'


class Venture(db.Model):
    """
    Top-level business entity. Separate from User.
    One user may have many ventures over time; only one should be ACTIVE at once
    (enforced in service layer, not DB constraint — allows parallel ventures later).
    """
    __tablename__ = 'venture'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    # Identity
    venture_name = db.Column(db.String(200), nullable=True)  # may be unnamed at start
    venture_description = db.Column(db.Text, nullable=True)   # rough initial description

    # Classification
    venture_type  = db.Column(db.String(20), nullable=True)   # TYPE_* constant
    venture_stage = db.Column(db.String(20), nullable=False, default=STAGE_IDEA)

    # Lifecycle
    status = db.Column(db.String(20), nullable=False, default=STATUS_ACTIVE)

    # Link to the detailed VentureRecord (Phase 2 output, created later)
    venture_record_id = db.Column(
        db.Integer,
        db.ForeignKey('venture_record.id', ondelete='SET NULL'),
        nullable=True,
    )

    # Metadata
    is_primary = db.Column(db.Boolean, nullable=False, default=True)  # user's main active venture
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    venture_record = db.relationship('VentureRecord', foreign_keys=[venture_record_id], lazy='select')

    def archive(self, reason: str = None):
        self.status = STATUS_ARCHIVED
        self.archived_at = datetime.utcnow()
        if reason:
            self.notes = (self.notes or '') + f'\n[Archived: {reason}]'

    def complete(self):
        self.status = STATUS_COMPLETED
        self.completed_at = datetime.utcnow()

    def advance_stage(self, new_stage: str):
        """Advance venture stage — service layer enforces valid transitions."""
        if new_stage in ALL_STAGES:
            self.venture_stage = new_stage
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            'id':                self.id,
            'user_id':           self.user_id,
            'venture_name':      self.venture_name,
            'venture_description': self.venture_description,
            'venture_type':      self.venture_type,
            'venture_stage':     self.venture_stage,
            'status':            self.status,
            'is_primary':        self.is_primary,
            'venture_record_id': self.venture_record_id,
            'created_at':        self.created_at.isoformat() if self.created_at else None,
            'updated_at':        self.updated_at.isoformat() if self.updated_at else None,
        }
